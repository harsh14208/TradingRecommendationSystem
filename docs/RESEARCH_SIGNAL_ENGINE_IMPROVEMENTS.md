# Research: Patents, Papers & Docs to Improve the Signal Engine

**Date:** 2026-07-14
**Scope:** Directional equity signal engine, options VRP sleeve, calibration, portfolio construction, and execution.
**Method:** Codebase audit + targeted literature/patent search.

---

## Executive Summary

The current Signal.Trade engine is a heavily-gated, additive-score mean-reversion system with a mature validation culture (gate ablation, isotonic calibration, shadow models, HRP allocation). After exhausting entry-alpha, exit-sweep, and price-factor IC (~0.28) improvements, four ideas survive the evidence×fit filter. These are listed first; the remainder of the note provides deeper prior art and additional longer-term directions.

**Priority order:**

1. **Portfolio-level volatility targeting** — strongest documented Sharpe lever not yet implemented.
2. **MAX-effect conditioning** — free OHLCV feature that materially changes short-term reversal returns.
3. **Limit-below-close entry execution** — directly attacks a measured entry-slippage leak.
4. **Regime-conditional model allocation** — patent-documented and fits existing HMM/cohort infrastructure.

The five longer-term improvement areas (regime detection, PIT data/survivorship bias, options VRP integration, cross-sectional alpha promotion, intraday microstructure/execution) follow in §6–§10.

---

## 1. Top Four Survivors (Start Here)

### 1.1 Portfolio-Level Volatility Targeting

**The idea.** Scale total gross exposure inversely to a forecast of portfolio-level volatility, while keeping the per-trade L-stack sizing logic unchanged. Your current system sizes individual trades but never targets portfolio vol; June's draw-up/draw-down was exactly the kind of high-vol-regime event this clips.

**Prior art.**

| Work | Type | Finding |
|------|------|---------|
| **Man Group, "The Impact of Volatility Targeting"** | Practitioner research | Vol targeting raises equity Sharpe from ~0.40 to 0.48–0.51; effect concentrated in equities and credit. |
| **Harvey et al. / CFA Digest** | Academic/practitioner summary | Confirms vol-scaling improves risk-adjusted returns; conditional variants stronger. |
| **Alpha Architect, "Conditional Volatility Targeting"** | Blog / research note | Shows vol targeting works best when conditioned on recent realized vol regime. |

**Fit to current code.** Implemented as `--vol-target [σ]` in `backtest_technicals.py --portfolio`.
- Causal 63-trade rolling realized vol of `net_pct` returns, annualized with √252.
- Exposure multiplier = σ_target / σ_forecast, clipped to [0.25, 2.0].
- Applied through the existing slot-size multiplier so individual signal scores and the L-stack are untouched.
- Default target is `VOL_REF_ANN = 0.25` (25% annualized).

**Prototype result (quick run, 15-ticker MR-only universe, 2003–2026).**

| Config | CAGR | Ann. Sharpe | Max DD |
|:---|---:|---:|---:|
| Baseline portfolio | +3.3% | 5.07 | -3.39% |
| Vol-target 25% | +2.8% | 4.94 | -1.50% |
| Δ | -0.5pp | -0.13 | +1.89pp |

> Avg size multiplier was 0.51× — the strategy's realized vol was roughly double the 25% target, so the target heavily de-risked the path. Risk-adjusted return (CAGR/MaxDD) improved from 0.97 to 1.87.

**Why it wins.** Largest documented effect; lowest implementation risk; no new data needed; directly addresses the June high-vol drawdown.

**Next step.** Run on the full (non-`--quick`) universe and test σ_target ∈ {0.10, 0.15, 0.20, 0.25} to find the risk-adjusted sweet spot. Also evaluate a VIX-conditioned variant where σ_forecast blends strategy realized vol with VIX level.

---

### 1.2 MAX-Effect Conditioning

**The idea.** Condition mean-reversion triggers on MAX, the maximum daily return over the past month. Lottery-like stocks (high MAX) exhibit much stronger short-term reversals than low-MAX stocks. MAX is a one-line OHLCV feature that fits naturally into the existing `quality_score` / L8 machinery.

**Prior art.**

| Work | Type | Finding |
|------|------|---------|
| **Chen et al., "Maxing Out Short-term Reversals" (SSRN)** | Working paper | Reversal returns are 1.66%/week in high-MAX stocks vs 0.65% in low-MAX stocks. |
| **Alpha Architect — volatility/turnover reversals** | Research note | Reversal effects concentrated in high-vol, high-turnover, lottery-like names. |
| **Turnover & 52-week-high conditioning** | Related literature | Reversal strongest after high turnover and 52-week-high events. |
| **Reversing the Trend of Short-Term Reversal** | Paper | Industry-relative residual reversal further de-noises raw return signals. |

**Fit to current code.** Testable in the existing harness. Implementation sketch:
- Add `MAX_21 = price.pct_change().rolling(21).max()` as a feature.
- Gate MR entry: require MAX_21 > high percentile (e.g., top tercile) to fire, or scale entry score monotonically with MAX.
- Optionally add **turnover conditioning**: only take MR signals when recent turnover is elevated.
- Optionally replace raw return triggers with **industry-relative residual return**: `ret - sector_etf_ret`, which de-noises the §63 z-score direction.

**Why it ranks second.** Free feature; large published spread; minimal code change; could improve per-signal IC without changing data infrastructure.

**Next step.** Add MAX_21 to `signal_engine.py` feature set and backtest the interaction with existing oversold conditions (RSI<42, BB%B<0.22, etc.).

---

### 1.3 Limit-Below-Close Entry Execution

**The idea.** Replace or supplement the current close-entry slot with a limit order placed below the prior close (entry − k×ATR). Intraday-pullback/limit entries dominate open entries for mean reversion, and the measured stop slippage (−0.86pp) shows the engine's edge lives partly in fill mechanics.

**Prior art.**

| Work | Type | Finding |
|------|------|---------|
| **Alvarez Quant Trading — MR entry comparison** | Practitioner research | Systematic comparison showing limit-on-pullback entries outperform open entries for mean-reversion strategies. |
| **Closing-auction research (arXiv)** | Paper | Provides fill-probability calibration for auction vs. limit orders. |
| **Cracking Markets (2026), "Intraday Breakout Details"** | Blog | Stop-entry vs. delayed limit-entry: limit entry becomes competitive when slippage > ~2 ticks/side. |

**Fit to current code.** The §96c close-entry slot is already half of this. Implementation sketch:
- For each EOD BUY signal, place a limit order at `close - k * ATR(14)` for the next session.
- Use fill-or-kill / day-order logic: if not filled by close, expire.
- Backtest with realistic slippage: assume fill at limit if intraday low ≤ limit, else no trade.
- Optimize k per style (intraday vs. swing) or use a fixed small k (e.g., 0.1–0.3 ATR).

**Why it ranks third.** Attacks a measured, quantified leak rather than adding new alpha; cheap to test; aligns with the documented mean-reversion edge.

**Next step.** Implement a `limit_entry_atr_fraction` parameter in the backtest harness and sweep k ∈ [0.05, 0.50] by style.

---

### 1.4 Regime-Conditional Model Allocation

**The idea.** Make cohort edges regime-conditioned by learning `(action, style, sector) × HMM-regime` expected-value cells. June-type regime breaks would then de-risk automatically instead of waiting for 20 resolved losses.

**Prior art.**

| Work | Type | Finding |
|------|------|---------|
| **US11410240B2 — López de Prado, "Tactical investment algorithms"** | Patent | Covers fitting regimes and allocating risk across prediction models by regime probability. Structurally matches your HMM + cohort-EV gate. |
| **Hamilton (1989)** | Seminal paper | Markov regime-switching foundation. |
| **Ang & Bekaert (2004)** | Paper | Regime-dependent asset allocation. |
| **Chaudhary (2026), "Multi-Scale Markov-Switching GARCH"** | arXiv paper | Triple-timeframe regime detection; 27-state probability tensor. |
| **Verma (2026), "Regime-Based Portfolio Allocation Using HMMs and RL"** | arXiv paper | HMM states + RL allocation with execution lag. |

**Fit to current code.** You already have HMM infrastructure and cohort EV tracking. Implementation sketch:
- Fit a daily macro HMM (VIX, MOVE, T10Y, credit spread, DXY, SPY trend) → 3 regimes.
- For each `(action, style, sector)` cohort, compute conditional EV and WR per HMM regime.
- Use regime-specific thresholds for score-to-confidence mapping and for max exposure.
- Patent note: US11410240B2 is active. Personal/internal use is generally fine; licensing the engine would require a freedom-to-operate review.

**Why it ranks fourth.** High fit to existing architecture, but requires more engineering than #1–#3 and is entangled with patent considerations.

**Next step.** Add HMM regime labels to the existing cohort analytics table and quantify EV divergence across regimes for the top 10 cohorts.

---

## 2. Immediate Roadmap

| Rank | Idea | Test location | Effort | Expected impact |
|------|------|---------------|--------|-----------------|
| 1 | Portfolio vol targeting | `backtest_technicals.py --portfolio` | Low | High (Sharpe +0.08–0.11 documented) |
| 2 | MAX-effect conditioning | Existing feature harness | Low | Medium (1.66% vs 0.65% weekly reversal spread) |
| 3 | Limit-below-close entry | Backtest execution layer | Low | Medium (closes −0.86pp slippage leak) |
| 4 | Regime-conditional allocation | Cohort analytics + HMM | Medium | High (tail-risk auto-de-risk) |

---

## 3. Longer-Term Improvement Areas

After the four survivors are tested, the following areas remain the next best leverage points.

### 3.1 Regime-Aware Signal Conditioning (broader)

**Why it matters.** The engine already runs ~32 risk gates, but most macro gates were ablated because they were static and harmful. A proper latent-regime classifier could replace ad-hoc VIX/MOVE caps and dynamically adjust score thresholds, position sizing, or even turn the engine off.

**Additional prior art.**

| Work | Type | Relevance |
|------|------|-----------|
| **Hamilton (1989), "A New Approach to the Economic Analysis of Nonstationary Time Series"** | Seminal paper | Introduces Markov regime-switching to econometrics. |
| **Ang & Bekaert (2004), "How Regimes Affect Asset Allocation"** | Paper | Two-regime international CAPM; state-dependent return moments. |
| **Wang, Lin & Mikhelson (2020), "Regime-Switching Factor Investing with Hidden Markov Models"** | Paper | HMM-driven factor timing; useful for toggling MR/momentum modes. |
| **Rundle & Medda (2019), "Macroeconomic Regime Identification using ICA and HMMs"** | SSRN paper | ICA + HMM recipe for combining many macro series. |
| **Chaudhary (2026), "Multi-Scale Markov-Switching GARCH"** | arXiv paper | Triple-timeframe MS-GARCH with 27-state probability tensor routed through Mixture-of-Experts. |
| **Verma (2026), "Regime-Based Portfolio Allocation Using HMMs and RL"** | arXiv paper | HMM states fed into RL allocation policy. |

**Actionable recommendations.**
- Build a daily macro HMM using VIX, MOVE, T10Y, credit spread (HY-IG), DXY, and SPY trend.
- Use state probabilities (not hard labels) to scale MR entry thresholds and max position size.
- Add an MS-GARCH micro layer for intraday vol forecasting around macro events.
- Fit the isotonic calibrator per regime, not pooled.

---

### 3.2 Point-in-Time Data & Survivorship Bias

**Why it matters.** Backtests rely on yfinance, which is not PIT and excludes delisted tickers. The project already flags this in `TODO.md` and the PBO analysis warns of overfit risk (PBO = 0.20).

**Prior art.**

| Work | Type | Relevance |
|------|------|-----------|
| **Bessembinder (2018), "Do Stocks Outperform Treasury Bills?"** | Paper | Most individual stocks underperform T-bills; ignoring delisted losers inflates backtests. |
| **Luo et al. (2014), Deutsche Bank "Seven Sins of Quantitative Investing"** | Practitioner report | Survivorship and look-ahead bias checklist. |
| **Bailey, Borwein, López de Prado & Zhu (2017), "The Probability of Backtest Overfitting"** | *J. Computational Finance* | PBO via CSCV; already in workflow. |
| **López de Prado, *Advances in Financial Machine Learning*** | Book | Purged CV, embargo, fractional differentiation, meta-labeling. |
| **Norgate Data / EODHD / WRDS CRSP-Compustat** | Data sources | PIT, survivorship-bias-free price and fundamentals. |

**Actionable recommendations.**
- Re-run the 23-year backtest on a PIT dataset including delisted names and historical constituents.
- Implement bitemporal tracking: every feature carries an `as-of` timestamp.
- Make CSCV/PBO a CI gate: PBO < 0.30 and Deflated Sharpe > 1.65 before promotion.
- Add a synthetic delisting-return model for dead tickers.

---

### 3.3 Options VRP Integration & Tail-Risk Management

**Why it matters.** Internal ORATS/Massive research found realized vol ≈ 0.72× implied, but the options sleeve is still standalone (`SELL_CASH_SEC_PUT`, etc.) and not integrated with directional sizing or tail hedging.

**Prior art.**

| Work | Type | Relevance |
|------|------|-----------|
| **Carr & Wu (2009), "Variance Risk Premiums"** | *Review of Financial Studies* | VRP = risk-neutral variance − physical realized variance. |
| **Bakshi & Kapadia (2003)** | *RFS* | Delta-hedged portfolios earn negative returns → positive VRP for sellers. |
| **Bollerslev, Tauchen & Zhou (2009)** | Paper | Aggregate VRP predicts equity returns. |
| **Goyal & Saretto (2009), "Cross-Section of Option Returns"** | Paper | HV-IV gap sorts produce significant single-stock option returns. |
| **Cao & Han (2013)** | *JFE* | Idiosyncratic vol negatively predicts delta-hedged call writing returns. |
| **Park (2013 Fed), "Volatility of Volatility and Tail Risk Premiums"** | FEDS paper | VVIX as tail-risk measure; spikes predict lower tail-hedge returns. |
| **Todorov (2018), "The Pricing of Tail Risk and the Equity Premium"** | Paper | Decomposes VRP into continuous/jump components. |
| **Vatanen (2025), "Harvesting VRP with Equity Index Options"** | Springer chapter | One-month ATM straddle + daily delta hedge; practical blueprint. |
| **Dörries, Korn & Power (2021)** | SSRN paper | Compares 7 VRP strategies across payoff, leverage, finite maturity. |
| **Brenner/Gastineau volatility instrument patent** | Patent | Check against existing claims if instrumentizing vol. |

**Actionable recommendations.**
- Integrate VRP as a sizing overlay: wide HV-IV gap + calm VVIX/VIX term → increase options allocation; spike → cut to zero.
- Add high-frequency realized vol (`rvol_hf`) from minute bars as a turbulence gate.
- Stress-test the short-vol sleeve through 2008/2020 with realistic bid-ask, gamma, assignment.
- Consider a tail-hedge sleeve: OTM SPY/QQQ put spreads + VIX calls sized to 1–3% annual premium.

---

### 3.4 Promoting Cross-Sectional Alpha to a Live Sleeve

**Why it matters.** The h=63 cross-sectional XGBoost passed promotion (net Sharpe +0.576, 90% CI excludes zero) but is only a bottom-decile sizing haircut.

**Prior art.**

| Work | Type | Relevance |
|------|------|-----------|
| **Gu, Kelly & Xiu (2020), "Empirical Asset Pricing via Machine Learning"** | *RFS* | Canonical ML cross-sectional returns paper. |
| **Chen, Pelger & Zhu (2024), "Deep Learning in Asset Pricing"** | *Management Science* | Autoencoder factor models. |
| **Freyberger, Neuhierl & Weber (2020)** | Paper | Nonparametric cross-sectional characteristic selection. |
| **Cremona et al. (2024), "Equity Market-Neutral Strategies using Variable Selection"** | Working paper | Ridge/lasso/elastic-net for ex-post beta neutrality. |
| **Du (2025), "Machine Learning Enhanced Multi-Factor Quantitative Trading"** | arXiv paper | 500–1000 factors, cross-sectional neutralization, PyTorch acceleration. |

**Actionable recommendations.**
- Run a dollar-neutral L/S book with the h=63 model: top decile long, bottom decile short, sector/beta neutralized.
- Use elastic-net beta neutralization at the portfolio level.
- Add adaptive neutralization strength: increase when cross-sectional dispersion or vol rises.
- Ensemble h=21 and h=63 models.
- Use the cross-sectional score to adjust directional confidence only when it does not contradict the MR signal.

---

### 3.5 Intraday Microstructure & Execution Quality

**Why it matters.** Live data shows the 11:00–12:00 ET window is catastrophic for WR, and EOD batch signals can be stale. The ATR-based cutoff was mis-calibrated.

**Prior art.**

| Work | Type | Relevance |
|------|------|-----------|
| **Wood, McInish & Ord (1985); Harris (1986)** | Papers | U-shaped intraday volatility/volume. |
| **Gao et al. (2018), "Intraday Momentum"** | Paper | First-half-hour return predicts last-half-hour return. |
| **Lunina (2011), "Intraday Dynamics of Stock Returns"** | Thesis | Lunch-hour decline in returns/volume/spreads. |
| **Almgren & Chriss (2000), "Optimal Execution of Portfolio Transactions"** | Seminal paper | Efficient frontier of cost vs. timing risk. |
| **Quantitative Brokers (2023)** | Practitioner doc | Microstructure regimes and intraday states. |

**Actionable recommendations.**
- Time-of-day gate: embargo new directional signals 11:00–12:00 ET unless intraday vol spikes.
- Use intraday realized vol and VWAP for dynamic ATR cutoff.
- Build a simple TCA/slippage model using spread, ADV, participation rate.
- Use delayed-limit entry for less liquid names; stop-entry only for highly liquid ETFs/index names.

---

## 4. Extending Existing Strengths

### 4.1 Hierarchical Risk Parity (HRP)
- **López de Prado (2016), "Building Diversified Portfolios that Outperform Out-of-Sample"** — canonical reference.
- **Next step:** Replace covariance input with a tail-dependence matrix (lower-tail correlation or FRM adjacency).

### 4.2 Isotonic Calibration
- **Zadrozny & Elkan (2001)** — isotonic calibration.
- **Jiang (2011), "Smooth Isotonic Regression"** — PCHIP alternative to step functions.
- **Next step:** Use smooth isotonic regression and report Brier/ECE per regime.

### 4.3 Probability of Backtest Overfitting (PBO)
- **Bailey et al. (2017)** — PBO via CSCV.
- **López de Prado's Deflated Sharpe Ratio** — multiple-trials adjustment.
- **Next step:** Run PBO per signal family and on the full blended engine.

---

## 5. Suggested Reading Order

1. **Vol targeting:** Man Group paper → Harvey et al. / CFA Digest → Alpha Architect conditional variant.
2. **MAX effect:** Chen et al. "Maxing Out Short-term Reversals" → Alpha Architect turnover/vol reversal notes.
3. **Entry execution:** Alvarez Quant Trading → Cracking Markets → closing-auction arXiv paper.
4. **Regime allocation:** US11410240B2 → Hamilton (1989) → Ang & Bekaert (2004) → Chaudhary MS-GARCH (2026).
5. **Cross-sectional ML:** Gu, Kelly & Xiu (2020) → Cremona EMN (2024).
6. **VRP:** Carr & Wu (2009) → Goyal & Saretto (2009) → Park VVIX (2013).
7. **Data bias:** Bessembinder (2018) → Luo et al. "Seven Sins" → Bailey et al. PBO (2017).

---

## 6. Immediate Next Steps (in priority order)

1. **Prototype portfolio vol-targeting** in `backtest_technicals.py --portfolio`.
2. **Add MAX_21** to the feature set and test interaction with existing oversold conditions.
3. **Implement limit-below-close entry** with ATR fraction sweep.
4. **Add HMM regime labels** to cohort analytics and quantify EV divergence.
5. Source a PIT survivorship-bias-free dataset and re-run the full backtest.
6. Integrate VRP as a sizing overlay using HV-IV gap + VVIX/VIX term structure.
7. Promote h=63 cross-sectional model to a beta-neutral L/S sleeve or confidence modifier.
8. Add midday entry embargo and dynamic ATR/slippage calibration.
9. Re-run CSCV/PBO and Deflated Sharpe after each major change.

---

## 7. References (Links)

- Man Group — Impact of Volatility Targeting: search "Man Group volatility targeting impact"
- Alpha Architect — Conditional Volatility Targeting: https://alphaarchitect.com
- Chen et al., "Maxing Out Short-term Reversals": https://papers.ssrn.com/sol3/papers.cfm?abstract_id=...
- Alvarez Quant Trading — MR entry comparison: https://alvarezquanttrading.com
- US11410240B2: https://patents.google.com/patent/US11410240B2
- Carr & Wu variance risk premium summary: https://flashalpha.com/articles/variance-risk-premium-vs-volatility-risk-premium-difference
- Goyal & Saretto discussion: https://www.sciencedirect.com/science/article/abs/pii/S0304405X12002450
- Bailey et al. PBO: https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf
- López de Prado publications: https://www.quantresearch.org/Publications.htm
- HRP original: https://quantpedia.com/hierarchical-risk-parity/
- Almgren & Chriss summary: https://zhuanlan.zhihu.com/p/574492685
- QB microstructure regimes: https://thehedgefundjournal.com/qb-a-new-era-in-quantitative-execution-microstructure-regimes/
- MS-GARCH 2026: https://arxiv.org/abs/2606.06190
- HMM+RL regime allocation 2026: https://arxiv.org/abs/2605.27848
- Gu, Kelly & Xiu (2020): https://dachxiu.chicagobooth.edu/download/ML.pdf
- Park Fed VVIX paper: https://www.federalreserve.gov/econres/feds/volatility-of-volatility-and-tail-risk-premiums.htm
- Dörries et al. VRP strategies: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3989529
- Cremona EMN variable selection: https://chairefintech.uqam.ca/wp-content/uploads/2024/11/Cahier_recherche_Severino_compressed.pdf
- Du cross-sectional ML: https://arxiv.org/abs/2507.07107
