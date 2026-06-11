# Signal.Trade — Research Learnings & Alpha Inventory

> Living document. Updated as each research section completes.
> Last updated: 2026-06-11 after §96–§103 external research agenda. Key new findings: (1) **The live-vs-IS gap was mostly DELIVERY LEAKS, not signal** — clean book = 57.8% net WR, +2.06%/trade net. (2) Strategy is structurally a **VIX 20–30 stress-regime play** — 100% of 23yr backtest trades in that window; calm sleeve abandoned (0 trades). (3) Factor attribution confirms **genuine idiosyncratic alpha** (+0.87%/day, p=0.044). (4) WATCH bench all rejected — 111-name curated list is already well-filtered. (5) §87 L10 conviction sizing verified +0.06 Sharpe at ΔN=0, deployed live. (6) v10.9 canon **fails deflated Sharpe at honest 744 trials** — IS iteration is statistically spent. (7) **§96: 61% of alpha from overnight gaps** — validates close-slot timing. (8) **§97: limit-order entries fail deploy bar** across all k values — adverse selection dominates. (9) **§101: TSMOM sleeve Sharpe 0.57** on vanilla config — genuine diversifying premia, but 2015-22 fold 0.277 just misses 0.30 bar; correlation +0.27 vs MR book.
> Primary research script: `backend/scripts/signal_alpha_decomposition.py`
> Primary backtest: `backend/scripts/backtest_technicals.py`
> Live engine: `backend/services/signal_engine.py`

---

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

### Portfolio simulation (5 concurrent slots, T-bill on idle, compound DD)
| Metric | Baseline (flat) | §87 (sizing) | Δ |
|:---|---:|---:|---:|
| Portfolio CAGR | +3.6% | +3.7% | **+0.1pp** |
| Portfolio Ann.Sharpe | 2.87 | 3.03 | **+0.16 (+5.6%)** |
| Portfolio Max DD | -6.16% | -6.33% | -0.17pp |
| Skipped (slots full) | 21 (9.7%) | 21 (9.7%) | +0 |

**Verdict: DEPLOY with monitoring.**

- Sizing-only layer yields +0.16 portfolio ann.Sharpe (+5.6% relative) with zero trade-count cost.
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
