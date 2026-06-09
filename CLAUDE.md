# CLAUDE.md — TradingRecommendationSystem

## Environment

- **Python version:** 3.11 (matches CI — `actions/setup-python@v5` with `python-version: "3.11"`)
- **Virtual env:** `backend/venv/` — always activate before running Python commands
- **Working directory for all backend commands:** `backend/`

## Commands

```bash
# Tests
cd backend && pytest tests/ -x -q --timeout=30

# Lint (must pass before commit)
ruff check backend/ --config ruff.toml
ruff format backend/ --config ruff.toml --check

# Security audit
pip-audit -r backend/requirements.txt --ignore-vuln PYSEC-2022-42969

# Backtest (takes ~3 min)
cd backend && python scripts/backtest_technicals.py
cd backend && python scripts/backtest_technicals.py --oos

# §QuantEngine research flags (combinable, each adds ~1 min)
cd backend && python scripts/backtest_technicals.py --beta-hedge      # strip beta: IS 0.29→0.12 pure alpha
cd backend && python scripts/backtest_technicals.py --forecast-sizing # Carver FDM: +0.04 Sharpe
cd backend && python scripts/backtest_technicals.py --portfolio        # concurrent portfolio CAGR+MaxDD
cd backend && python scripts/backtest_technicals.py --walk-forward     # BUY_THRESH OOS re-select (WF avg 0.455)
cd backend && python scripts/backtest_technicals.py --inv2             # VIX<20 gate ablation (2022-present epoch)
cd backend && python scripts/backtest_technicals.py --inv5             # legacy ablation flag (§59/§60/§61/§78 removed 2026-06-02; use --validate-live-gates instead)
cd backend && python scripts/backtest_technicals.py --exit-sweep --sequential  # grid over exit knobs (max_loss_days × no_progress); ranks by capital-aware portfolio ANN Sharpe. RESULT 2026-06-08: no real edge — top-ANN config (np=3) is a turnover artifact (CAGR flat 3.4 vs 3.3, WR 67→56%); max_loss=OFF dominates on every robust axis but within 1 SE of baseline. Exit lever exhausted; confirms OHLCV+macro structural ceiling.
# §Inv-B quality_score tier analysis runs automatically in every IS backtest (no flag needed)
# §Inv-C L8 quality_score-weighted sizing validation runs automatically after §Inv-B
cd backend && python scripts/backtest_technicals.py --quality-sweep  # 14-config entry quality gate sweep
cd backend && python scripts/backtest_technicals.py --validate-live-gates  # ablate all testable live engine gates (~15 min); skips IS stats for speed; results in docs/SIGNAL_VALIDATION.md

# Tier-3 signal validation
cd backend && python scripts/backtest_edgar.py           # EDGAR: §50 Piotroski, §73 Insider (~10 min first run, §76 Altman removed); cached to data/edgar_fundamentals.pkl
cd backend && python scripts/backtest_edgar.py --cached  # use cached EDGAR data (~3 min)
cd backend && python scripts/backtest_edgar.py --ticker NVDA  # debug single ticker
# §63 Sector cointegration runs automatically in every IS backtest (no flag needed)
# --validate-live-gates now includes §63 cointegration ablation in the REMOVE section

# Gate contribution + §85-1 fundamental modifier audit
cd backend && python scripts/gate_contribution_analysis.py                        # A5: all gates, full report
cd backend && python scripts/gate_contribution_analysis.py --section85 --after 2026-06-01  # §85-1: fundamentals only (needs ≥200 resolved signals)

# Frontend build (A8 complete — bundle pre-built in dist/)
node build.mjs                                                         # rebuild after JSX changes
# Or: .venv_test_cov/lib/python3.14/site-packages/playwright/driver/node build.mjs (no npm needed)

# Russell 1000 screener
cd backend && python scripts/screen_russell1000_mr_candidates.py --fast   # 2006-2016 only (~2hr)
cd backend && python scripts/screen_russell1000_mr_candidates.py          # full 23yr (~4hr)

# Russell 2000 screener (small-cap; pass rate 0.2% vs R1000 1.6% — large-cap quality essential)
cd backend && python scripts/screen_russell2000_mr_candidates.py --fast   # 2006-2016 only (~4hr, 467 tickers)
cd backend && python scripts/screen_russell2000_mr_candidates.py          # full 23yr (~8hr)
cd backend && python scripts/screen_russell2000_mr_candidates.py --adv 20 # raise ADV floor to $20M

# Cross-sectional MR amenability model (universe expansion decisions)
cd backend && python scripts/cross_sectional_mr_screen.py                 # IS analysis + ranked scores
cd backend && python scripts/cross_sectional_mr_screen.py --oos-validate  # + OOS validation on HELD_OUT_TICKERS

# §86 Market-neutral cross-sectional alpha model (Qlib-style ranking; research artifact — see Research baseline)
cd backend && python scripts/cross_sectional_alpha_model.py                                   # single chronological split
cd backend && python scripts/cross_sectional_alpha_model.py --walk-forward --cost-sweep       # purged expanding-window CV + bootstrap Sharpe CI + cost curve
cd backend && python scripts/cross_sectional_alpha_model.py --universe curated                # restrict to backtest_technicals.TICKERS (the edge-bearing IS set); 'full' = complete S&P 500
cd backend && python scripts/cross_sectional_alpha_model.py --short-interest                  # add SI level+velocity features (Postgres short_interest_biweekly, 2017-12+)
cd backend && python scripts/cross_sectional_alpha_model.py --exit-decile 0.25                # Qlib TopkDropout hold-until-dropout hysteresis (turnover lever)
cd backend && python scripts/cross_sectional_alpha_model.py --horizon 25                       # lower-drawdown variant (net +0.32, MaxDD -24.7%); default is now 21 (~monthly)
cd backend && python scripts/cross_sectional_alpha_model.py --wq-alphas                        # add orthogonal WorldQuant-101 alphas (wq002/wq026); helps ONLY at h=5, hurts at h=21 — leave off
cd backend && python scripts/fetch_sp500_ohlcv.py                                             # backfill full S&P 500 OHLCV cache (membership: data/sp500_ticker_start_end.csv from fja05680/sp500)

# Hold-period research
cd backend && python scripts/backtest_technicals.py --hold 5   # test 5-day hold (confirmed worse: Sh 0.27 vs 0.31)

# Confidence recalibration
cd backend && python scripts/backfill_confidence.py --check          # readiness + current Brier
cd backend && python scripts/backfill_confidence.py --force --apply  # recalibrate on all resolved signals

# Phantom win fix (auto-runs nightly, manual trigger:)
cd backend && python validate_predictions.py --fix-phantoms --apply

# Alembic migrations
cd backend && alembic upgrade head
```

## Architecture

```
backend/
  main.py              # FastAPI app, router mounts, lifespan
  database.py          # SQLAlchemy async engine, session factory
  config.py            # Pydantic settings (loads .env)
  routers/             # HTTP endpoints (signals, quotes, auth, billing, …)
  services/
    signal_engine.py   # Orchestration — generate_signal() + scan_all(); re-exports engines/ helpers
    engines/           # BE-1 decomposition (helpers ← assembler ← signal_engine)
      helpers.py       #   leaf constants + _levels/_score_to_action/_current_session/_make_plain_english
      assembler.py     #   _assemble_signal() — risk gates, calibration, final signal dict
    signal_workers.py  # *_worker async tasks (news/fundamentals/options/institutional/sentiment)
    signal_scoring.py  # technical family scorers (oscillators/macd/ema/obv-adx/MAs)
    signal_ml.py       # XGBoost champion/challenger gate
    scanner.py         # Async market scanner loop
    market_data.py     # OHLCV cache (Redis → in-memory fallback)
    polygon_client.py  # Polygon REST + extended-hours snapshot
    delivery_gates.py  # Sector/session/volatility filters
    macro.py           # VIX, STLFSI4, SPY trend
  tests/               # pytest suite (~1636 tests)
  scripts/
    backtest_technicals.py  # 23-year MR backtest + OOS validation
    train_backtest_ml.py    # Train entry model on IS backtest outcomes
    eval_ml.py              # Evaluate both models (§1-§8)
```

## Key constants

| Constant | Value | File |
|---|---|---|
| `BUY_THRESH` | 50 | `backtest_technicals.py` |
| `HOLD_DAYS` | 10 | `backtest_technicals.py` |
| `FRICTION` | 0.5% round-trip | `backtest_technicals.py` |
| MR gate | BB%B<0.22 OR IBS<0.15 OR VWAP%<−0.75% | `signal_engine.py` (RSI removed §40) |
| Stop swing (ATR) | 1.5s/2.0t universal | `atr_levels()` / `_levels()` (§17: +0.03 Sharpe, +5.6pp WR vs 1.0s; ADX>35 branch removed from backtest to match live) |
| OSC weight | 1.0 | `signal_engine.py:3170` — (osc_capped ± mr_capped) × 0.85; each family capped ±18 within combined bucket. Backtest uses separate OSC ±25×1.0 and MR ±18×1.0 (technical-only calibration — live engine has 50+ extra families that raise scores, so cap values differ). |
| MR weight | 1.0 (backtest) / 0.85 (live combined) | `backtest_technicals.py` (separate MR family) vs `signal_engine.py:3170` (combined stretched-price bucket with OSC) |
| Sector HARD_LIMIT | 30% | `signal_engine.py` (was 50%, tightened §43) |
| Sector SOFT_LIMIT | 20% | `signal_engine.py` (was 30%, tightened §43) |
| Scanner semaphore | 8 per worker | `signal_engine.py:scan_all()` (was 15, §43 DB pool fix) |
| Swing floor | **46%** confidence | `delivery_gates.py:STYLE_CONF_FLOORS` (recalibrated 70→46 post phantom-win correction 2026-05-31) |
| min_confidence | **40%** | `config.py` (recalibrated 57→40 — honest scale after phantom-win correction) |
| BLOCKED_TICKERS | LRCX/MRVL/AMAT/KLAC/STT/MTB/**APH** | `delivery_gates.py` (APH added 2026-05-31: N=4, 0% WR, −8.70%) |
| §77 Tax-Loss | **−4pp penalty** | `gates/calendar.py` (inverted: live WR 31% near 52-wk low, was +4pp) |
| §75 Buyback boost | **disabled** | `signal_engine.py` (live WR 33.8%, −8.7pp drag) |
| positionSizeScale | L1×…×L8 (L9 bear removed) | `signal_engine.py` (L4=(conf−40)/14+0.5 clamped [0.5,1.5]; L7=raw-score Kelly ±15% +0.03Sh; L8=quality_score ≥43→1.30×/35–43→1.0×/<35→0.75× +0.06Sh; L9 bear dampener removed — bear WR=72%>baseline) |
| ATR≤70 research finding | Backtest-only (not live gate) | IS sweep: +0.05 Sharpe but N 197→98 (−50%). Ann.Sharpe DROPS: 0.95→0.78 (N reduction dominates). Keep for research reference; do not apply as live delivery gate. |
| Entry model OOS AUC | 0.6399 (champion) | `data/backtest_ml_features.json` (14 tech features, 23yr IS) |
| Entry model CV-AUC | 0.6188 ± 0.1261 | purged expanding-window CV (K=5, embargo=20d) |
| Min N for live model deploy | 300 | `signal_ml.py:_MIN_LIVE_N_FOR_DEPLOYMENT` (Hanley-McNeil CI justification) |
| Min AUC delta to deploy | 0.005 | `signal_ml.py:_MIN_AUC_DELTA_TO_DEPLOY` |
| Dual model blend | ratio = avg(model_probs) / (base_conf/100 × 0.85), clamped [0.75, 1.25]; final = base_conf × ratio | `signal_ml.py:blend_confidence()` |
| §63 cointegration ADF gate | residual ADF p < 0.10 required (Engle-Granger step 2) | `technicals.py:_COINT_ADF_PMAX` (live, unconditional); `backtest_technicals.py:_COINT_REQUIRE_STATIONARY` (toggle). Added 2026-06-09 — non-cointegrated pairs now return `coint_z=None`/NaN. statsmodels `adfuller`/`coint`. |
| Macro regime HMM | `hmmlearn.GaussianHMM` (2-state, full cov, sticky prior) | `macro_regime.py` — replaced hand-rolled Baum-Welch/Viterbi 2026-06-09; same public contract (`get_macro_regime()`). |

## CI

File: `.github/workflows/ci.yml`
Steps: install deps → syntax check → import smoke → pytest → accuracy gate → pip-audit → ruff

**CI Python is 3.11.** Local Python is 3.14. Never use syntax that requires 3.12+:
- ❌ Backslashes inside f-string `{}` expressions
- ❌ `match` statements without `# type: ignore` if targeting 3.10

`ruff.toml` sets `target-version = "py311"` — run `ruff check` locally to catch these before push.

## Research baseline (§59–§83 + gate validation + EDGAR Tier-3 as of 2026-06-03)

All §47–§83 implemented. **v10.7 (2026-06-09, awesome-quant library audit):** Two hand-rolled algorithms replaced with battle-tested libraries (numpy-1.26 safe; +`statsmodels`/`hmmlearn`/`arch` to requirements). (1) **§63 cointegration ADF gate** — added the missing Engle-Granger step 2 (residual ADF stationarity test, p<0.10) to `technicals.py` (live, unconditional) and `backtest_technicals.py` (`_COINT_REQUIRE_STATIONARY` toggle). Was a correctness bug: §63 awarded +4pp on non-cointegrated (spurious-regression) pairs. Before/after on identical survivorship-corrected code: gate OFF (old) N=189/Sh=0.27 → gate ON (new) **N=205/Sh=0.23** (both clear Lo-CI + deflated-SR). The −0.04 IS Sharpe is the §76-Altman pattern again — the ungated edge was partly a spurious artifact acting as an incidental quality filter; gate kept for correctness/OOS-robustness. (2) **Macro regime HMM → `hmmlearn.GaussianHMM`** — replaced ~150 lines of hand-rolled Baum-Welch/forward-backward/Viterbi in `macro_regime.py`; identical public contract, fixed random_state removes label-switching risk in `hmm_bull_prob`/`hmm_trans_risk` meta-label features. Also wired `arch` GARCH(1,1) forward-vol as opt-in triple-barrier widths (`train_metalabel_model.py --barriers garch`; ablation ΔAUC≈0, default stays ATR). Research prototypes in `backend/scripts/research/` (skfolio HRP, alphalens IC — isolated env, numpy-2.x). **v10.6 (2026-06-09):** S&P 500 survivorship-bias correction enforced (point-in-time constituents from fja05680/sp500.git) — trims universe to historically-valid members; IS N=189, Sh=0.27 (higher quality than uncorrected v10.5). Also fixed a broken `--oos`/`--full-universe` path: `process_ticker` was refactored to return scored indicator frames instead of trades, but `run_oos_validation`/`run_full_universe_curation_bias` still unpacked the old tuple order and skipped `simulate_ticker` — they now call `simulate_ticker` on each frame. **v10.5 (2026-06-03):** §63 sector cointegration added to IS backtest scoring (rolling 252d Engle-Granger coint_z); §76 Altman removed from live engine (74% false-positive rate); dead gate cleanup complete; IS N=230, Sh=0.20. **v10.3 (2026-06-02, math-audit fixes):** ADX>35 ATR branch removed; Hurst window 63→64 bars; portfolio ann.Sharpe denominators fixed. **v10.2/v10.1:** ATR≤70 REVERTED, L9 removed, L8 quality_score recalibrated. Backtest canon (v10.7, 2026-06-09):

| Universe | N | WR | Avg Ret | Sharpe | MC P5 | 95% CI |
|---|---|---|---|---|---|---|
| **IS (v10.7, §63 ADF cointegration gate, 2026-06-09)** | **205** | **67.8%** | **+0.80%** | **0.23** | **0.12** ✅ | **[0.09, 0.36] ✅** |
| IS (v10.6, survivorship-corrected, §63 ungated, 2026-06-09) | 189 | 69.8% | +0.97% | 0.27 | 0.17 ✅ | [0.13, 0.42] ✅ |
| IS L7 / L8 sizing (v10.6, each +0.03) | 189 | ~71% | — | **0.31** | — | — |
| IS sector-filtered (live-equivalent, v10.6) | 183 | 70.5% | — | **0.29** | — | — |
| **OOS CLEAN (ex live-blocked, v10.6)** | **91** | **62.6%** | **+0.50%** | **0.13** ⚠ | — | **[−0.07, 0.34] ⚠** |
| OOS ALL (incl. blocked, v10.6) | 105 | 58.1% | +0.16% | 0.04 | — | [−0.15, 0.23] |
| Curation gap (IS sector-filt 0.24 − OOS clean 0.13, v10.6) | — | — | — | **0.11** | — | — |
| IS (v10.5, 107 tickers, 2026-06-03 — §63 coint + dead gate cleanup) | 230 | 66.1% | — | 0.20 | — | — |
| IS (v10.4, 107 tickers, 2026-06-02 — dead gates removed, §59/§60 not yet restored) | 241 | 65.6% | — | 0.19 | — | — |
| **IS (v10.3, 107 tickers, 2026-06-02)** | **217** | **68.2%** | **+0.88%** | **0.24** | **0.14** ✅ | **[0.11, 0.38] ✅** |
| IS L7+L8 combined sizing (§Inv2+§Inv-C, v10.3) | 217 | 70.1% | +0.96% | **0.28** | — | — |
| IS L7 score-weighted only (§Inv2, v10.3) | 217 | 69.4% | +0.92% | 0.26 | — | — |
| IS L8 quality_score-weighted only (§Inv-C, v10.3) | 217 | 70.1% | +0.96% | 0.28 | — | — |
| IS quality High tier (top tercile quality_score ≥44, v10.3) | 72 | 75.0% | +1.06% | **0.33** | — | — |
| IS quality Low tier (bottom tercile quality_score <37, v10.3) | 72 | 61.1% | +0.44% | 0.11 | — | — |
| **IS sector-filtered (live-equivalent, KO/PG removed, v10.3)** | **212** | **68.9%** | **+0.93%** | **0.26** | — | — |
| **OOS CLEAN (63 tickers ex-blocked, v10.3)** | **87** | **64.4%** | **+0.61%** | **0.15** | ⚠ | **[−0.06, +0.37] ⚠** |
| OOS ALL (63 tickers incl. blocked, v10.3) | 102 | 58.8% | +0.19% | 0.05 | ⚠ | [−0.15, +0.24] |
| Curation gap (IS − OOS CLEAN Sharpe, v10.3) | — | — | — | **0.09** ✅ | — | — |
| IS (v10.0, 107 tickers, 2026-06-01 — pre-ATR-fix) | 188 | 70.7% | +1.12% | 0.31 | 0.20 | [0.17, 0.46] |
| OOS v6 CLEAN (pre-v10.3, 41 tickers ex-blocked) | 51 | 62.7% | +0.62% | 0.16 | ⚠ | [−0.12, +0.44] |
| IS (v9.0, 100 tickers — dead gates removed 2026-05-31) | 173 | 70.5% | +1.06% | 0.29 | 0.16 | [0.13, 0.44] |
| IS (§46 pre-agenda baseline) | 126 | 60.3% | +0.68% | 0.18 | 0.04 | — |

**IS v10.1 (2026-06-01):** L8 quality_score sizing calibrated to IS p67/p33 (thresholds 43/35). §Inv-C: L8 alone +0.06 Sharpe (Sh 0.31→0.37, N=188, WR 70.7%→73.8%). L7+L8 combined: IS effective Sharpe ≈ **0.37** (zero N reduction). Quality gate sweep: ATR≤70 gives +0.05 IS Sharpe but N drops 50% → ann.Sharpe FALLS; not deployed as live gate. AI-theme tickers (AAOI, COHR, LITE, MXL, SIMO) — all FAIL (momentum stocks incompatible with 10d MR VIX gate). R2000 screened (1/440 PASS = 0.2% vs R1000 1.6% — large-cap quality essential). OOS v7+v8 pre-specified (15 total tickers).

**IS v10.0 (2026-06-01):** N=188 (was 173 — +MCO/HAL + sector map fix unlocking correct blocked-sector filtering). MC P5=0.20 (↑ from 0.16). SR=0 outside 95% CI at N=188 ✅. quality_score discrimination: High tier Sh=0.51 vs Low tier Sh=0.17 — spread +0.34. Deflated Sharpe 0.31 > data-mining expectation 0.20 ✅. L7 score-weighted sizing adds +0.03 Sharpe → 0.34, live in signal_engine.py.

**Sector filter corrected (2026-06-01):** _BLOCKED_SECTORS in backtest was incorrectly set to {XLI, XLV, XLE, XLRE, XLU} — removed 21 tickers from §10 comparison. Actual delivery_gates.py only blocks {XLF, XLP, XLU}. Fixed to {XLP, XLU, XLRE}: §10 now removes only KO/PG (XLP Consumer Staples). XLV/XLI/XLE stocks are live-eligible. IS sector-filtered (correct): N=185, WR=71.4%, Sharpe=0.33.

**Cross-sectional amenability model (2026-06-01):** OLS on 86 IS tickers, R²=0.235. Statistically significant predictors: sect_consumer t=+2.37**, sect_health t=+2.12** (SURPRISE — large-cap health = sentiment/rate MR, not FDA binary), sect_tech t=+1.59*. Healthcare confirmed live-eligible and moved to _MR_SECTORS in screen_russell1000_mr_candidates.py. OOS validation: r=0.355 ✅ — top-15 predicted OOS Sharpe=0.36 vs bottom-15 Sharpe=0.15. Run `python scripts/cross_sectional_mr_screen.py --oos-validate` to evaluate any new universe candidate.

**OOS v6 (2026-05-31):** CLEAN N=51, Sharpe=0.16, curation gap −0.08 (smallest ever ✅). SR=0 still inside CI at N=51.

**§QuantEngine decomposition (2026-05-31):** Beta hedge strips IS Sharpe 0.29→0.12 (pure MR alpha). Phantom wins corrected (88 signals + 112 outcome_14d) → live WR 42.5%, live Sharpe 1.32. Calibration v4 (2026-06-01): Brier 0.2641, 18,656 signals updated avg −1pp, all signals now <55% confidence (min_confidence=40%). Cal v3 val-Brier was 0.2432; v4 uses pre-A19 data — next recal after ≥50 post-A19 resolved signals. Portfolio CAGR +1.1%/yr; concurrent MaxDD −7.06%. **Honest forward Sharpe: 0.13–0.18** (v10.6 survivorship-corrected IS baseline N=189, Sh=0.27; with L7/L8 sizing ~0.31; OOS CLEAN N=91 Sh=0.13 confirms the haircut — midpoint ~0.15. Technical gate ceiling confirmed: pure OHLCV+macro path tops out at IS ~0.28 without external alpha data. v10.4 lesson: individual gate ablation ΔSh≈0 does not mean zero combined effect — §59/§60 restored after v10.4 regression showed 24 marginal trades hurt aggregate WR).

**Russell 1000 screener + §31 validation (2026-06-01):** MCO added (N=3, WR=66.7%, XLF live-eligible). HAL added (N=2, WR=100%, XLE research-only). PASS (fast mode, 2006-2016): GOOGL (Alphabet duplicate of GOOG — skip), AMP (already in IS — skip). No new IS additions from fast screen. Healthcare now moved to _MR_SECTORS (was _RESEARCH_ONLY_SECTORS) in screener — cross-sectional model confirmed t=+2.12**. OOS v7 pre-specified 2026-06-01 (see below).

**OOS v7 pre-specified (2026-06-01):** 10 tickers locked before any IS research. Amenability-model screened: healthcare/consumer/tech emphasis. See HELD_OUT_TICKERS in backtest_technicals.py (v7 block). Sectors: XLV healthcare (SYK, RMD, IDXX, ZBH), XLY consumer (RL, DECK, POOL), XLF exchange operators (NDAQ, CBOE, BR). Never mentioned in any prior IS research or backtest comment. Run `--oos` after ≥30 new live trades to evaluate.

**OOS v8 pre-specified (2026-06-01, Russell 2000 screener):** 5 tickers from R2000 fast-mode screen. R2000 pass rate: 1/440 (0.2%) vs R1000 1.6% — confirms large-cap quality essential for 10d MR. LNC (PASS: N=11, WR=73%, Sh=0.76); AMG, PAYC, SIG, AEO (WATCH: WR≥75%, N=4-8). Excluded data artifacts: BILL/FND (IPO post-2016), GAP (ticker ambiguity). Total HELD_OUT_TICKERS: 63.

**§86 Market-neutral cross-sectional alpha model (2026-06-09, `scripts/cross_sectional_alpha_model.py`):** Qlib-style daily cross-sectional ranking → dollar-neutral top/bottom decile L/S, target = 5d forward return minus cross-sectional mean. Built to break the ~0.28 ceiling via beta-neutrality; CONCLUSION: **ceiling is IC/data-bound, not architecture-bound.** Curated IS universe (110 names) WF net Sharpe ≈ 0.0–0.42 (mean IC ~0.011–0.016). Confirmed dead-ends, each validated per-fold (aggregate numbers repeatedly sold false dawns the per-fold view killed): (1) **Full S&P 500 expansion HURT** — net 0.42→−0.02; pulled in recycled/delisted tickers (free-yfinance maps historical symbols to today's owners → spurious ±1000% prints; needed ±50% `FWD_RET_CAP` winsorizer) + signal dilution + turnover rise. Irreducible without paid PIT security master (§84). (2) **Qlib TopkDropout** (`--exit-decile`) couldn't cut turnover — hysteresis only helps when rankings persist; at IC~0.013 they re-randomize every 5d. (3) **Short-interest velocity** (`--short-interest`) aggregate net −0.05→+0.26 was a single 2025-squeeze fold; worse in 5/9 folds; SI ranks below all price features. Harness is reusable for any new signal: survivorship-free universe, purged walk-forward CV, block-bootstrap Sharpe CI, cost-sensitivity sweep, per-fold stability. Only real levers left: new ORTHOGONAL data (§62 options-IV/flow) or accept honest ~0.2–0.4. See docs/TODO.md §86 for full step log.

**§86 update (2026-06-09, WorldQuant-101 + horizon sweep — first robustly net-positive config):** Screened 30 WQ-101 alphas via alphalens IC (`scripts/research/exp4_wq101_ic.py`); only **wq002/wq026** are orthogonal to the 8 RAW_FEATURE_COLS (max|corr|~0.2, `exp5_orthogonality.py`) and add *free* IC at h=5 (+0.04 gross Sharpe, +10% IC, turnover-neutral) — but the book stays net-negative. Root cause is **annual turnover cost, not IC.** The **horizon sweep** (new `--horizon` flag) takes full-universe WF **net Sharpe −0.058 (h=5) → +0.061 (h=10) → +0.347 (h=21)**, cost-robust to 20bps one-way (+0.234) and only break-even at 40bps, 11/15 folds net-positive, MaxDD −31%. Mechanism: per-rebalance turnover is flat (~1.34) but ~12 rebalances/yr vs ~50 cuts total cost drag ~4×. **DEFAULT `HORIZON` raised 5→21 (~monthly).** `--horizon 25` is a lower-drawdown variant (net +0.32, MaxDD −24.7%). Short-horizon WQ alphas decay and HURT at h=21 (net 0.347→0.214) → `--wq-alphas` stays OFF. Caveat: 90% CI grazes 0 ([−0.06, +0.76]) and mean IC at h=21 is tiny (~0.002) — the edge is **cost-structure-driven, not IC-driven**; more Sharpe needs genuine monthly-horizon IC = non-price/fundamental alpha (OpenBB/SimFin §62-style), not more price factors.

**Live ML retrain status (2026-06-09):** N≥300 deploy threshold reached (566 resolved signals: 495 BUY / 71 SELL, 101 tickers). `train_model()` run: OOS AUC 0.6872 (95% CI [0.607,0.767]) vs champion 0.6883 → **rejected** (Δ−0.0011 < +0.005 required); champion kept, live model untouched. Top features structural (`has_fundamentals_source`/`target_pct`/`n_rationale`), not alpha. Caveat: all 566 in one ~7-week window → effective independent N ≪ 566, Δ in noise. Auto-retrain already live: `_weekly_ml_retrain` (main.py:588) Sun 11am ET, same self-gating `train_model()` — promotes a challenger only on ≥0.005 AUC beat. No manual action needed.

**Gate changes (2026-05-31):**
- §77 Tax-Loss: inverted from +4pp boost → −4pp penalty (live WR 31% near 52-wk low)
- §75 Buyback: score boost removed (live WR 33.8%, −8.7pp drag)

**Gate removals (2026-06-02, --validate-live-gates validation):**
- §59 OU halflife scoring modifier — removed from `gates/statistical.py` (dead as scoring gate; hard block RESTORED to backtest 2026-06-03 — see below)
- §60 Hurst ceiling scoring modifier — removed from `gates/statistical.py` (same; hard block RESTORED to backtest 2026-06-03)
- **§76 Altman Z-Score — removed from `gates/fundamentals.py` (2026-06-03)**. EDGAR validation: 79/106 IS tickers (74%) permanently below Z'<1.23 — structural reasons (financial sector leverage model, tech goodwill/intangibles, Altman calibrated on 1968 manufacturing only). Was penalising ~80% of signals by -15 pts. The apparent +0.12 Sh gain in §50+§76 backtest combo was equivalent to raising BUY_THRESH from 50→55 (Altman's false positives accidentally create a quality filter, not genuine distress detection). Removed.
- §61 Idio vol hard block — removed from backtest and `gates/statistical.py` (ΔSh=0.00, +0N — dead)
- §78 Sep/Oct score floor — removed from backtest (ΔSh=0.00, +0N — dead at 100-ticker scale)
- §47 VIX3M hard block (Gate 27) — rejected before live deploy (ΔSh=−0.08, −50N — harmful)
- §67 FOMC day block — removed from backtest (ΔSh=0.00, +4N); kept in `delivery_gates.py` for live
- §64+§68 T10Y sector penalties — removed from backtest (ΔSh=0.00, +1N); kept in `signal_engine.py` for live
- TRIN/AD breadth fetch calls — removed (^TRIN/^NYAD 404 from yfinance, data never populated)

**Gate restorations (2026-06-03):**
- §59 OU halflife hard block (>25d) — restored to backtest (v10.4 regression: removing all dead gates together added 24 marginal trades, dropped IS Sh 0.24→0.19; individual ΔSh≈0 misleading at combined level)
- §60 Hurst ceiling hard block (>0.80) — restored to backtest (same rationale)

**§47–§58 implementation summary:**
- §47: VIX term structure backwardation — already in `macro.py` (VIX/VIX3M ratio, +7/-4)
- §48: IVR gate — MR BUY + IVR≥50 → +5pp; IVR<20 → −3pp (`signal_engine.py`)
- §49: Put-call skew — 25d skew >0.10 → +4pp in MR BUY (`signal_engine.py`)
- §50: Piotroski F-Score — already fully implemented in `fundamentals.py` (9-point, lines 6320–6350)
- §51: Forward PE value trap — PE>30 → −5pp; PE<15 → +3pp (`signal_engine.py`)
- §52: Short interest velocity — SI down >15% → +4pp; SI up >20% → −5pp (`signal_engine.py`, data from `market_data.py`)
- §53: Post-earnings timing — REJECTED (−17.4pp WR in 35–65d window vs outside)
- §54: VIX<15 MR suspension — hard block in `delivery_gates.py`
- §55: Cross-asset macro 3/3 headwinds — hard block in `delivery_gates.py`
- §56: Kelly position sizing — VIX-conditional `positionSizeScale` in `_assemble_signal()`
- §57: Thursday DOW gate — −3pp haircut / score≥55 gate in `delivery_gates.py`
- §58: EPS revision momentum — proxied by existing Finnhub `revision_pts` in `signal_engine.py`

See `docs/Stats.md` §47–§52 for full per-strategy results. Monte Carlo MR-Only P5=0.13 → edge statistically confirmed.

## §59–§84 research agenda — implementation status (2026-05-29)

26 strategies across 7 groups. ✅ = fully wired in live engine; ⏳ = deferred/needs paid data.

| Status | Group | Sections | Notes |
|---|---|---|---|
| 🗑️ | Statistical/Quant | §59 OU halflife, §60 Hurst, §61 idio vol | **Removed 2026-06-02** as hard-block gates (ΔSh=0.00 each). `technicals.py` still computes values for quality_score/L8 sizing. `gates/statistical.py` now only has §63. |
| ⏳ | Statistical/Quant | §62 VRP | Needs options per-stock IV |
| ✅ | Statistical/Quant | §63 sector cointegration | `compute_cointegration_zscore()` in `technicals.py`; Z<−2.0→+4pp; ETF histories injected from watchlist prefetch. **§63 now gated on Engle-Granger step-2 ADF stationarity (p<0.10, statsmodels) 2026-06-09** — non-cointegrated pairs return None. |
| ✅ live / 🗑️ backtest | Macro extensions | §64 yield curve, §65 TRIN, §66 AD breadth, §67 FOMC, §68 T10Y rate | Live: `macro.py` fetch; `_assemble_signal()` / `delivery_gates.py`. **Backtest: §64/§65/§66/§67/§68 removed 2026-06-02** (ΔSh=0.00; TRIN/^NYAD fetch 404; §64/§67/§68 +1/+4/+1 N with no Sharpe gain). |
| ✅ | Options pack | §69 GEX flip, §70 zero-DTE, §71 max pain, §72 VRP proxy | `options.py` compute + `score_options()` |
| ✅ | Fundamental quality | §73 insider clustering, §74 Beneish, §76 Altman | `edgar.py` / `fundamentals.py` compute; `signal_engine.py` gate |
| ⏳ | Fundamental quality | §75 buyback window | EDGAR 8-K parsing complexity |
| ✅ | Calendar/seasonal | §77 tax-loss window, §78 Sep/Oct seasonality | `_assemble_signal()` / `delivery_gates.py` |
| ⏳ | Calendar/seasonal | §79 Q1 rebalancing | Needs prior-year sector return |
| ✅ | Execution quality | §80 NBBO spread | `spread_pct` from `_snapshot_cache.lastQuote`; >1.0%→−10pp, >0.5%→−5pp |
| ✅ | Execution quality | §81 block prints | `get_recent_block_prints()` in `polygon_client.py`; ≥3 block buys→+5pp |
| ✅ | Portfolio construction | §82 trailingStopPct | Added to `_assemble_signal()` return dict |
| ✅ | Portfolio construction | §83 cross-signal correlation | avg pairwise corr in `scan_all()`; avg_corr>0.75→positionSizeScale cut |
| ⏳ | Portfolio construction | §84 survivorship bias | Paid Norgate/Sharadar PIT data. Free path tried 2026-06-09 (§86): membership from fja05680/sp500 is clean, but free-yfinance PRICES for delisted/recycled tickers are corrupt (symbol reuse) → still need a paid security master |

## MCP servers (when Node.js is available)

```bash
# GitHub — lets Claude read PRs, CI logs, issues directly
claude mcp add github -- npx -y @modelcontextprotocol/server-github
# Set: export GITHUB_PERSONAL_ACCESS_TOKEN=<your-pat>

# SQLite — lets Claude query trading.db directly
claude mcp add sqlite -- npx -y @modelcontextprotocol/server-sqlite backend/trading.db
```
