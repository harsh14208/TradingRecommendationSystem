# Signal.Trade — Research Learnings & Alpha Inventory

> Living document. Updated as each research section completes.
>
> **North star:** Every research thread in this document serves one final objective —
> generating a tradable, risk-controlled edge that can be auto-executed through a broker.
> A signal is not "done" when it improves backtest Sharpe; it is done when it survives
> paper trading, calibration, decay monitoring, and operational risk controls enough to
> be trusted with live capital. See [RUNBOOK.md](RUNBOOK.md) §7 for the live-graduation criteria.
> Last updated: 2026-06-12 after §107 GDELT bounded pilot validation. Key new findings: (1) **§107 GDELT news tone adds no deployable edge** — per-trade tilt fired on 0/217 trades; cross-sectional ΔSharpe -0.003 inside placebo noise. (2) **The live-vs-IS gap was mostly DELIVERY LEAKS, not signal** — clean book = 57.8% net WR, +2.06%/trade net. (3) Strategy is structurally a **VIX 20–30 stress-regime play** — 100% of 23yr backtest trades in that window; calm sleeve abandoned (0 trades). (4) Factor attribution confirms **genuine idiosyncratic alpha** (+0.87%/day, p=0.044). (5) WATCH bench all rejected — 111-name curated list is already well-filtered. (6) §87 L10 conviction sizing verified +0.06 Sharpe at ΔN=0, deployed live. (7) v10.9 canon **fails deflated Sharpe at honest 744 trials** — IS iteration is statistically spent. (8) **§96: 61% of alpha from overnight gaps** — validates close-slot timing. (9) **§97: limit-order entries fail deploy bar** across all k values — adverse selection dominates. (10) **§101: TSMOM sleeve Sharpe 0.57** on vanilla config — genuine diversifying premia, but 2015-22 fold 0.277 just misses 0.30 bar; correlation +0.27 vs MR book.
> Primary research script: `backend/scripts/signal_alpha_decomposition.py`
> Primary backtest: `backend/scripts/backtest_technicals.py`
> Live engine: `backend/services/signal_engine.py`

---

## LXX. Confidence Ontology Split (2026-06-27)

The single most important fix to the live engine's quant hygiene was splitting
the overloaded `confidence` field into separate objects:

- **Problem:** `confidence` had become five different concepts in one number:
  raw model score, calibrated win probability, risk adjustment, peer
  confirmation, and scan-relative ranking.  Post-scan steps in
  `signal_engine.py` were mutating the value after calibration, breaking the
  promise that stored confidence was a calibrated probability.
- **Fix:** introduce `alphaScore`, `rawConfidence`, `calibratedProbability`,
  `displayConfidence`, `positionSizeScale`, and `rankScore`/`rankPercentile`.
  Calibration produces `calibratedProbability`; only `displayConfidence` and
  sizing/rank fields may be adjusted afterwards.
- **Static ticker blocklists are dangerous.** The defensive BUY blocklist
  (`KO`, `PEP`, `ABBV`, `MRK`, `LLY`, `NKE`, `V`, etc.) mixed live-validated
  and backtest-derived exclusions.  Backtest-derived ticker bans encode
  look-ahead selection bias and temporary regimes.  Stage B replaces the
  blocklist with `TickerPerformanceGate`, which uses decay-weighted forward
  performance, minimum sample guards, and auto-retirement.  The transition is
  being run as a 30-day controlled experiment: every signal records both the
  static and dynamic decisions, and `scripts/analyze_ticker_perf_shadow.py`
  computes overlap, forward WR, missed winners, saved losers, volume impact,
  and sector skew before promotion.
- **Rule for future gates:**
  - Probability changes only when evidence changes expected win rate.
  - Sizing changes when risk, liquidity, correlation, concentration, or portfolio context changes.
  - Ranking changes only display/order, not probability.

**Implemented in:** `services/engines/assembler.py`, `services/signal_engine.py`,
`services/gates/warning.py`, `models.py`, plus
`tests/test_confidence_invariants.py`.

## The Core Hypothesis (validated)

Large-cap stocks that become oversold via a specific set of conditions (RSI<42, BB%B<0.22, IBS<0.15, VWAP%<−0.75%) exhibit a statistically reliable mean-reversion bounce over 5-10 days.

**Evidence base:**
- 20-year backtest (2006-2026) spanning GFC 2008, COVID crash 2020, 2022 rate-hike bear
- Best config to date (§17f): **N=27, WR=96.3%, Sharpe=1.80, Ann. Sharpe=2.10**, MaxDD=−0.08%
- §15f base (production target): N=66, WR=78.8%, Sharpe=0.70, Ann. Sharpe=1.27, MaxDD=−0.28%
- Jensen's Alpha: +0.90%/trade (beta-adjusted, t=8.21, p<0.001) from live data
- R²=0.010 vs SPY — only 1% of signal variance explained by market

**Why the edge exists:** Forced institutional selling, ETF rebalancing, and stop-cascade dynamics push quality names temporarily below fair value. The bounce is microstructure correcting — not a pattern fit. The alpha is market-correlated (β≈1.15): the bounce happens *because* the broad market stabilizes, not independently of it. Attempting to hedge away the beta removes the alpha (§23d: Sharpe 0.35→0.20).

---

## Alpha Inventory — All Sources Identified

### A1. MR Condition Gate (entry filter, not a scoring signal)

The mean-reversion gate (RSI<42, BB%B<0.22, IBS<0.15, VWAP%<−0.75%) is the most important structural element. It acts as a hard entry filter — without it, BUY signals have near-zero edge (Sharpe 0.04 at MR-gate off).

**Updated 2026-06-09: MR-count=2.** Backtest on 100-ticker/23yr universe with full gate stack (§59–§82) showed:
- MR-count=1 (OR logic): 155 trades, Sharpe 0.20
- **MR-count=2 (≥2 conditions): 154 trades, Sharpe 0.21** (+0.01, −1 trade)

Requiring 2+ conditions filters weak single-condition setups (especially IBS-only) without materially reducing trade count. The mild improvement (0.20→0.21) justifies the change because it costs effectively nothing in trade frequency.

**IBS<0.15 dominates** (11.1% of raw BUY signals pass via IBS alone vs RSI<42 at only 1.7%). IBS-alone entries are genuine but are the weakest class — they disproportionately hit stops. Requiring a second condition (RSI<42, BB%B<0.22, or VWAP%<−0.75%) alongside IBS removes the worst performers while keeping most valid setups.

**RSI gate depth is irrelevant.** RSI<35 vs RSI<42 produces identical results because IBS dominates the OR logic. RSI threshold is a dead parameter.

**Implemented in:** `services/engines/assembler.py` `_has_mr`, `delivery_gates.py` hard block, `backtest_technicals.py` `--mr-count` flag.

---

### A2. MR Weight = 0.1 (multi-family conviction filter)

Setting the MR scoring family weight to 0.1 (from 1.0) is a quality filter, not a signal weight. At full weight, the MR family inflates scores for oversold stocks regardless of whether other independent families (TREND, VOL, MA, HYG) agree. At 0.1, only entries where multiple families confirm the setup clear BUY_THRESH.

**Effect:** N 302→166, Sharpe 0.18→0.32, Ann 0.70→0.92 (74-ticker universe, §10d).
**Insight:** The MR score family is structurally redundant as a scorer — gate 9 already handles MR filtering. The weight reduction uses it only as a tie-breaker in edge cases. This is the most counterintuitive finding in the research: reducing the weight of the signal that defines the strategy improves the strategy.

**Implemented in:** `signal_alpha_decomposition.py` MR_W=0.1, `signal_engine.py` scoring weights.

---

### A3. ATR%rank ≥ 20 (panic-regime filter)

Requiring that the stock's current ATR is above the 20th percentile of its own 252-day ATR history. Removes dormant-volatility entries where the oversold condition is low-energy drift, not a genuine panic.

**Effect:** N 166→137, WR +3.4pp, avg return +0.30pp, Sharpe +0.06, Ann 0.92→1.00, MaxDD −35%. First configuration to achieve Ann. Sharpe = 1.00.

**Why 20th percentile:** ATR≥10 and ATR≥15 add low-quality dormant-zone trades. ATR≥20 is the natural discontinuity — below it, MR=0.1 scoring rarely clears BUY_THRESH anyway (the gate formalises an existing structural boundary). ATR≥30+ over-filters valid bounces and collapses N faster than Sharpe grows.

**Sector exception:** Financials benefit from ATR≥30 (Sharpe 0.56→0.60, Ann 0.62→0.66 in isolation). Financial names with ATR rank 20-29 are in quiet drift, not credit/rate stress. ATR≥30 in Financials = genuine liquidity event.

**Implemented in:** `signal_engine.py` per-sector ATR gate (`_SECTOR_MR_CONFIG["atr_rank_min"]`).

---

### A4. Universe Curation — Sector Quality Matters More Than Parameters

**The single biggest finding in the entire research arc (§15a).**

Removing 26 weak-sector tickers (Semis, Software/IT, Telecom, Other) from the 68-ticker universe improved Sharpe by +0.15 — more than the ATR gate (+0.06), VIX gate (+0.04), and score threshold (+0.06) combined.

**Sector quality ranking (isolated backtests):**
| Sector | Sharpe | Why |
|---|---|---|
| Consumer Disc. (HD/COST/SBUX/TGT/LULU…) | **0.68** | Brand-equity names sold off on bad weeks recover sharply. Highest-quality MR sector |
| Financials (JPM/GS/BAC/BLK/SCHW…) | **0.56–0.60** | Stress-driven dislocations in well-capitalized banks recover reliably |
| Tech/FAANG (NVDA/MSFT/AAPL/GOOGL/META…) | **0.49** | Deep liquidity + institutional ownership = clean snap-backs |
| Semis (INTC/AMD/QCOM/TXN/MRVL) | 0.21 | Chip cycles are multi-quarter, not 5-10 day MR events |
| Software/IT (CSCO/ORCL/CTSH/PANW/WDAY) | 0.10 | Drift, not panic-bounce dynamics |
| Other (CVX/EOG/VZ/PEP/UNH) | −0.02 | Commodity cycles, defensives, utilities don't fit the model |

**The underlying insight:** MR alpha requires a specific stock profile — deep liquidity, institutional ownership, momentum-driven price action, recovery tied to macro stabilization. Healthcare FDA events, chip super-cycles, and utility rate sensitivity are all orthogonal to this mechanism. Wrong tickers create low-quality entries that are hard to filter at the parameter level because they look right technically but are economically wrong.

**Implemented in:** `_DECOMP_EXPANSION` ticker list, `_DEFENSIVE_BUY_BLOCK` for confirmed bad tickers. §16 completed: Energy confirmed positive (Ann=0.44 with VIX≥15+thresh=40+hold=5d), Telecom/Comm admitted, Healthcare/Industrials/Real Estate blocked.

---

### A5. Per-Sector VIX Floor (fear premium gate)

MR bounces require a "fear premium" — the forced selling that creates a genuine dislocation. In low-VIX environments (VIX < 13), oversold stocks are drifting structurally, not panicking temporarily.

**Per-sector optimal floors (§15c):**
- Tech/FAANG: VIX ≥ 13 (+0.11 isolated Sharpe)
- Consumer Disc/Staples/Comm: VIX ≥ 13 (+0.14 isolated Sharpe — largest sector benefit)
- Financials: VIX ≥ 15 (+0.06 isolated Sharpe — stricter because financial stress requires more macro fear to be genuine)

**Why Financials is stricter:** JPM/BAC "oversold" with VIX=13 is a bad week in a calm market. JPM/BAC "oversold" with VIX=15 is a real credit event or rate shock. The distinction matters because financial sector mean-reversion requires macro stress as the catalyst.

**At the global level (§12b):** VIX≥15 improves per-trade Sharpe but collapses N enough that Ann. Sharpe drops. Per-sector application preserves N where the floor isn't justified. Global VIX floor is the wrong tool; sector-specific is the right one.

**Implemented in:** `signal_engine.py` VIX floor gate (`_SECTOR_MR_CONFIG["vix_min"]`), per-sector rationale surfaced to UI.

---

### A6. Per-Sector Score Threshold (conviction filter)

Each strong sector has a distinct minimum composite score for MR BUY entries (§15d):

| Sector ETF | Threshold | Key Finding |
|---|---|---|
| XLF (Financials) | **42** | At thresh=42: WR=83.3%, Sharpe=0.89 isolated — best sector-param combo found in 20 years |
| XLK (Tech/FAANG) | **40** | Quality boundary confirmed twice (§14b + §15d). Lowering to 38 hurt aggregate Ann 0.92→0.74 |
| XLY/XLP/XLC (Consumer) | **38** | Slight relaxation valid — consumer names generate reliable bounces at modest conviction |
| Global baseline | 35 | Floor for all non-calibrated sectors |

**The Financials insight:** A Financials MR entry scoring ≥ 42 means MA, TREND, VOL, HYG, and ATR all independently signaled simultaneously alongside the MR gate condition. That level of multi-family confluence in a financial name = genuine crisis-level dislocation, not noise. 83.3% WR at N=24 is statistically meaningful and operationally significant.

**The Tech insight:** FAANG names have strong institutional coverage and momentum tendencies. They look technically oversold frequently (growth stocks have high volatility). Score ≥ 40 filters for the genuine setups where enough independent families confirm the oversold condition isn't just a momentum pullback in disguise.

**Implemented in:** `signal_engine.py` sector score gate (`_SECTOR_MR_CONFIG["buy_thresh"]`).

---

### A7. Per-Sector Hold Period (return-speed calibration)

Each sector has a fundamentally different recovery speed (§15b):

| Sector | Optimal Hold | Recovery mechanism |
|---|---|---|
| Tech/FAANG | **5 days** | Mega-cap liquidity + momentum reversal is fast. Overstaying past day 5 introduces sector-rotation risk |
| Financials | **7 days** | Rate-shock/credit-stress recovery aligns with Fed announcement and weekly macro cycles |
| Consumer | **10 days** | Discretionary spending sentiment recovery is gradual — needs the full window |

**The universal 10-day hold was leaving money on the table in Tech** (overstaying) and cutting Financials trades at the right time by accident. Sector hold optimization is a structural parameter fix, not overfitting.

**Implemented in:** `signal_engine.py` `recommendedHoldDays` in signal dict, `_SECTOR_MR_CONFIG["hold_days"]`.

---

### A8. Signal Family Architecture (essential vs redundant)

**Essential families (OHLCV, removing any drops Sharpe):**
| Family | ΔSharpe if removed | What it captures |
|---|---|---|
| MA (SMA/VWAP/Z-score) | −0.13 to −0.15 | Structural deviation from mean — most critical |
| TREND (MACD/EMA/ADX) | −0.07 to −0.09 | Trend exhaustion context; prevents buying accelerating downtrends |
| VOL (OBV/surge/dry-up) | −0.05 to −0.06 | Volume capitulation = forced selling exhausted |
| HYG (credit stress ETF) | −0.01 to −0.03 | Near-orthogonal (corr≈0.07 avg) macro signal — only genuine non-price alpha |
| CMF (Chaikin MF) | −0.01 to −0.02 | Money flow confirmation |

**Key signal engine adjustments confirmed by decomp (v3/v4 research):**
- KC lower breach + RSI<42: score +8 (was score −8). Keltner-channel oversold with RSI confirmation = high-probability MR setup, not breakdown
- SMA20 streak ≤ −7 days: score +7 (was momentum −8). Extended weakness = peak MR probability, not continuing trend
- Donchian 20d low + RSI<45: score +8 (was momentum −10). 20-day oversold extension is a MR setup signal
- ATR rank < 10th pct: score +6 (new). Extreme vol coiling = pre-bounce compression
- LH/LL + RSI<45: score +7 (was momentum −7). Downtrend extended → approaching oversold reversal

**Confirmed redundant (16 families, all removed):**
MFI, WK52, RSI_DIV, STREAK, PIVOT, SUPER, HURST, GAP, RSI_LEVEL, EARN-score, REDDAY, MOM_DECEL, BB_PURE, IBS_PURE, VWAP_DIST, DONCHIAN-score, PRICESTR-score, RS_QUALITY, SECTOR_RS

> **§45 note (2026-05-29):** OSC was classified redundant in §40 (24-ticker v10 subset). This finding does NOT hold for the 105-ticker BASE_WEIGHTS universe. §45 OSC sweep: OSC×1.0 = Sharpe 0.00 (only breakeven); OSC×0.3 = Sharpe −0.24. OSC weight restored to 1.0 in live engine and decomp script. OSC remains load-bearing for the full production universe.

**The exhaustion finding:** The OHLCV signal space is fully explored. All 27 tested families cover the entire price/volume surface. No new pure technical signal will materially improve beyond current architecture. Future per-trade Sharpe gains (above the ~0.50 ceiling) require alternative data: options flow, short interest velocity, or earnings revision momentum.

---

### A9. Adaptive Exit (backtest v6.1)

When a trade is profitable after ≥2 days AND RSI>55 OR MACD crosses positive OR price recaptures VWAP, exit early rather than waiting for the full hold period.

**Effect in backtest:** 16.3% of all trades now exit as adaptive exits, 100% WR at +2.98% avg. Replaces the weakest time-exits. Stop rate dropped from 31.8% (live engine) to 20.0%.

**Why it works:** MR bounces often overshoot the entry signal and recover quickly. If RSI has normalized back to 55+, the thesis has played out — holding further is just chasing continuation, which is a different trade the system isn't designed for.

**Implemented in:** `backtest_technicals.py` adaptive exit logic. Live engine surfacing via `recommendedHoldDays`.

---

### A10. Regime-Aware Gating

**Broad market breadth gate:** >70% of S&P 500 above 200-DMA → require score ≥ 42. When the technical tide is universally elevated, Supertrend/momentum/price-structure all default positive, adding ~+15 pts to any score. A 35-41 score in that environment is the tide, not alpha.

**SPY trend filter:** Confirmed bear trend blocks BUY signals below score thresholds. MR bounces in confirmed downtrends fail significantly more often ("catching a falling knife" regime).

**Deep bear guard:** In deep bear markets, RSI must be ≥ 35 (not the usual < 42 entry) for MR entry — prevents buying structurally deteriorating sectors.

**Day-of-week alpha (live data, §11a):**
- Best: Wednesday (+4.11% avg, 4.69× PF)
- Worst: Friday (51.8% WR, +1.71%) — pre-weekend position unwinding
- Gate implemented: score ≥ 65 required on Thursdays (fills Friday open, weekend gap risk)

---

### A11. Macro Orthogonal Signals (non-price alpha)

**HYG (iShares High Yield Corporate Bond ETF):** When HYG is declining (credit spreads widening), MR setups have a legitimate macro catalyst and bounce harder. HYG has correlation ≈ 0.07 with all price-based families — genuinely orthogonal information. The only non-price signal confirmed as net-positive.

**STLFSI4 (St. Louis Fed Financial Stress Index):** Elevated financial stress increases confidence that the oversold reading is macro-driven, not idiosyncratic. Implemented in macro context score layer.

**VIX:** Used both as a hard gate (per-sector floors) and as a rationale confidence modifier (VIX>30 → additional confidence haircut unless confidence ≥ 75).

---

## Key Negative Findings (What Doesn't Work)

These are as important as what works — they prevent future research from repeating dead ends:

| Finding | What was tested | Why it fails |
|---|---|---|
| **Beta-hedge kills alpha** | Long stock + short SPY×β | Alpha IS the market-correlated bounce. Removing beta removes the recovery mechanism. Sharpe 0.35→0.20 |
| **VIX global floor collapses N** | VIX≥15 globally | N drops faster than Sharpe improves. Per-sector application is the correct tool |
| **MR confluence requirement hurts** | Require 2+ MR conditions simultaneously | IBS-alone entries are valid and orthogonal. Requiring confluence removes good trades |
| **Consecutive score filter** | Require prev bar also ≥ threshold | Same per-trade quality, 60% N reduction. N-destructive without quality benefit |
| **Score-weighted sizing** | Bet proportional to signal score (40-65) | Within MR=0.1 filtered universe, score 40-65 does not predict relative trade quality. Equal-weight optimal |
| **Tech BUY_THRESH=38** | Lower threshold to unlock more Tech trades | Adds noise. Ann 0.92→0.74. Tech has a quality boundary at 40 |
| **Tighter stops (1.0×ATR)** | Reduce stop from 1.5×ATR to 1.0×ATR | Triggers before MR bounce completes, consistently. 1.5×ATR is well-calibrated |
| **Hold=5d universally** | Apply 5-day hold to all sectors | Better per-trade Sharpe but annualized same/worse at 74 tickers. Sector-specific hold is the right approach |
| **RSI gate depth** | RSI<35 vs RSI<42 | Zero effect. IBS<0.15 dominates the OR logic at 11.1% of raw signals vs RSI at 1.7% |
| **Universe expansion without curation** | 74-ticker vs 30-ticker | New tickers diluted per-trade Sharpe (0.24→0.18). OSC edge is universe-specific — doesn't generalize to Healthcare FDA events, chip cycles, utility rate sensitivity |
| **Momentum dual-gate** | MOM: RSI 50-68 for continuation entries | Short-term reversal effect (Jegadeesh 1990): momentum edge is at 1-12 month horizons; at 5-10 days it reverses. Confirmed empirically v11a/v11b |
| **Wider targets (2.5×/3.0×ATR)** | Extend target to let winners run | Marginal improvement at best (+0.02 Sharpe at 2.5× in 30-ticker universe, worse at 74-ticker) |
| **All OHLCV-only new signals** | 16 additional families tested v1-v8 | Signal space exhausted. Corr 0.14 avg off-diagonal = good orthogonality, but no new family adds net edge |
| **Calm-regime sleeve (§88)** | Lower thresholds + 0.5× sizing when VIX<20 | **0 trades in 23 years.** MR triggers (RSI<42, BB%B<0.22, IBS<0.15, VWAP%<−0.75) naturally only fire in fear-driven capitulation. Structural mismatch, not a parameter problem |
| **WATCH bench expansion (§90)** | PANW, BWA, FTI, EQH, TRGP, APTV, DHI, FIVE, ITW | **0 trades across all 9.** 111-name curated list is already well-filtered; no easy N expansion via bench screening |

---

## The Quality-Quantity Pareto Frontier

The most important structural constraint in this strategy:

```
Higher per-trade Sharpe ────────────────────── Lower per-trade Sharpe
     0.50                0.41    0.38    0.32               0.18
  VIX+ATR+consec        ATR≥50  ATR≥20  MR=0.1            Baseline
    N=20                 N=102   N=137   N=166              N=302
    Ann=0.50             Ann=0.92 Ann=1.00 Ann=0.92        Ann=0.70
   (stat unreliable)               ↑
                             SWEET SPOT
```

Every gate that improves per-trade Sharpe reduces N. The annualized formula (`per_trade_Sharpe × √(N/20)`) means the optimal point is NOT maximum per-trade Sharpe — it's the point where the Sharpe improvement outpaces the √N decay. At 74 tickers, that point is ATR≥20 (Ann=1.00). With 150+ tickers, more gates become viable.

**With sector-optimized filters (§15f):** N=66, per-trade Sharpe=0.70, Ann=1.27. The per-sector filters achieved a non-obvious result: they simultaneously improved per-trade Sharpe AND preserved enough N that annualized kept growing. This is because each sector filter is orthogonal — removing a bad Tech trade doesn't remove a good Financials trade.

---

## Research Progression — Full Timeline

| Version | Universe | Key change | N | Per-trade Sh | Ann. Sh |
|---|---|---|---|---|---|
| v2 (original best) | 30 tickers | MR×0.5 + OSC×1.0, 11 families | 77 | 0.43 | 0.84 |
| v11c | 30 tickers | Gap+streak MR triggers | 144 | 0.24 | 0.64 |
| v12 (74 tickers) | 74 tickers | Universe expansion | 302 | 0.18 | 0.70 |
| v12 MR=0.1 | 74 tickers | MR weight as quality filter | 166 | 0.32 | 0.92 |
| v12 + ATR≥20 | 74 tickers | ATR rank entry gate | 137 | 0.38 | 1.00 |
| §13b 68-ticker | 68 tickers | Remove weak sectors | 127 | 0.36 | 0.92 |
| §15a 42-ticker | 42 tickers | Strong-only universe | 80 | 0.52 | 1.03 |
| §15f sector-opt | 42 tickers | Per-sector VIX/hold/thresh/ATR | 66 | 0.70 | 1.27 |
| §16 full-universe | 157 trades | All sectors sector-optimized | 157 | 0.40 | **1.12** |
| **§17f best** | **42 tickers** | **§15f + ATR≤70 + jump<-6%** | **27** | **1.80** | **2.10** |
| §87–§94 canon | 100 tickers | L10 sizing + per-sector hold + MR-count=2 | 217 | 0.24 | 0.34 |

---

## Remaining Structural Ceilings

**Per-trade Sharpe ceiling: ~0.50** with OHLCV signals.

Avg net return (best config): +1.63–2.45%. Implied std dev: ~3.5–4.3%.
At N=20 ultra-filtered: Sharpe=0.50, avg=+2.03%. Still 2× short of per-trade Sharpe=1.0.

Root cause: 3-5% std dev is irreducible event-driven variance (earnings gaps, macro shocks post-entry) that no technical signal can anticipate. The MR alpha (+1-2.5% avg) is 25-70% of the noise floor. No OHLCV filter combination changes this ratio.

**To break through the ceiling:**
1. **Alternative data** — options flow (large call buying in oversold = institutional accumulation), short interest velocity, earnings revision momentum. Could identify 3-4% avg return setups vs current 1.6-2.5%.
2. **Expanded curated universe (150+ tickers)** — if per-trade Sharpe holds at 0.38-0.70, Ann. Sharpe scales with √N. At 150 tickers with §15f filters: estimated Ann. Sharpe 1.5-1.8. **§90 WATCH bench rejected all 9 candidates — expansion is not a free lever.**
3. **Options strategies** — long ATM calls on oversold setups. 3% stock bounce → 30-50% call return. Requires IV surface modeling.

**Regime reality (§93d, 2026-06-10):**
The strategy is structurally a **VIX 20–30 stress-regime play** — 100% of 23-year backtest trades in that window. Post-GFC Bull (108 trades, Sh=0.45) and Late-cycle/COVID (92 trades, Sh=0.33) were strong. Rate-hike cycle (2022+, 38 trades, Sh=−0.10) is negative. The live period overlaps the negative regime — this is the primary driver of the 25.5pp live-vs-IS WR gap, not delivery leakage or fill slippage. Future Sharpe will be regime-dependent; there is no alpha in rate-hike/QE-tightening environments for this setup.

---

## §16 Results (completed 2026-05-25)

Full-universe sector optimization across all 11 GICS sectors. Full data in Stats.md §26.

**Sector ranking (optimal config):**
1. Financials: Ann=0.97, WR=88.2%, N=17 → hold=7d, VIX≥15, thresh=42, ATR≥30
2. Tech/FAANG: Ann=0.63, WR=73.3%, N=30 → hold=5d, VIX≥13, thresh=40, ATR≥20
3. Consumer: Ann=0.52, WR=72.2%, N=18 → hold=10d, VIX≥13, thresh=40, ATR≥20
4. Energy: Ann=0.44, WR=75.0%, N=8 → hold=5d, VIX≥15, thresh=40, ATR≥20 ← **new**
5. Semis: Ann=0.40, WR=54.8%, N=31 (weaker, admitted)
6. Telecom: Ann=0.19, VIX floor removed (hurt)
7. Software/IT, Industrials, Healthcare: near-zero / blocked
8. Real Estate: BLOCK (Sharpe=-15, WR=0%)

**Sector-optimized full universe:** N=157, Ann.Sharpe=1.12 vs baseline 0.83 (+0.29).

**Changes to `_SECTOR_MR_CONFIG`:** Consumer thresh 38→40, XLC VIX floor removed + hold 7d→10d, Energy promoted (vix=15, thresh=40, hold=5d), Materials hold 10d→5d.

## §17 Results (completed 2026-05-25)

Entry quality gate research on §15f base. Full data in Stats.md §27.

**Key finding: ATR ceiling ≤70 is a transformative gate.**
- ATR ≤70 alone: N=29, WR=93.1%, Sharpe=1.58, Ann=1.90 (+0.63 vs baseline)
- §15f + ATR≤70 + jump<-6%: **N=27, WR=96.3%, Sharpe=1.80, Ann=2.10** (+0.83!)
- T+2 delay: HURTS (-0.29 Sharpe). Never implement.
- IBS streak gate: No effect (not a sole trigger in this universe).

**Interpretation:** Valid MR regime is ATR 20th–70th percentile. Below 20 = dormant drift. Above 70 = trending panic (selling accelerating, not exhausted). Both ends are structurally hostile to mean-reversion bounces.

**Both gates live in signal_engine.py** (lines 975-1024). §17 validates their thresholds.

---

## Key Insights for Future Research

1. **Universe composition > parameter tuning.** Wrong tickers cost you more than wrong parameters. Before sweeping hold/VIX/thresh, first confirm the sector has genuine MR edge in isolation.

2. **The fear premium is load-bearing.** Low-VIX MR entries are drift, not panic. The bounce mechanism requires macro fear as the catalyst. Any research that ignores VIX at entry is optimizing a broken setup.

3. **IBS<0.15 is the dominant MR trigger** (11.1% of raw signals). It's orthogonal to RSI/BB and valid on its own. Do not require it to co-occur with RSI — that removes valid trades.

4. **Beta is not the enemy; it's the mechanism.** The MR bounce happens because the market stabilizes and the correlated stock recovers. Attempting to hedge it removes the alpha. This strategy is inherently regime-dependent (requires eventual market stabilization).

5. **Per-sector filters are orthogonal; global filters are N-destructive.** Applying VIX≥15 globally collapses N. Applying it only to Financials (where it's justified) preserves N in Tech and Consumer where the floor is lower. Always prefer per-sector gating over global gating.

6. **The annualized Sharpe formula creates a non-obvious optimum.** Maximizing per-trade Sharpe (minimum N) is wrong. Maximizing Ann = per_trade_Sh × √(N/20) means accepting some per-trade quality reduction in exchange for N. The sweet spot moves right (toward more N) as universe size grows.

7. **Sector recovery speed is structurally determined.** Tech bounces in 5 days because liquidity is deep and momentum reversal is fast. Consumer takes 10 days because spending sentiment is slow. Hold period is a sector property, not a strategy property.

8. **Financials has extraordinary precision at high conviction.** The combination of Financials + score≥42 + VIX≥15 + ATR≥30 is the single highest-quality sector-param combination found: WR=83.3%, Sharpe=0.89. This subset should be prioritized in position sizing when conditions align.

9. **MR signal families are double-counters at scoring.** The MR family (BB+RSI+IBS+VWAP) overlaps structurally with OSC and DONCHIAN (corr 0.70-0.74). Giving MR full weight double-counts the oversold condition. Weight it at 0.1 — just enough to break ties, not enough to dominate.

10. **The OHLCV ceiling is real and reached.** 27 families tested, signal space exhausted, per-trade Sharpe ceiling ≈ 0.50. The next improvement must come from outside price/volume: options flow, short interest, alternative data, or structural changes (options strategies).

11. **Factor attribution confirms genuine idiosyncratic alpha (§89b).** Regressing IS trade returns on FF5 + ST_Rev: Alpha = +0.87%/day (p=0.044), R² = 0.05. HML and CMA are significant but the strategy is 95% idiosyncratic — not replicable via factor ETFs. ST_Rev beta is NOT significant (p=0.530), confirming the edge is not just short-term reversal.

12. **The live-vs-IS gap is primarily regime mismatch (§93d), not delivery leakage.** 25.5pp WR gap (43.6% live vs 69.1% IS). The live period (2022+) overlaps the rate-hike epoch where the backtest itself shows negative Sharpe (−0.10). Hour 11–12 ET shows catastrophic live WR (23.7% vs 47.8% baseline, p=0.000) — likely a midday liquidity/microstructure effect. But the May+ reliable cohort shows reversal at 11–12h (small sample), so the effect may be regime-specific.

13. **The strategy is structurally a VIX 20–30 stress-regime play.** 100% of 23-year backtest trades occurred in VIX 20–30. Zero in calm (<20) or panic (≥30). This is not a general mean-reversion strategy — it is a fear-driven capitulation strategy. Edge is tied to macro stress as the catalyst.

---

## §18 Results (completed 2026-05-25)

S&P 500 screener candidate validation for EXPE, GOOG, LULU, MAR, TPR.
Script: `backend/scripts/validate_s18_candidates.py`.

| Ticker | §15f N | WR | Sharpe | §17f N | Verdict |
|---|---|---|---|---|---|
| GOOG | 5 | 80% | 0.81 | 3 | ✓ **ADD** (already in TICKERS) |
| MAR | 3 | 100% | 2.28 | 2 | ⚠ N too small — monitor |
| EXPE | 1 | 100% | — | 1 | ⚠ N too small — insufficient |
| LULU | 1 | 100% | — | 0 | ⚠ §17f removes all trades — skip |
| TPR | 3 | 67% | 0.47 | 2 | ⚠ below WR/Sharpe threshold |

**Key finding:** Only GOOG passes the N≥5, WR≥55%, Sh≥0.35 quality bar. Other §18 candidates have too few backtest trades to confirm edge — the §15f/§17f filters are extremely selective for these names. Low N is not necessarily a bad sign (it means the filter is working and only high-quality setups fire), but it means we cannot statistically confirm the edge in these names yet. Run the full S&P 500 screener to find additional confirmed candidates.

**GOOG already in TICKERS at `backtest_technicals.py:58`** — no action needed.

---

## §19 Results (completed 2026-05-25, v2 re-run same day)

OOS Walk-Forward Validation. Fixed §15f/§17f params, no re-optimisation per window.
Script: `backend/scripts/run_section19_oos_walkforward.py`.
Two runs: v1=25-ticker (N-starvation), v2=56-ticker (after §30 screener expansion).

**v2 results (56-ticker universe — definitive run):**

| Window | N | WR | Avg% | Sharpe | Ann.Sharpe | Pass? |
|---|---|---|---|---|---|---|
| 2016–2017 | 13 | 69.2% | +0.98% | 0.37 | 0.94 | ✗ |
| 2018–2019 | 20 | 60.0% | +1.41% | 0.37 | 1.18 | ✓ |
| 2020–2021 | 26 | 50.0% | +0.79% | 0.20 | 0.74 | ✗ |
| 2022–2023 | 8 | 62.5% | +1.51% | 0.49 | 0.97 | ✗ |
| 2024–2025 | 9 | 44.4% | +0.22% | 0.05 | 0.11 | ✗ |

**Verdict: 1/5 windows pass. N-starvation is ruled out (N=8–26). §15f/§17f thresholds appear over-tuned to the 2006-2016 training regime.**

**What §19 v2 reveals:**
1. N-starvation was NOT the only issue — 1/5 pass stands with adequate sample sizes
2. 4/5 windows have positive avg return — the directional MR edge exists OOS
3. **2016-17 (Ann=0.94) and 2022-23 (Ann=0.97)** are 0.03–0.06 below the pass threshold — suggests the pass bar configuration is slightly over-specified
4. **2020-2021** is the key failure: N=26 (enough), WR=50%, Sh=0.20 — COVID crash created massive gaps that overshot before MR recovery, breaking the holding-period assumption
5. **2024-2025** is the weakest window: N=9, Ann.Sh=0.11 — low-VIX low-vol bull market generates few qualifying setups and those that fire show no edge
6. **DO NOT add more sector-specific constraints** — the OOS data shows current parameters already over-specify

---

## §20 Results — OOS Relaxed Global Params (completed 2026-05-25)

Tests whether the base MR signal (without §17f gates) generalises OOS.
Script: `backend/scripts/run_section20_oos_relaxed.py`
Config: thresh=35, ATR≥20, no ATR ceiling, no return-jump filter, no VIX floor. 56 tickers.

| Window | N | WR | Avg% | Ann.Sharpe | Pass? |
|---|---|---|---|---|---|
| 2016–2017 | 37 | 78.4% | +2.04% | 2.69 | ✓ |
| 2018–2019 | 35 | 54.3% | +0.67% | 0.74 | ✗ |
| 2020–2021 | 50 | 58.0% | +1.73% | 2.10 | ✓ |
| 2022–2023 | 18 | 44.4% | +0.75% | 0.61 | ✗ |
| 2024–2025 | 37 | 40.5% | +0.01% | 0.01 | ✗ |

**Verdict: 2/5 pass. Base signal also not universally robust OOS.**

**The defining finding — regime-conditional performance:**

| Window | Regime | §19 strict Ann.Sh | §20 relaxed Ann.Sh | Winner |
|---|---|---|---|---|
| 2016–2017 | Low-VIX bull | 0.94 | **2.69** | Relaxed |
| 2018–2019 | Vol spike | **1.18** | 0.74 | Strict |
| 2020–2021 | COVID recovery | 0.74 | **2.10** | Relaxed |
| 2022–2023 | Rate-hike bear | **0.97** | 0.61 | Strict |
| 2024–2025 | Low-VIX AI bull | 0.11 | 0.01 | Neither |

**Key insight: The optimal threshold moves with VIX regime.**
- Strict gates (§17f) outperform in HIGH-VIX sell-offs (VIX ≥ 20). The ATR ceiling and return-jump filter correctly reject gap-and-fade trades.
- Relaxed gates outperform in LOW-VIX bull markets (VIX < 18). More oversold bounces are genuine in calm trending markets.
- **Neither config works in 2024-25.** N=37 (relaxed), Ann.Sh=0.01 — the current AI-driven low-VIX market has structurally degraded the MR snap-back edge. Stocks reaching RSI<42 in this regime are structurally declining, not temporarily dislocated.

**Conclusions from §19+§20:**
1. The MR edge is real but regime-conditional — not a static edge
2. In-sample Ann.Sharpe 1.27–2.10 is an overestimate (regime-cherry-picked training period)
3. Realistic OOS expectation: ~0.7–1.5 in productive VIX regimes (15-25); near-zero in hostile regimes
4. No single static threshold stack passes ≥3/5 OOS windows
5. The right fix is VIX-regime switching, not more parameter complexity

**Recommended §21:** Implement VIX-regime conditional thresholds — high-VIX mode (thresh=38, §17f gates ON) when rolling-20d VIX ≥ 18; low-VIX mode (thresh=35, gates OFF) when VIX < 18. Test OOS. The architecture is already in signal_engine.py via `vix_min_override`; the insight is to condition threshold tightness on VIX level rather than using a fixed stack.

---

## §30 Results — Extended S&P 500 Screener (completed 2026-05-25)

Script: `backend/scripts/screen_sp500_mr_candidates.py --fast`
Config: base discovery (thresh=35, ATR≥20, 2006–2016). Sectors: Tech+Consumer+Financials+Communication.
Quality bar: WR≥55%, Sh≥0.35, N≥3.

**Funnel:** 158 loaded → 103 tested → **31 PASS** / 72 FAIL / 55 SKIP (N<3)

**31 PASS tickers:**
- Communication: PSKY (Paramount Skydance)
- Consumer: AVY, DPZ, EBAY, EXPE, HLT, LULU, MAR, ROST, TPR
- Financial: BLK, BX, C, FITB, KEY, KKR, MA, RF, SCHW
- Tech: CDNS, CPAY, CRM, CTSH, FIS, GEN, LRCX, NTAP, PANW, ROP, TDY, TEL

**Action taken:** All 31 added to `backtest_technicals.py` TICKERS (lines 63–84). Production universe grows from 25 → 56 tickers. `signal_alpha_decomposition.py` deduplication added (line 219) to handle overlap with `_DECOMP_EXPANSION`.

**Projection:** 56 tickers → ~115 trades/yr → Ann.Sharpe ~1.68 (at 0.70/trade per-trade Sharpe). Conservative: 1.44.

**Note:** These are base-discovery PASS tickers (thresh=35, no VIX floor, 2006-2016 period). Some (EXPE, LULU, MAR, TPR) previously failed §15f strict-gate validation (N<5 under high-threshold gates). With 56 tickers, §19 OOS walk-forward should reach N≥20/window, enabling statistically meaningful validation.

**Confirmed FAIL (do not add):** AVGO, FFIV, INTU, DELL, MS, USB (negative alpha or structurally bad for MR), plus 66 others tested and below quality bar.

---

## §31 Results — Russell 1000 Screener (completed 2026-05-31)

Script: `backend/scripts/screen_russell1000_mr_candidates.py --fast`
Config: base discovery (thresh=35, ATR≥20, 2006–2016). Sectors: Tech+Consumer+Financial+Comm+Energy+**Healthcare+Industrials** (research-only).
Quality bar: WR≥50%, Sh≥0.20, N≥3. WATCH: WR≥60%, Avg≥0.5%, N≥5.
Universe: Wikipedia S&P 500 (503) + S&P 400 MidCap (400) = 903 → 455 after sector/cap/beta → 437 after ADV≥$50M.

### Key methodological finding: pre-scoring look-ahead bias

Full 20yr mode (`--fast` removed) produced *fewer* signals per ticker than fast 10yr mode (AMP: N=10→3, GOOGL: N=10→6). Root cause: `_prescore()` normalises scores using the full time-series window. Adding 2017-2026 data (including COVID crash and 2022 bear market) shifts the all-time percentile distribution, retroactively pushing 2006-2016 signal scores below the thresh=35 cutoff. **Always use `--fast` (2006-2016 window) for discovery screening** — the pre-scoring window is consistent with the signal window, no look-ahead contamination.

### PASS tickers (Sharpe ≥ 0.20, N ≥ 3)

All 5 are **Industrials (XLI) — research-only, blocked in live engine by §10**. Added to `backtest_technicals.py` TICKERS as research-only (same as HON/RTX/CAT/DE/LMT).

| Ticker | Name | N | WR | Avg% | Sharpe | ADV | Action |
|---|---|---|---|---|---|---|---|
| CSX | CSX Corp (railway) | 10 | 67% | +1.58% | **0.50** | $866M | ✅ Added (Sh>0.29) |
| UNP | Union Pacific (railway) | 11 | 73% | +1.50% | **0.44** | $1.16B | ✅ Added (Sh>0.29) |
| ETN | Eaton (industrial/elec) | 10 | 70% | +1.49% | **0.43** | $1.0B | ✅ Added (Sh>0.29) |
| XYL | Xylem (water tech) | 10 | 60% | +0.99% | **0.30** | $266M | ✅ Added (Sh>0.29) |
| ITW | Illinois Tool Works | 10 | 73% | +0.59% | 0.28 | $588M | ⛔ Below IS Sh=0.29 |

**Railway stocks (CSX/UNP) are the standout finding.** Sharpe 0.44–0.50 exceeds the IS universe aggregate (0.29). Cyclical demand cycles + institutional liquidity creates textbook MR setup. Also confirmed: AMP (Financial) added earlier from fast-mode (N=10, WR=80%, Sh=0.42) remains valid.

### WATCH tickers — §90 VALIDATED, ALL REJECTED (2026-06-10)

Full 22-year IS backtest on 9 WATCH candidates. **Result: 0 trades across all 9 tickers.**

| Ticker | Sector | Screener N | §15f+§17f IS N | Verdict |
|---|---|---|---|---|
| PANW | Tech | 7 | 0 | ⛔ REJECTED — not in S&P 500 until 2023; too short window |
| BWA | Consumer | 7 | 0 | ⛔ REJECTED — ample history, zero MR signals with current engine |
| FTI | Energy | 6 | 0 | ⛔ REJECTED — ample history, zero MR signals |
| EQH | Financial | 5 | 0 | ⛔ REJECTED — never in S&P 500 |
| TRGP | Energy | 7 | 0 | ⛔ REJECTED — not in S&P 500 until 2022; too short window |
| APTV | Consumer | 8 | 0 | ⛔ REJECTED — ample history, zero MR signals |
| DHI | Consumer | 8 | 0 | ⛔ REJECTED — ample history, zero MR signals |
| FIVE | Consumer | 9 | 0 | ⛔ REJECTED — never in S&P 500 |
| ITW | Industrials | 10 | 0 | ⛔ REJECTED — ample history, zero MR signals |

**Key finding:** The Russell 1000 screener's fast-mode (2006-2016) produced promising WR for these tickers, but the full 22-year IS backtest with the complete gate stack (§59–§82) filters every single one. The screener's pre-scoring normalization window creates a look-ahead-like shift that overstates signal counts. **The 111-name curated list is already well-filtered — no easy N expansion via bench screening.**

**Remaining WATCH (unvalidated, research-only):**
HAL (Energy), MCO (Financial), M (Consumer), AMAT (Tech), plus Industrials/Healthcare research-only list.

### Screener bugs fixed (2026-05-31)

All bugs were present in both `screen_russell1000_mr_candidates.py` and `screen_sp500_mr_candidates.py`:
1. **WR display**: `stats()` returns WR as percent (80.0) but display multiplied by 100 again → 8000%. Fixed: removed `× 100`.
2. **Avg display**: same double-multiplication. Fixed.
3. **MaxDD key**: `stats()` returns `max_dd` but code read `maxdd` → always 0. Fixed.
4. **MIN_WR**: was 0.55 (decimal) but WR stored as percent → filter always passed. Fixed to 55.0.
5. **process_ticker args**: signature expanded to 12 args; screener was passing 5. Fixed.
6. **iShares IWB URL**: returns HTML (bot-protection) not CSV. Fixed: HTML-detect in first 512 bytes → immediate fallback to Wikipedia S&P 500 + S&P 400.

### Universe expansion summary (total additions to date)

| Session | Tickers added | Source | Notes |
|---|---|---|---|
| §30 (2026-05-25) | 31 | S&P 500 screener | All live-eligible |
| §31a (2026-05-31) | AMP | Russell 1000 fast | Financial; Sh=0.42 |
| §31b (2026-05-31) | CSX, UNP, ETN, XYL | Russell 1000 fast | XLI research-only |
| **Total IS universe** | **105** | | 100 individual stocks + 5 from §31 |

### Next validation steps

1. ✅ Run IS backtest with 105-ticker universe — confirmed aggregate Sharpe ≥ 0.29 holds
2. ✅ Validate top WATCH tickers — §90 completed; PANW/APTV/FTI/EQH/TRGP/BWA/DHI/FIVE/ITW all REJECTED (0 trades)
3. ⏳ MCO (N=9, WR=78%) and HAL remain unvalidated — run full 20yr IS
4. ❌ Energy sub-sector (HAL/FTI/TRGP) — FTI/TRGP rejected; HAL still WATCH
5. ⏳ Monitor midday 11–12 ET effect in May+ cohort — need N≥20 reliable signals to confirm persistence
6. ⏳ Meta-model auto-activation — wait for CV-AUC to cross 0.52 (needs ~4–6 more months at current N)

---

## §87 Consecutive-Score Sizing A/B Validation (2026-06-10)

**Question:** Does applying a 1.3× position-size multiplier to persistent-oversold signals (prev_score ≥ threshold) improve risk-adjusted returns vs. flat sizing?

**Method:** Full 23-year IS backtest (111 tickers, 2003–2026) run twice: baseline (flat sizing) and variant (`--consec-score-sizing`). Three perspectives reported:

### §1 Unweighted per-trade metrics (entry/exit selection unchanged)
| Metric | Baseline (flat) | §87 (sizing) | Δ |
|:---|---:|---:|---:|
| Total Trades | 217 | 217 | +0 |
| Win Rate | 69.1% | 69.1% | +0.0pp |
| Avg Return | +0.80% | +0.80% | +0.00pp |
| Sharpe | 0.24 | 0.24 | +0.00 |
| Profit Factor | 1.73× | 1.73× | +0.00 |
| MC P5 / P95 | 0.07 / 0.43 | 0.07 / 0.43 | — |

> Per-trade metrics identical by construction — sizing does not affect entry/exit selection.

### §87 Size-weighted metrics (score-proportional portfolio)
| Metric | Baseline (flat) | §87 (sizing) | Δ |
|:---|---:|---:|---:|
| Boosted trades | — | 50/217 | — |
| Weighted Win Rate | 69.1% | 70.7% | **+1.6pp** |
| Weighted Avg Return | +0.80% | +0.99% | **+0.19pp** |
| Weighted Sharpe | 0.24 | 0.30 | **+0.06** |

### Portfolio simulation (5 concurrent slots, compound DD)
| Metric | Baseline (flat) | §87 (sizing) | Δ |
|:---|---:|---:|---:|
| Portfolio CAGR | +3.6% | +3.7% | **+0.1pp** |
| Portfolio Ann.Sharpe | — | — | **no longer reported** (was T-bill-inflated) |
| Portfolio Max DD | -6.16% | -6.33% | -0.17pp |
| Skipped (slots full) | 21 (9.7%) | 21 (9.7%) | +0 |

> ⚠ The previous Ann.Sharpe figures (2.87 → 3.03) were T-bill-inflated event-time artifacts
> and are no longer reported as real numbers. CAGR remains the honest summary metric.

**Verdict: DEPLOY with monitoring.**

- Sizing-only layer improves CAGR +0.1pp with zero trade-count cost.
- MC P5 = 0.07 > 0 confirms edge survives block-bootstrap autocorrelation correction.
- Slight DD worsening (-0.17pp) is acceptable given Sharpe gain; DD-throttle (R7) still deployable and additive.
- Sizing mode is strictly superior to the previous filter mode (skip single-day spikes) because it retains marginal trades at reduced size rather than discarding them entirely.

**Code:** Backtest in `simulate_ticker()` (`backtest_technicals.py`); live engine in `_apply_l10_conviction_sizing()` (`scanner.py` lines 1530–1580), wired at Step 5b of the scan pipeline.

---

## §DELIV Lessons — The Live-vs-IS Gap Was Mostly Delivery (2026-06-10)

A DB-level audit of the delivered book overturned the working theory that the live-vs-IS WR gap (~43% vs ~69%) was regime mismatch or signal decay. **Most of it was delivery leaks** (full data: Stats.md §DELIV):

1. **Audit delivery before blaming the signal.** Three leaks compounded: blocked sectors not actually blocked (model-file "dynamic unblock" — 32% of the book at ≈−1.4%/trade), SELL delivery with negative edge bypassing confidence floors, and per-sector calibration silently OFF (81% null `sector_rs`). Clean book (May+ BUYs ex-blocked): **57.8% net WR, +2.06%/trade net** — near-IS economics were there all along.
2. **File existence is not a promotion gate.** A sector-model training run re-opened deliberately-blocked XLI 3 days after it was blocked, just by writing `backtest_ml_model_XLI.json`. Policy changes must go through an explicit promotion record (QENG-1c), never artifact side-effects.
3. **Deconfound before filtering.** "Stale deliveries earn +0.38%/trade" was sector composition: within clean sectors, stale deliveries earn +2.12%. A 120-min staleness cutoff would have dropped ~82% of good deliverable trades — the ATR≤70 N-collapse trap, delivery edition. The correct guard is price-validity (entry ± 0.5×ATR / stop breach), not age.
4. **Sizing > filtering, again (§87).** The consec-score signal worth +0.14 Sharpe as a filter (−73% N) captures +0.06 Sharpe as a 1.3× sizing tier at ΔN=0 — now live as L10. Same pattern as L7/L8.
5. **Claims need instrumentation.** §87's original "+0.03, deployed" was unverifiable (no report section consumed the multiplier) and undeployed. If an A/B can't show the effect, the effect is a claim, not a result.
6. **The IS statistical budget is spent.** v10.9 canon DSR fails at the honest 744-trial count (E[max]=0.25 > IS 0.24). Every additional IS sweep raises the bar retroactively. Edge proof now lives in the post-fix forward window (first uncontaminated live sample), OOS accrual, and orthogonal data.

---

## §104–§110 Free Alt-Data Integration — Retraction & Post-Mortem (2026-06-11)

**Question:** Can free alt-data panels (FINRA short volume, SEC fails-to-deliver, NAAIM positioning, Wikipedia pageviews) improve the Signal.Trade edge?

**Honest answer as of this writing:** Not yet demonstrated above the harness noise floor. The first-pass cross-sectional results looked promising but contained **two implementation defects** that invalidate the headline numbers. The per-trade tilt verdicts remain valid.

### Per-trade tilt verdicts (legacy 23-year book) — STILL VALID
| Tilt | Pre-registered threshold | N | Result | Deployed? |
|:---|:---|---:|:---|:---|
| FINRA SV ratio ↓ | `sv_ratio_5d_delta < −2.0` | ~49 | FAILED (underperformed baseline) | No |
| FINRA SV extreme | `ratio>40 AND delta<−10` | 8 | Data snooping (P≥80% luck on ≥6 looks) | No — SPRT ID 10 exploratory only |
| SEC FTD >75 pctile | `ftd_63d_pctile > 75` | ~5 | INCONCLUSIVE | No — SPRT ID 9 only |
| NAAIM exposure <30 | `naaim_exposure < 30` | ~18 | FAILED (−0.054% avg) | No |

**Lesson:** A per-trade condition that fires on <20% of a 217-trade book yields N≈8–35 cohorts. At baseline WR ~69%, P(≥7/8 wins) ≈ 23% on one cut; with multiple threshold/grid searches, most "discovered" cohorts are noise. **Rare-extreme features belong where breadth gives N: the cross-sectional model or a forward SPRT.**

### Cross-sectional integration — FIRST-PASS RESULTS RETRACTED
All five sources were wired into `backend/scripts/cross_sectional_alpha_model.py`, but the initial backtest table was wrong for two reasons:

**Defect 1: market-wide features z-scored to death.** UMCSENT, NAAIM, and AAII are identical for every ticker on a given date. `cross_sectional_zscore()` standardized per-date, giving std=0 → NaN → `fillna(0)` dead columns. Because `train_model()` only sees `*_z` columns, these features contributed zero information. The apparent +0.095 from `--naaim` was XGBoost `colsample_bytree=0.8` sampling noise: adding dead columns changed which price features were sampled in each tree, producing a different (but informationally equivalent) model. **Fix:** market-wide features are now passed through RAW so trees can use them as regime/context splits interacting with z-scored per-ticker features.

**Defect 2: same-day lookahead for FINRA SV and Wikipedia.** `build_panel()` called `load_short_volume_panel()` / `load_wikipedia_panel()` raw and merged same-day with `merge_asof(..., direction='backward')`. But FINRA SV for day T publishes ~6pm ET after the close; Wikipedia views for day T are final only after the day ends. Both are tradable from T+1 onward. The per-trade PIT merge functions (`merge_sv_pit`, `merge_wikipedia_pit`) correctly lagged +1 day, but the cross-sectional harness did not. **Fix:** both panels are shifted +1 calendar day before `merge_asof` in `build_panel()`.

**Coverage caveats:** Wikipedia is a 20-mega-cap pilot (AAPL, MSFT, NVDA, TSLA, META, GOOGL, AMZN, JPM, V, JNJ, UNH, XOM, PG, HD, MA, ABBV, PFE, CVX, PEP, LLY), 2015-07 → 2024-12, so the majority of names get zero and the last 1.5 years of the walk-forward have no wiki data. FINRA SV is consolidated NMS 2019-01 → 2024-12, not the §104-promised 2009+ per-venue history. SEC FTD uses `effective_date = settlement_date + 30d` and was correctly lagged.

### Corrected single-split previews (h=21, 10bps one-way)
These are quick previews after the code fixes; full walk-forward results are pending.

| Config | Net Sharpe | Note |
|--------|------------|------|
| baseline | 0.369 | price features only |
| `--finra-sv` | 0.414 | +1d lag applied; 40% coverage |
| `--wiki` | 0.451 | +1d lag applied; 2% coverage (20 mega-caps) |
| `--naaim` | −0.182 | market-wide now usable and actively harmful |
| `--naaim --wiki` | 0.111 | |
| placebo (3 seeds) | 0.151–0.159 | 3 pure-noise features |

### Corrected walk-forward (h=21, 10bps one-way)
| Config | Net Sharpe | Gross Sharpe | Positive folds | Mean IC |
|--------|------------|--------------|----------------|---------|
| baseline (price only) | 0.195 | 0.300 | 9/15 | +0.0016 |
| `--finra-sv` | 0.287 | 0.396 | 9/15 | +0.0032 |
| `--wiki` | 0.215 | 0.316 | 8/15 | +0.0033 |
| `--naaim` | 0.163 | 0.292 | 8/15 | +0.0085 |

### Corrected walk-forward (h=63, 10bps one-way)
| Config | Net Sharpe | Gross Sharpe | Positive folds | Mean IC |
|--------|------------|--------------|----------------|---------|
| baseline (price only) | 0.616 | 0.662 | 10/14 | +0.0207 |
| `--wiki` | 0.694 | 0.742 | 11/14 | +0.0199 |
| `--finra-sv` | 0.454 | 0.490 | 10/14 | +0.0205 |
| `--naaim` | 0.328 | 0.380 | 10/14 | +0.0176 |

### Placebo distribution (10 pure-noise seeds, 3 noise features each)
| Horizon | Mean net Sharpe | 5%-95% band | Min / Max |
|---------|-----------------|-------------|-----------|
| h=21 | 0.309 | [0.286, 0.332] | 0.284 / 0.335 |
| h=63 | 0.708 | [0.688, 0.724] | 0.687 / 0.728 |

At h=21, `--finra-sv` lands inside the placebo band; `--wiki` and `--naaim` land *below* it (and below baseline). At h=63, `--wiki` lands inside the placebo band, while `--finra-sv` and `--naaim` land well below it. Adding alt-data does not produce a net-Sharpe uplift that is distinguishable from adding random noise.

### Paired per-fold/rebalance bootstrap: real vs baseline
| Comparison | ΔSharpe | 90% CI | two-sided p |
|------------|---------|--------|-------------|
| wiki vs baseline, h=21 | +0.011 | [−0.052, +0.072] | 0.771 |
| finra_sv vs baseline, h=21 | +0.053 | [−0.034, +0.134] | 0.513 |
| naaim vs baseline, h=21 | −0.019 | [−0.257, +0.206] | 0.900 |
| wiki vs baseline, h=63 | +0.077 | [−0.115, +0.310] | 0.610 |
| finra_sv vs baseline, h=63 | −0.163 | [−0.372, +0.038] | 0.461 |
| naaim vs baseline, h=63 | −0.288 | [−0.691, +0.214] | 0.521 |

No alt-data configuration shows a ΔSharpe whose 90% confidence interval excludes zero.

### Coverage-epoch attribution (full S&P universe, walk-forward 2012→2026)
Epoch split by calendar years: `pre_2019`, `2019_2024`, `post_2024`.

**h=21 net Sharpe by epoch**
| Config | pre-2019 | 2019-2024 | post-2024 |
|--------|----------|-----------|-----------|
| `--wiki` | +0.063 | +0.702 | −0.839 |
| `--finra-sv` | +0.231 | +0.702 | −1.020 |
| `--naaim` | +0.254 | +0.546 | −1.545 |

**h=63 net Sharpe by epoch**
| Config | pre-2019 | 2019-2024 | post-2024 |
|--------|----------|-----------|-----------|
| `--wiki` | +0.559 | +0.929 | +0.558 (2025 only) |
| `--finra-sv` | +0.315 | +0.819 | +0.172 (2025 only) |
| `--naaim` | −0.068 | +0.965 | +0.113 (2025 only) |

The h=21 "edge" is entirely confined to the 2019-2024 coverage window and reverses sharply post-2024, when Wikipedia/FINRA-SV coverage ends. The h=63 pre-2019 numbers are also positive, but the paired bootstrap still does not separate them from baseline sampling noise.

### Horizon-as-hyperparameter
Treating horizon as a tunable hyperparameter selected on the first half of folds (2012-2019) and evaluated on the second half (2020-2026) selects **h=63**. Its out-of-sample net Sharpe on the held-out folds is **+0.494**, not the full-sample +0.616. This is the honest, selection-adjusted estimate for a default HORIZON=63.

Selection-fold scores by candidate horizon:
| Horizon | 21 | 42 | 63 | 84 | 126 |
|---------|----|----|----|----|-----|
| Selection-fold net Sharpe | +0.008 | +0.259 | +0.381 | +0.303 | −∞ |

### EDGAR fundamental factors (SimFin proxy) — 2026-06-11
SimFin bulk data was not yet on disk (requires a free `SIMFIN_API_KEY`), so the same canonical monthly-horizon fundamental alpha was tested with the existing EDGAR panel (`--fundamentals`, `--universe curated`): Piotroski change, gross profit / assets, asset growth, and net buyback yield.

| Horizon | Baseline (curated) | +EDGAR fundamentals | Placebo band (10 seeds) | ΔSharpe vs baseline |
|---------|--------------------|---------------------|-------------------------|---------------------|
| h=21 | 0.259 | 0.138 | [0.440, 0.520] | −0.070 [−0.242, +0.095] |
| h=63 | 0.364 | 0.358 | [0.398, 0.460] | −0.006 [−0.344, +0.295] |

At both horizons the fundamental overlay is **inside or below the placebo band** and the paired bootstrap ΔSharpe confidence interval includes zero. The fundamental factors do not currently add net-of-cost Sharpe above the harness noise floor.

### Pre-registered entry-timing ablation: close vs next-open (§96b)
Ran `backtest_technicals.py` with the default next-open fill and with `--entry-at-close` (sequential mode to avoid macOS fork deadlocks). Same 217-trade IS universe, 0.5% round-trip friction.

| Variant | N | Win Rate | Avg Return / Trade | Sharpe | Max DD |
|---|---|---:|---:|---:|---:|
| Next-open entry (canon) | 217 | 69.1% | +0.80% | **0.24** | −2.31% |
| Close entry (signal-day fill) | 217 | 66.4% | +0.92% | **0.25** | −1.79% |

ΔSharpe = **+0.01**, ΔAvgRet = **+0.12%**, but win rate falls by 2.7pp. The overnight/intraday decomposition on the canon book shows intraday contribution (50.5%) slightly exceeds overnight (49.5%), and the script’s own §96b verdict flags close-entry as **ΔSharpe = 0.00** once execution realism is considered. Close-entry is therefore **not a meaningful edge improvement**; it is an execution convenience at best, with the caveat that the signal must be computable ~10 minutes before the close.

### What the defects teach
1. **Cross-sectional standardization is not feature-agnostic.** A feature that is constant across the cross-section must be handled differently (raw, or as an interaction with per-ticker features). Blind z-scoring silently kills it.
2. **PIT discipline must be enforced in every merge path.** Having correct lag logic in one code path (per-trade backtest) does not protect another code path (cross-sectional panel) from lookahead.
3. **Coverage epoch matters.** A feature that exists only for 20 names and only until 2024-12 cannot support claims about the full 2012→2026 walk-forward. Per-fold attribution by coverage epoch is mandatory.
4. **The DSR/selection lesson applies to horizon sweeps too.** Picking the maximum of 6 horizons and quoting its unadjusted CI is the same selection mistake the project already identified in IS backtests. The non-monotonic table (h=25 0.288 → h=30 0.128 → h=40 0.488) is a warning sign.
5. **Placebo features are a necessary control.** If adding real features produces the same magnitude of ΔSharpe as adding noise features, the effect is not distinguishable from sampling noise.

### Required before claiming an alt-data effect
- [x] Corrected walk-forward for `--finra-sv`, `--wiki`, `--naaim`, and combos.
- [x] Silent-failure guard: `build_panel()` now raises if an explicitly requested alt-data flag's merge fails or its panel is missing.
- [x] Placebo distribution: 10 placebo seeds per horizon; real-feature net Sharpe is inside or below the noise band.
- [x] Paired per-fold daily-return bootstrap for real features vs baseline; no ΔSharpe CI excludes zero.
- [x] Per-fold attribution split by coverage epoch (pre-2019, 2019-2024, post-2024); h=21 effect is confined to the 2019-2024 coverage window and reverses post-2024.
- [x] Horizon-as-hyperparameter treatment: h=63 selected on 2012-2019 folds; OOS net Sharpe on 2020-2026 folds is +0.494.
- [x] Reproducibility guard: migrated panel persistence from pickle to Parquet in `finra_short_volume`, `sec_ftd`, `sentiment_naaim_aaii`, and `wikipedia_pageviews`. Loaders read `.parquet` and fall back to the legacy `.pkl` once, then rewrite to Parquet.

### Honest verdict
No alt-data config has demonstrated a reproducible, properly-lagged, selection-adjusted effect above the harness noise floor. The h=63 net 0.769 claim is **withdrawn**. The strongest honest estimate for a default h=63 is the horizon-selection OOS net Sharpe of **+0.494**, not the full-sample +0.616. Wikipedia's h=63 net Sharpe of +0.694 is inside the placebo band [+0.688, +0.724], its h=21 edge disappears outside the 2019-2024 coverage epoch, EDGAR/SimFin-style fundamental factors also fail to add Sharpe, and the pre-registered close-entry A/B shows **ΔSharpe ≈ 0.00** (0.24 → 0.25). The per-trade tilt verdicts stand: these panels are retained for cross-sectional reuse and forward SPRT, not as IS-validated sizing boosts.

**Code:** `backend/scripts/analyze_cross_sectional_alt_data.py` runs the full attribution pipeline; `backend/scripts/cross_sectional_alpha_model.py` now exports per-fold returns and has strict merge-failure guards; backfill loaders in `backend/services/{finra_short_volume,sec_ftd,sentiment_naaim_aaii,wikipedia_pageviews}.py` persist Parquet; per-trade tilt harness in `backend/scripts/backtest_technicals.py`.

### Addendum: per-fold nested-horizon validation (2026-06-11, `--nested-horizon`)
The single-split horizon test above (select on 2012-2019 → OOS 2020-2026 = +0.494) is now complemented by a per-fold expanding-window version: `cross_sectional_alpha_model.py --nested-horizon` re-selects the horizon for EVERY walk-forward fold using only folds strictly before it (grid {21,40,63}, burn-in 2, full universe, price features only, 10bps). Result: **h=63 won the ex-ante selection in all 12 eval folds (2014–2025)** — the prior-evidence ranking never flipped — giving nested net Sharpe **+0.576 [90% CI +0.22, +0.91]**, ann ret +6.9%, **selection haircut 0.000** vs fixed h=63 on the same folds (h=21: +0.419, h=40: +0.438). Mixed-horizon annualization via `_mixed_horizon_stats()` (reduces exactly to `_stats()` at constant horizon).

**Read:** the quarterly-rebalance cost-structure effect is real and was ex-ante capturable from as early as 2014 with two folds of evidence — this is a genuine, selection-clean improvement over the h=21 default, NOT a false dawn. Remaining caveats before any deploy decision: (1) the grid itself {21,40,63} descends from the contaminated sweep — this validates 63-beats-21/40, not 63-is-optimal; (2) per-fold dispersion is wide (2018: −1.80, 2021: +2.26; 8/12 folds positive); (3) ~~borrow/cost sweeps~~ **CLOSED 2026-06-11** — h=63 full-WF track (net 0.616, CI [+0.29, +0.94], 10/14 folds positive, MaxDD −11.8%, mean IC +0.021): cost sweep +0.481 at 40bps one-way (h=21 went NEGATIVE there — the cost-robustness gap is the whole thesis confirmed); borrow sweep +0.572/+0.528 at realistic 50/100bps GC, breakeven ≈700bps/yr; conservative 20bps-exec + 150bps-borrow combo ≈ +0.44; (4) ~~shadow scorer horizon~~ **CLOSED 2026-06-11 — parallel h=63 shadow deployed.** Rather than replacing the h=21 model (which would break its forward-accrual continuity), both horizons now run side by side: `--save-model --horizon 63` persists to `cross_sectional_{model,features}_h63.json`, `cross_sectional_shadow.score_batch_h63()` ranks each scan batch with it, and `scan_all()` attaches `crossSectionalShadowPctH63` (+ `xs_shadow_pct_h63` in the rationale meta) alongside the existing h=21 field. The two forward series will arbitrate which horizon's ranking transfers to the live ~10d book. **§92 promotion criteria remain tied to the h=21 field ONLY** — the h=63 shadow never feeds promotion or sizing. Default `HORIZON` stays 21 in the research script.


### Addendum: §110 CBOE options snapshot shipped (2026-06-11)
The free CBOE delayed-quotes options endpoint (`cdn.cboe.com/api/global/delayed_quotes/options/{SYMBOL}.json`) was wired into production as a live-only data source:

- `services/options_cboe.py` parses the full chain (bid/ask, IV, OI, volume, greeks) and returns an aggregate dict matching the existing `services/options.py` contract.
- `services/options.py` fallback order is now **Polygon → CBOE → yfinance**.
- `models.py` adds `OptionsChainDaily`; Alembic migration `20260611_1945_404971b9f841_add_options_chain_daily` is applied.
- `scripts/snapshot_cboe_options.py` upserts one row per ticker per day.
- `main.py` supervises `nightly_cboe_options_snapshot` at 6:30pm ET.

There is no backtest history; the table accrues forward from 2026-06-11 onward. This starts the self-grown IV-rank / skew / PCR series that reduces the scope of any future paid options-data purchase to deep *historical* IV only.


### Addendum: §104a FINRA per-venue backfill results (2026-06-11)
`services/finra_short_volume.py` was extended to download the pre-consolidation venue files (FNRA, FNSQ, FNYX) for 2009-08-03 → 2018-07-31 and the consolidated `CNMS` file from 2018-08-01 onward. Per-venue rows are aggregated by `(date, symbol)` so the panel now covers the full 2009+ history promised in §104. The parser was hardened for early files that lack `ShortExemptVolume` and for recent files that report fractional share volumes. Final panel: **34,505,889 rows**, 2009-08-03 → 2026-06-11.

Cross-sectional attribution re-run (`--configs baseline finra_sv --horizons 21 63`, 5 placebo seeds, output `data/alt_data_attribution_finra_sv_2009.json`):

| Horizon | Baseline net Sharpe | FINRA SV net Sharpe | Placebo band | Coverage | Verdict |
|---------|--------------------:|--------------------:|-------------:|----------|---------|
| h=21 | +0.195 | +0.295 | [+0.285, +0.332] | 79% | inside placebo |
| h=63 | +0.616 | +0.586 | [+0.687, +0.726] | 79% | below placebo |

Paired bootstrap ΔSharpe vs baseline: h=21 **+0.058** [−0.036, +0.142], p=0.287; h=63 **−0.031** [−0.192, +0.153], p=0.768.

**Conclusion:** extending FINRA SV from 6/15 folds to 15/15 folds and from 2019-2024 to 2009+ does **not** produce a Sharpe uplift distinguishable from the harness noise floor. The h=21 effect is inside the placebo band; h=63 is below it. The 6/15 fold coverage problem was real, but resolving it falsifies the alt-data claim rather than confirming it.

### Addendum: §104b FRICTION=0.5% validation (2026-06-11)
The QENG-3a fill ledger (`broker_orders` + `fills`) exists and is migrated, but contains **zero fills** — auto-execution has not yet produced a broker fill sample. A new script, `scripts/analyze_realized_friction.py`, is ready to measure realized round-trip cost per ticker and per ADV bucket once fills accrue. Until then the canonical 0.5% round-trip assumption remains the deliberate ~2× conservative buffer documented in R10-8; no backtest constant was changed.

### Addendum: §107 GDELT bounded pilot results (2026-06-12)
The GDELT fetcher was corrected to use GKG 1.0 daily zip files (`http://data.gdeltproject.org/gkg/YYYYMMDD.gkg.csv.zip`) rather than the non-existent daily GKG 2.0 path. Downloads are now concurrent. The missing `--gdelt` merge block was added to `scripts/cross_sectional_alpha_model.py` with the same +1-day PIT lag used for Wikipedia and FINRA SV. A full 2015+ panel for the 20-ticker pilot was built: **74,189 ticker-day rows** over 4,180 calendar days (2015-01-01 → 2026-06-11).

Per-trade tilt validation (`backtest_technicals.py --gdelt`, MR-only canon, 23-year IS window):

| Variant | N | Win Rate | Avg Return | Sharpe | Max DD |
|---|---|---:|---:|---:|---:|
| Baseline (no GDELT) | 217 | 69.1% | +0.80% | 0.24 | -2.31% |
| +GDELT tone capitulation sizing tilt | 217 | 69.1% | +0.80% | 0.24 | -2.31% |
| Δ | 0 | 0.0 pp | 0.00 pp | **0.00** | — |

The GDELT tilt (`tone_z < -1.5` at entry → 1.10× size) **fired on zero trades** in the 217-trade canon book; the panel is present but the condition never coincided with a mean-reversion entry. The per-trade verdict is therefore **no effect, not negative** — the hypothesis that negative-news tone at oversold entry marks capitulation found no triggering instances in the IS window.

Cross-sectional validation (`cross_sectional_alpha_model.py --gdelt --placebo --walk-forward`, h=21, full S&P 500 survivorship-corrected universe, 15 expanding folds 2012→2026):

| Variant | Net Sharpe | Gross Sharpe | Ann. Return (net) | Max DD |
|---|---|---:|---:|---:|
| Baseline + placebo noise | 0.307 | 0.419 | +4.44% | -30.97% |
| +GDELT tone_z + placebo noise | 0.304 | 0.415 | +4.38% | -31.71% |
| Δ | **-0.003** | -0.004 | -0.06 pp | — |

The +GDELT ΔSharpe is well inside the harness noise floor and the 90% bootstrap CI on the net Sharpe ([-0.113, +0.709]) includes zero. Mean rank IC is +0.0012 with GDELT vs +0.0041 baseline — actually lower.

**Conclusion:** the GDELT bounded pilot **does not add deployable edge** in either the per-trade MR book or the cross-sectional L/S book. The infrastructure (fetcher, panel, PIT merge, tests, nightly-snapshot readiness) is retained because GDELT is free and the news-sentiment family is already wired live; if a future variant (e.g., a more aggressive entity→ticker mapping, headline-only filtering, or event-day spike detection) wants another look, it must be pre-registered and validated on untouched forward data. The §107 per-trade guardrail stands: a tilt that fires on 0% of the IS book is unfalsifiable and must not be deployed.

---

## FRED `realtime_start` Trap — Gate 2 + §14 Panel Silently Dead for 3 Days; §14 Verdict FLIPPED (2026-06-12)

**Finding (backtest-logic audit):** the v8.3-review fix d55a26e (2026-06-09) keyed FRED observations to `o["realtime_start"]` intending the publication date. But FRED's observations endpoint only returns real vintage dates when the request carries an explicit realtime window — **by default every observation echoes `realtime_start` = TODAY**. Verified live: 1,222 STLFSI4 observations collapsed to a single dictionary key dated today. Every run since 06-09 (including the v10.9 canon) had `stlfsi4.get(date)` → None on all historical dates: **Gate 2 and the §14 FRED panel were silently inactive.**

**Fix:** observation-date keying + per-series real publication lag (`pub_lag_days` param on `fetch_fred_series()`: 7 for weekly STLFSI4/NFCI, 1 for daily BAA10Y/T10Y3M) — the join the v8.3 review actually prescribed. True ALFRED vintages are unusable here: STLFSI4 was created in 2020, so first-release keying would erase all pre-2020 history. Verified: 8,548 daily keys restored; COVID crisis print (5.66, week ending 2020-03-20) correctly invisible until 2020-03-27.

**Impact on canon: zero.** Full re-run with the live gate: N=217, WR 69.1%, Sh 0.24, CI [0.10, 0.37] — identical. Gate 2's block condition (STLFSI4>1.5 ∧ VIX>30) is subsumed by Gate 1's VIX>30 hard block.

**But the §14 verdict flips.** First honest §14 measurement (panel populated, lagged): 22 trades blocked (10.1%), WR +1.2pp, avg +0.12pp, **Sharpe 0.24→0.27 (+0.03), MaxDD −2.31%→−0.93%**. This agrees with the pre-bug 2026-06-08 read (+0.02, 18 blocked). The "§14 −0.06 harmful" A/B (2026-06-10) that justified deleting §14 hard blocks from live delivery is the irreproducible outlier — a dead panel must produce Δ=0.00 exactly, so −0.06 measured something else. **Two consistent working-panel reads (+0.02/+0.03 with ~60% MaxDD reduction) vs one broken one.** Live re-instatement of §14 delivery gating is now an open decision (QENG-1c promotion discipline applies; restoring a pre-registered gate on corrected evidence is not data mining).

**Lessons:** (1) An API's field name is not its semantics — verify what a "fix" returns before trusting it (one `print(len(...))` would have caught this on 06-09). (2) A gate that silently receives None fails open — gate inputs need liveness asserts (n keys ≥ expected coverage), the same class of guard the cross-sectional harness got after the alt-data retraction. (3) Decisions inherit the bugs of their measurements: the §14 deletion was made off a measurement taken while the input was dead.

**Audit clean bill:** exit engine (stop-before-target, gap-through slippage, fill-bar-anchored stops), entry timing, PIT constituents hard-fail, date-sorted MaxDD, registry-driven DSR trial count, no indicator look-ahead. Minor residuals noted: unmapped constituents return True (silent survivorship bypass), `in_trade_until` calendar-day undershoot, FF ST_Rev unlagged (moot while meta-model is gated off).

## Disposition of the Root "Sharpe Improvement Analysis" (2026-06-09 doc, retired 2026-06-12)

A 415-line external-lens analysis (`SHARPE_IMPROVEMENT_ANALYSIS.md`, repo root) recommended ~12 changes to lift Sharpe while holding N. The doc was deleted in the 2026-06-12 docs consolidation; this entry records what survived contact with measurement, so its ideas don't get re-proposed:

- **Adopted:** non-linear score-band sizing (§4.2 → shipped as L7 score-band, +0.05 Sharpe, v10.8); dynamic stops (§4.1's spirit → dynamic RSI stops, 2.0× ATR when RSI<30, embedded in the v10.8 baseline); conviction-tier sizing direction generally vindicated by §87 L10 (+0.06).
- **Tested and rejected:** condition-based adaptive exits (§4.3, "RSI>45 exit shows 100% WR") — the 2026-06-08 `--exit-sweep` grid found the exit lever exhausted: top configs were turnover artifacts, max_loss=OFF dominated every robust axis. The "100% WR" cited was a small-N in-sample read.
- **Superseded diagnosis:** the doc attributed the live-vs-IS gap (−28pp WR) to exits and flat sizing. The v8.4 delivery audit (2026-06-10) showed the gap was **mostly delivery leaks** — sector model-file unblock (32% of book at ≈−1.4%/trade), SELL delivery bypass, stale EOD entries — not exit management. Honest clean-book re-baseline: 57.8% net WR, +2.06%/trade.
- **Not pursued:** inverting the VIX sizing dampener (§4.4) — the strategy is structurally a VIX 20–30 stress-regime play (100% of IS trades); §56 VIX-conditional Kelly sizing already covers the regime axis, and §88's calm-sleeve failure showed the calm side has no trades to size.

**Lesson:** plausible mechanism-level recommendations from code reading alone (without per-fold measurement) had roughly a 1-in-4 hit rate here — every adopted item was the one that had already been independently validated by a sweep.

## §85-2 MD&A Sentiment Audit — Modifier Never Fired Historically (2026-06-09; doc folded in 2026-06-12)

*(Condensed from the retired `docs/MDA_AUDIT_85_2.md`.)*

**Finding:** the MD&A sentiment modifier had **never fired** on any of the 566 resolved signals — 0 had `mda_delta` in rationale, 0 had any EDGAR source (buyback gate worked: 77).

**Root cause:** `_fetch_filing_text()` in `services/edgar.py` used the deprecated EDGAR `-index.json` URL pattern, which 404s. The code failed silently → `get_mda_delta()` always returned `{}` → the `abs(_mda_score) >= 2.0` trigger never fired.

**Fix (v8.2, 2026-06-09):** consume `primaryDocument` directly from the SEC submissions JSON (also one fewer HTTP round-trip per filing). Verified on AAPL: 2 filing texts returned, delta 0.0 as expected for a stable large-cap. Also removed the dead `^BDI` fetch from `supply_chain.py`.

**Open items (tracked as §85-2b in TODO):** monitor signals with `mda_delta != 0` going forward; evaluate ΔWR at N≥50 and disable the modifier if no improvement. `_KNOWN_CIKS` covers only ~60 tickers — unknown tickers silently return `{}`.

**Lesson (same family as the FRED `realtime_start` trap):** a modifier whose data dependency fails silently is indistinguishable from a modifier with no edge — instrument the *input* (fetch success rate), not just the output.

## §112–§116 Free Alt-Data Ablations — v8.7 (2026-06-12)

**Context:** v8.7 wired five additional free alternative-data paths into the cross-sectional harness (§112 CBOE self-grown IV-rank history, §113 FINRA ATS weekly dark-pool participation, §114 SEC FTD velocity, §115 NAAIM/UMCSENT rolling percentiles, §116 Wikipedia cross-sectional attention). This section reports the corrected walk-forward/placebo ablations and the honest verdict on each.

**Infrastructure / panel status before the ablation:**
- SEC FTD panel rebuilt and extended to 2004: `build_ftd_panel(start=2004-01-01)` → 11.2M rows, date range 2017-07-15 → 2026-06-13; features `ftd_63d_pctile` and `ftd_pctile_chg_1m` merged with +30d publication lag.
- NAAIM/UMCSENT panels regenerated with percentile features: `naaim_exposure_pctile` (52-week rolling percentile) and `umcsent_pctile` (24-week rolling percentile), passed through raw as market-wide regime features.
- Wikipedia panel recalculated with cross-sectional z-score `views_z_xs` (per-date demeaning) and +1d PIT lag.
- FINRA ATS downloader hardened: the historical `otctransparency.finra.org` endpoint now returns HTML instead of CSV; historical backfill is blocked, so the ATS panel is empty and only live-forward accumulation is possible.
- CBOE IV-rank history self-accumulates from 2026-06-12 onward; only 68 one-day observations exist, so no historical backtest is possible yet.

**Methodology:** All runs use `backend/scripts/cross_sectional_alpha_model.py --walk-forward --wf-start 2012 --wf-test-years 1 --placebo --placebo-seed 42 --universe curated --cost-bps 10 --decile 0.10`. This is the same h=21 expanding-window harness used in the §104–§110 retraction, with price/volume base features plus one placebo noise feature. The baseline therefore already includes the full price-feature set and a placebo control; each row below adds the named alt-data feature(s) on top.

**h=21 walk-forward results (15 expanding folds, 2012→2026):**

| Config | Net Sharpe | Gross Sharpe | Mean IC | Positive folds | Coverage | Verdict |
|---|---:|---:|---:|---:|---:|---|
| Baseline (price + placebo) | **0.395** | 0.479 | +0.0203 | 10/15 | — | — |
| +SEC FTD velocity (`ftd_pctile_chg_1m`) | 0.353 | 0.436 | +0.0209 | 11/15 | 45% | inside noise |
| +NAAIM/UMCSENT pctile | −0.040 | 0.039 | +0.0151 | 7/15 | 100%/89% | inside noise / worse |
| +Wikipedia `views_z_xs` | 0.410 | 0.494 | +0.0211 | 11/15 | 4% | inside noise |
| +All three above combined | 0.029 | 0.106 | +0.0192 | 8/15 | mixed | inside noise / worse |
| +FINRA ATS `ats_ratio` | *not testable* | — | — | — | 0% | endpoint blocked |
| +CBOE IV-rank | *not testable* | — | — | — | <1d | live-forward only |

**Placebo interpretation:** The baseline itself has a 90% Sharpe CI of [−0.058, +0.919]; every alt-data variant's net Sharpe CI also includes zero. The ΔSharpe between any alt-data config and baseline is within the harness noise floor (the +0.015 wiki Δ, −0.042 sec_ftd Δ, −0.435 naaim Δ, and −0.366 combined Δ are all small relative to sampling variation across folds).

**Per-source verdicts:**
- **§114 SEC FTD velocity:** No edge. The 1-month change in FTD percentile is available for 45% of ticker-days but does not improve rank IC or net Sharpe. The 2017+ coverage epoch is too short and the signal too weak to beat 10bps one-way turnover.
- **§115 NAAIM/UMCSENT percentiles:** No edge; combined config is actually worse (net Sharpe −0.040). Market-wide sentiment as a raw regime feature does not interact strongly enough with the cross-sectional price features to produce a net-of-cost spread. This aligns with the §106 retraction.
- **§116 Wikipedia attention (`views_z_xs`):** No edge at 4% coverage. The 20-name pilot is too narrow to move the 109-name curated book; the feature is nearly always missing and is ignored or imputed by the booster. Widening coverage is the only remaining free-data hope, but the pilot result gives no evidence it will help.
- **§113 FINRA ATS:** Historical backfill is blocked by FINRA (`otctransparency.finra.org` returns HTML). The newer `api.finra.org` sample lacks per-ticker total-volume denominator needed for `ats_ratio`. Verdict: live-forward accumulation only; no research claim possible until ≥1 year of weekly data accrues.
- **§112 CBOE IV-rank:** Live-only by design. The self-grown history began 2026-06-12 (68 tickers, one snapshot). A backtest requires ≥252 prior observations per ticker; earliest possible validation is ~12 months of nightly snapshots.

**What the ablations teach:**
1. **Coverage breadth matters more than feature cleverness.** Wikipedia's cross-sectional z-score is statistically sensible but covers only 4% of the book; it cannot influence the portfolio. FINRA ATS has 0% coverage historically.
2. **Market-wide features face a high bar.** NAAIM/UMCSENT are regime/context variables; trees can split on them but they do not create a cross-sectional spread at h=21 after costs.
3. **Turnover cost dominates weak features.** Even a feature with positive mean IC (~0.021) does not lift net Sharpe because the added turnover (1.25→1.27×) and the 10bps cost drag consume the spread.
4. **Combining weak features does not create a strong one.** The combined config is the worst performer — trees overfit to the extra noise and the turnover structure is unchanged.

**Forward gates (unchanged):**
- §91 rising-SI sizing tilt: ≥50 rising-SI resolved signals.
- §92 cross-sectional shadow promotion: ≥150 tagged signals (h=21 field only).
- Post-fix forward audit: ≥50 post-fix resolved signals for CAL-1 v5.
- OOS v7/v8 validation: ≥30 live trades per pre-specified ticker list.
- §112 CBOE IV-rank: ≥252 nightly snapshots per ticker before any backtest.

**Honest status:** No free alt-data path among §112–§116 has demonstrated a deployable edge. The v8.6 retraction stands. Paid alt-data (§98 ORATS, Unusual Whales, ORTEX) remains unjustified until a free-data path first clears IC > ~0.03 in a properly lagged, walk-forward, cost-adjusted harness. The infrastructure is retained because the sources are free and the forward-shadow/SPRT gates can reuse them; the only honest near-term action is live-forward accumulation for §112 and §113.

**Code:** `backend/scripts/run_free_alt_ablations.sh` runs baseline, SEC FTD, NAAIM, Wikipedia, and combined ablations; `backend/scripts/cross_sectional_alpha_model.py` enforces PIT lags and raises on merge failure; `backend/scripts/summarize_free_alt_ablations.py` parses logs into `backend/data/alt_ablations_summary.json`; panel builders are in `backend/services/{options_cboe.py, finra_ats_dark_pool.py, sec_ftd.py, sentiment_naaim_aaii.py, wikipedia_pageviews.py}`. Raw logs: `backend/data/alt_ablations/{baseline,sec_ftd,naaim,wiki,combined}.log`.

## §117 Sector-Specific XGBoost Promotion Gate — Implementation Notes (2026-06-12)

**Problem:** v8.1 unblocked blocked sectors (XLF/XLP/XLU/XLI) by checking whether `data/backtest_ml_model_{SECTOR}.json` existed. A training run wrote `backtest_ml_model_XLI.json` three days after XLI was blocked, reopening the sector and leaking ~32% of the live book at ≈−1.4%/trade.

**Fix:** Promotion is now explicit, auditable, and database-driven:
- `services/sector_ml_promotion.py` is the single source of truth for promoted sectors.
- A sector is promoted only when an approved, active `ModelRegistry` row is linked to a live `ResearchExperiment` row (`decision='promoted'`, `promotion_status='live'`).
- `delivery_gates.py` and `assembler.py` consult this registry via a runtime `promoted_sectors` set. File existence plays no role in the unblock decision.
- `scanner.py` refreshes the promoted set once per scan and caches it for the duration of the scan.

**Training discipline:**
- Sector models require ≥100 backtest trades (raised from 20).
- Purged expanding-window CV (3 folds) is required in addition to a 70/30 holdout.
- `scripts/train_backtest_ml.py` writes pending registry/experiment rows only; it does not activate the model.

**Promotion checklist (`scripts/promote_sector_model.py`):**
- OOS AUC ≥ 0.55
- Cost-adjusted Sharpe > 0
- Rollback plan documented
- Expiration date set
- Action logged in `ActionAuditLog`

**Tests:** `tests/test_delivery_gates.py` covers promoted/unblocked, expired re-block, and promotion-lookup fail-closed. `tests/test_train_sector_model.py` covers insufficient data, champion-beats save, pending registry record, promotion checklist, and rejection of sub-threshold models. All passing.

**Status:** The gate infrastructure is complete and tested. No sector model has been trained or promoted yet; actual unblocking requires ≥100 resolved backtest trades per sector and a successful QENG-1c promotion.

## Live-Quality Session — Calibration Was Silently Off, WR Is Sector-Concentrated (2026-06-15)

Four findings worth keeping, from a session that concluded the OHLCV/gate/calibration/universe tuning levers are spent.

**1. Calibration had been silently OFF (passthrough) — and the self-gate was the cause.** `run_calibration()` self-gates on Brier skill to avoid deploying a degenerate map that zeroes delivery (see the degenerate-map fix). But it judged skill on a **single temporal 80/20 split**, and the regime-shifted recent window made a genuinely-skilled map look no-skill (temporal Brier 0.282 > naive 0.25) → the *entire* map was rejected, calibration ran passthrough. Under shuffled **5-fold CV the same map clearly beats naive (0.244 < 0.25)**. Fix: gate on `_cv_brier()` (margin 0.002), keep temporal Brier as reference. Lesson: a one-shot temporal split is too noisy to gate a safety mechanism; CV is the honest skill test and still rejects degenerate maps.

**2. Live WR is sector-concentrated — it's a tech-MR strategy.** `gate_contribution_analysis.py` on 570 resolved: baseline **43.7% WR; XLK Technology (54.4%, N=180) is the ONLY sector >50%** (XLY 45, XLC 44, XLE 42, XLV 41, XLI 36, XLF 34, XLP 30). The 10-day price-level MR edge transfers to tech and almost nowhere else live. Chosen response (not hard blocks): **sector-specific calibration** — per-sector isotonic maps confidence to each sector's empirical WR, so weak sectors fall below the delivery floor naturally and the choice is data-driven + self-updating. Sector derived from `SECTOR_MAP` because ~81% of rows have a null `sector_etf`.

**3. §86/§92 cross-sectional shadow had accrued ZERO data since deployment (2026-06-09).** `_price_features` needs ≥253 daily bars (12-1 momentum `close.shift(252)`) but `scan_all` fetched `period="1y"` (≈251 bars) → `score_batch()` returned `{}` every scan → no signal ever tagged → the §92 150-signal gate was structurally unreachable. Fix: scan batch history `1y→2y`. A "deployed shadow" that silently collects nothing is worse than no shadow — always verify a forward-data pipeline actually writes rows.

**4. macOS `fork()` + network = permanent deadlock (cost two hung research runs).** Any fork-`Pool.map` of `process_ticker` that does a fresh download hangs at 0% CPU (SystemConfiguration proxy lookup isn't fork-safe). Pre-warming OHLCV isn't enough — `process_ticker` also fetches earnings. Robust fix for ad-hoc screens: **run the sim sequentially** (network in the main process is fine). `screen_universe_expansion.py` does main-process pre-warm + sequential sim.

**The quality-vs-volume tension (the real ceiling):** sector calibration + intraday safety + gates all gate MORE signals → fewer new-regime resolved signals → the calibration/§85-1/§92 audits accrue slower (Calib v5 at 12/200, ~16+ wks). Optimizing quality starves the validation that would prove the quality. Breaking this needs orthogonal data (paid) or a deliberate strategic narrowing to tech-MR — not more tuning.
