# Signal.Trade — Development Progress

> **Version: v8.1** · Updated: 2026-06-09 · Server: `uvicorn main:app --host 0.0.0.0 --port 8000`
> **Ratings live in [`docs/Stats.md §15`](Stats.md) (single source of truth, v8.1). This file is a chronological dev log.**
> ~210 tickers (incl. 52 leveraged ETFs) · 150 API endpoints · dual auto-execution brokers (Alpaca + IBKR)
> **Data: Polygon.io-first (bulk OHLCV + quotes + reference) · yfinance fallback · FRED (macro) · EDGAR (fundamentals/8-K) — pooled aiohttp + cached TLS across 20 modules**
> **Database: PostgreSQL 16 (primary) · single Alembic head · Alembic-only prod schema policy ([`SCHEMA_CHANGE_POLICY.md`](SCHEMA_CHANGE_POLICY.md))**
> **Tests: 1871 passed (ex-e2e) · run the full suite with `--ignore=tests/e2e` (e2e leaves a running event loop) · Backtest IS v10.7: N=205, WR=67.8%, Sharpe=0.23 (survivorship-corrected + §63 ADF gate)**
> **v8.1 (2026-06-09) — Survivorship correction + new live gates + correctness fixes + open-source quant-library audit.** Survivorship bias corrected via free PIT S&P constituents (the #1 named ceiling); new live gates (§14 FRED macro-regime, Polygon short-volume, dynamic sector limits + XLI ML); live correctness fixes (`sector_etf` decouple — was nulling ~81% of signals; cohort-enrichment restore; dark_pool restart-storm); §63 cointegration ADF correctness fix + macro-regime HMM→hmmlearn (both live); cross-sectional model net-positive at h=21 (net +0.347, borrow-robust) deployed in **SHADOW**. **Overall 8.8/10 product · 8.6/10 quality** (+0.1 from v8.0.1; shadow/research work excluded per "implemented ≠ working live"). See Stats.md §15.
> **v8.0 — Quant Engine (QENG) Roadmap Implementation (16/17 QENG features complete):** experiment registry, PBO report, checklist promotions, PIT feature store, replay engine, version lineage, live fill ledger, TCA service, capacity limits, portfolio allocator, HRP, cost-aware turnover control, stat-arb residual sleeve, TS momentum trend sleeve, cross-sectional factors, cross-sleeve capital allocator, triple-barrier meta-labeling, shadow-control cohort routing, and policy versioning. Overall 8.6/10 product · 8.3/10 quality (v8.0.1, revised down after a server-log audit found the PIT feature store crashing every live scan on NaN→json and the TSYS-5a health scorecard recording 0 calls due to a constraint/race — both green in the test suite; see Stats.md §15 v8.0.1).

## 📊 Live database stats (2026-05-17)

| Metric | Value |
|--------|-------|
| Watchlist tickers | 191 |
| Total signals generated | 7,015+ |
| Signals sent to Telegram | 543 |
| Resolved signals (outcome_pct filled) | 529 |
| Effective ticker-days (deduplicated) | 459 |
| 7d win rate (mark-to-market) | 58.8% |
| 7d win rate (stop-enforced) | 42.2% |
| 14d win rate | 65.1% |
| Win rate (friction-adjusted, best horizon) | 54.4% |
| Brier score | 0.2531 (best horizon) |
| Confidence gap | +11.0pp overconfident (raw) |
| XGBoost training samples | 529 |

## 🏅 Quality Ratings — v8.1 (2026-06-09)

> Ratings maintained in **[`docs/Stats.md §15`](Stats.md)** — single source of truth.
> **Overall: 8.8/10 product audit · 8.6/10 B+ quality grade** (v8.1, 2026-06-09 — +0.1 from survivorship correction + live correctness fixes + new gates; shadow/research excluded; see Stats.md §15).
> v8.0: Quant Engine (QENG) Roadmap Implementation (16/17 items): (1) Research experiment registry, PBO report, checklist; (2) PIT feature store, event replay, lineage; (3) fill ledger, TCA service, capacity limits; (4) portfolio allocator, HRP baseline, turnover control; (5) residual stat-arb, TS momentum, weekly factor sleeves, cross-sleeve allocator; (6) triple-barrier meta-labeling, cohort routing, policy versions. 1871 tests.
> v7.8: TSYS-1→13 targeted-system hardening (auth lockout/session, Stripe reconciliation, provider scorecard/corporate action validation, gate trace/explainability, model registry, outcome audit, risk limits/key rotation, Prometheus metrics, index audit/purges, audit log/risk-ack gate). 1862 tests.
> v7.7: IBKR integration, §75 buyback window EDGAR parser, HTTP latency cached TLS / pooled sessions pass. 1646 tests.
> v7.6: BE-1 partial (signal_engine.py 7421→5848, `services/engines/`), ACT-4 EOD-batch delivery fix, DPC-1 notification prefs, ACT-1 XLI block, ACT-2 sector audit. 1636 tests.
> v7.5: 32/38 free path-to-10/10 items done. BT-2/4, RD-3/4, CAL-2/3, ML-5, PROD-3/4, SEC-2/3/4/6, FE-1/3/4, DEPLOY-4/5/6, OOS v9 (10 tickers). 1115 tests.
> v7.4: RISK-1/2/4 (bracket stops + DD circuit-breaker + kill switch), A16-UI, PROD-1/3, ML-4, CAL-4, BE-2. 1096 tests.

---

## ✅ Implemented

### v6.4 (2026-05-31) — Methodology Soundness: Sharpe CI, Deflated Sharpe, ML Deployment Gates, Expanded Universe

**Backtest statistical reporting (`backtest_technicals.py`):**
- `sharpe_ci_print()` added — reports Lo (2002) 95% CI on per-trade Sharpe and Bailey-López de Prado Deflated Sharpe (expected max SR from 50 parameter searches). Called from IS main block and both OOS result tables. IS CI [0.13, 0.44] with SR=0 outside ✅; OOS CI [-0.36, 0.46] with SR=0 inside ⚠.
- OOS section now prints minimum N required for CI lower bound to exceed 0 at SR=0.10 (≈384 trades; current N=27 flagged as insufficient).
- IS Sharpe 0.29 > data-mining expectation 0.22 from 50 trials — passes Deflated Sharpe test ✅.

**ML deployment soundness (`signal_ml.py`):**
- `_MIN_LIVE_N_FOR_DEPLOYMENT = 300` — training runs below N=300 but model is never deployed (Hanley-McNeil 95% CI spans ±0.07+ below this threshold, making champion/challenger unreliable). Current N=529 passes.
- `_MIN_AUC_DELTA_TO_DEPLOY = 0.005` — challenger must beat champion by >0.005 AUC, not just by epsilon. Prevents noise-driven churn at current sample sizes.
- `auc_ci_95(auc, n_pos, n_neg)` — Hanley-McNeil (1982) 95% CI for AUC. Logged at INFO level and persisted to metadata JSON (`oos_auc_ci_95`, `training_only`, `n_total`, `min_live_n_for_deployment`, `min_auc_delta_to_deploy`).
- Champion correctly retained (new model CV-AUC 0.6188 < champion 0.6399; Δ = −0.0211 < 0 → rejected).

**Universe expansion (backtest `backtest_technicals.py`):**
- 74 → 100 IS tickers (XLK/XLF/XLY/XLC/XLB additions; XLV/XLE/XLI/XLP blocked in live engine remain research-only).
- New IS canon: **N=157, WR=70.7%, Avg=+1.04%, Sharpe=0.29, MC P5=0.16** ✅. Sector-filtered: N=136, WR=69.9%, Sharpe=0.27.
- **Key milestone:** IS Sharpe 95% CI lower bound = **0.13 > 0** — first time the IS result clears statistical significance at 5% on per-trade data.

**Methodology tests (`test_backtest_methodology.py`, tests 14–19):**
- Test 14: Lo (2002) formula correct — IS N=114, SR=0.28 per-trade is statistically significant (lo>0).
- Test 15: OOS N=27, SR=0.05 → CI contains zero — regression guard against overclaiming OOS significance.
- Test 16: Deflated Sharpe formula produces plausible range for N=50 trials.
- Test 17: `_MIN_LIVE_N_FOR_DEPLOYMENT ≥ 200` and `_MIN_AUC_DELTA` in [0.001, 0.05] — deployment gate constant validation.
- Test 18: Hanley-McNeil CI for AUC=0.64, N=529 lands in expected range.
- Test 19: Zero-class degenerate case returns (0.0, 1.0) gracefully.

**Lint/format:** 5 ruff errors auto-fixed (unused imports, bare f-string); all 5 files reformatted.

**Tests: 1000 passed, 0 failed, 2 skipped** (up from 916 pre-session; 1 pre-existing flaky test `test_vector_store` passes in isolation, fails due to test-order import state — unrelated to these changes).

### v6.3 (2026-05-30) — Signal Quality Hardening: CMF Ablation, §63/§80/§81/§83, SHAP Audit, Sector XGBoost

**CMF ablation (§46 decomp follow-up):**
`BASE_WEIGHTS["cmf"]=0.00` in `signal_alpha_decomposition.py` — CMF family confirmed redundant when TREND=0; OBV/RVOL carry the same money-flow information. Live engine CMF scoring halved (×0.5) to eliminate double-counting while preserving qualitative gate. Projected ΔSharpe: +0.04 (from §46 decomp; IS rerun pending).

**§63 Sector Cointegration Gate:**
`compute_cointegration_zscore(stock_prices, etf_prices, window=252)` added to `technicals.py`. Engle-Granger regression of stock on sector ETF; residual Z-score measures deviation from long-run pair equilibrium. Gate: Z<−2.0→+4pp (double dislocation), Z<−1.0→+2pp, Z>0.5→−2pp. Zero additional API calls — sector ETF Close series injected into `market_ctx["etf_histories"]` from already-prefetched watchlist histories in `scan_all()`. Projected ΔSharpe: +0.08–0.15 (per TODO §219).

**§80 NBBO Spread Quality Gate:**
Extracts bid/ask from `_snapshot_cache.lastQuote` (already populated by `get_polygon_snapshot_batch()`). Spread >1.0%→−10pp, >0.5%→−5pp, <0.1%→+1pp. Enforces honest friction calibration: backtest assumes 0.5% round-trip; wide-spread names make this 2–3× too optimistic. Validation: tag resolved trades with spread at entry.

**§81 Block Print Detection:**
`get_recent_block_prints(ticker, min_block_size=5000)` added to `polygon_client.py`. Fetches last 500 trades via `/v3/trades`, classifies: at_low (≤day_low×1.01) = accumulation, at_high (≥day_high×0.99) = distribution. Gate: ≥3 block buys + bbv>bsv×2→+5pp, ≥3 block sells + bsv>bbv×2→−6pp. 10-min TTL cache. Projected ΔSharpe: +0.10–0.20 on names with clear block activity.

**§83 Cross-Signal Correlation Penalty:**
In `scan_all()`, after all signals scored: build 63d return matrix for simultaneous BUY signals, compute avg pairwise correlation per signal vs. the rest. avg_corr>0.75→positionSizeScale cut by min(0.40, (corr−0.75)×1.6). Follows existing architecture: correlation risk is inventory risk, not alpha uncertainty — confidence unchanged, only sizing reduced.

**SHAP Feature Audit (eval_ml.py §7):**
`shap_audit(rows, model)` added using `shap.TreeExplainer`. Reports mean |SHAP| per feature with direction (pos/neg), flags inverted features (negative SHAP on expected-positive features), lists near-zero candidates for removal. `shap>=0.45.0` added to `requirements.txt`. Note: requires Python 3.11 CI environment (numba incompatible with Python 3.14 local).

**Sector XGBoost (XLF/XLP/XLU):**
`train_sector_model(all_results, vix_dict, sector_etf, sector_tickers, champion_auc)` in `train_backtest_ml.py` — trains sector-specific XGBoost (max_depth=3 vs 4 global, shallower to avoid overfit on smaller sector N) and saves `backtest_ml_model_{SECTOR}.json` only if OOS AUC > global champion. `get_sector_entry_model(sector_etf)` and `predict_entry_prob_sector(tech, vix, sector_etf)` added to `signal_ml.py` — transparently falls back to global model when no sector file exists. `_assemble_signal()` now calls `predict_entry_prob_sector` instead of `predict_entry_prob` directly.

**Test fixes:**
- `test_options_sweep_gex_gives_15pp_bonus` — added `patch("services.signal_ml.get_entry_model", return_value=None)` alongside existing `get_model` patch; new `predict_entry_prob_sector` was reading the live backtest model and boosting both test paths to the 72.0 ceiling, masking the sweep vs GEX-only difference.
- `test_pre_long_weekend_haircut_applied` — corrected patch target from `services.delivery_gates` to `services.market_calendar`; `get_upcoming_holidays`/`is_pre_long_weekend` are local imports inside the function, not module-level attributes.

**Test count:** 916 passed, 0 failed, 3 skipped (up from 762 in v6.2; 154 additional tests from new test modules).

### v6.2 (2026-05-29) — §59–§82 Full Gate Stack + Backtest Universe Expansion

**Backtest `backtest_technicals.py`:**
All §59–§82 research gates wired into backtest simulation and analysis sections. New gates in `simulate_ticker()`: §59 OU half-life (HALFLIFE_MAX=25d), §60 Hurst (CEIL=0.80), §61 idiosyncratic vol (>55%), §64 yield-curve XLF penalty, §67 FOMC day hard block, §68 rising-rates XLK penalty, §78 Sep/Oct seasonality floor. New `compute_indicators()` columns: `ou_halflife`, `hurst`, `realized_vol_63`, `near_52wk_low`. New macro fetches: `fetch_t10y()` (§64/§68), `fetch_trin()` (§65), `fetch_ad_breadth()` (§66). Trade dict gains `trin`, `ad_ema10_chg`, `zweig_thrust`, `near_52wk_low` metadata fields. Three new analysis sections: §14 TRIN capitulation split, §15 Zweig/A-D breadth split, §16 tax-loss harvest window split. Gate calibration empirically adjusted (Hurst 0.60→0.80, OU 12d→25d — large-cap median H=0.71; 0.60 blocked 88–95% of signals). §55 `fetch_cross_asset_composite` bug fixed: `get_loc` KeyError on misaligned tz-aware indices replaced with vectorized DataFrame join + index normalization.

**Universe expansion 48→74 tickers (balanced across sectors):** XLB: +LIN/SHW/APD/ECL/NUE (1→6) · XLC: +DIS/T/VZ (5→8) · XLF: +V/AXP/SPGI (8→11) · XLY: +BKNG/GM/TJX (13→16) · XLK: +ANET (15→16) · XLV: +JNJ/MRK/LLY/UNH (research) · XLE: +XOM/CVX/COP (research) · XLI: +HON/RTX (research) · XLP: +PG/KO (research). ETF expansion tested and rejected: broad/sector ETFs (SPY/QQQ/IWM/XLK/XLY/XLB/XLI) all showed WR 33–50% avg −0.5 to −1.0% — MR signals calibrated on individual stock vol don't hold at index level.

**Result:** IS N=114, WR=67.5%, Avg +0.98%, Sharpe=0.28, **MC P5=0.12** ✅ (>0.10 = edge generalises). Sector-filtered: N=94, WR=64.9%, Sharpe=0.24.

### v6.9 (2026-05-25–29) — Security Hardening, esbuild Pipeline, Alpha Research §32–§45

**Infrastructure & Security:**
PostgreSQL migration complete (7,015+ signals, 8 users, SQLite removed). Alembic installed with initial 13-table schema migration. CI fixed: pytest-timeout added, accuracy gate now fails builds, pip-audit enforced. SecurityHeadersMiddleware (CSP, HSTS, X-Frame-Options). Stripe webhook idempotency via `StripeEvent` table. Password-reset tokens moved to DB (SHA-256, expiry, prior token invalidation). All 11 background tasks supervised via `_supervise()`; `/api/health` reports live/dead status.

**Auth & Frontend Security:**
Access tokens moved from `localStorage` to JS module-level variable. DOM injection removed from login/signup/verify-email (textContent replaces innerHTML). `test_frontend_smoke.py` added (6 antipattern checks). esbuild pipeline: `build.mjs` → `dist/app-bundle.js`; Dockerfile multi-stage (Node.js build → Python serve); `load-app.js` + `init.js` extracted for CSP compliance. `'unsafe-eval'` added temporarily for Babel fallback (remove after bundle confirmed in prod).

**Backend Architecture:**
Scanner decomposed: `fetch_market_context()`, `_persist_scan_signals()`, `_deliver_scan_signals()` extracted; `_run_scan_impl` is a thin 11-step orchestrator. Admin MRR uses `TIER_PRICES_CENTS`. All `datetime.utcnow()` replaced with timezone-aware equivalents. Confidence-weighted position sizing: `positionSizeScale = portfolio_size_scale × clamp(conf/62, 0.5, 1.5)`.

**Signal Engine Features:**
EPS revision hard gate (blocks MR BUY 8–14d pre-earnings without analyst revision or unusual calls). Fundamental value-trap gate (revenue <−20% YoY AND FCF <−5%). VIX<20 gate (blocks all MR in calm markets, 103-ticker 23yr finding). GEX + options flow hard gate (yfinance, no paid API). Adaptive exit (RSI>55 / MACD+ / VWAP while profitable): 17.1% of trades exit early at 100% WR, avg +3.20%. Score-segmented hold: low-score trades (40–49) use 5-day hold; WR +6.1pp, Ann.Sh +0.12.

**Research §32–§35:**
SELL signals (−45 thresh): collapse Sharpe 0.20→−0.03 — disabled. Energy sub-sectors (XOM/CVX/COP/SLB): N=13, WR=61.5%, Ann.Sharpe=2.03. XLU: no viable MR edge, blocked. §35b adaptive exit RSI accepted: WR +7pp. ATR 2.0/2.5× confirmed optimal. Covered call overlay rejected (kills right-tail convexity). Intraday disabled (WR 34.8%). Confidence gap closed: +1.2pp vs prior +11pp.

**Research §40/§42–§45 — OSC/MR Weight Calibration:**
RSI removed from MR gate (non-binding). MR weight 0.50→0.70 (optimal, 105-ticker sweep). OSC weight: 1.0→0.3 (§40, 24-ticker subset) then REVERSED 0.3→1.0 (§45: OSC×1.0 only breakeven on 105-ticker universe; OSC×0.3 = Sharpe −0.24 — was a calibration error). DONCHIAN 1.0→0.50 (OSC↔DONCHIAN corr=0.70; live engine MR-path scores halved: 8→4, 5→2). BUY_THRESH confirmed non-binding (no trades in 30–49 band). OOS=0.00 identified as sector contamination artifact (MS/XLF: WR=16.7%, avg=−2.34% alone destroys OOS). §45 ablation: TREND removal = +0.29 Sharpe, VOL removal = +0.15 Sharpe, DONCHIAN removal = neutral. TREND=0 applied to decomp script; §46 validation running.

---

### v6.1 (2026-05-25) — §16/§17 Sector Gates, Polygon Options Chain, Entry-Quality Filters

**Signal engine (`signal_engine.py`):**
- [x] **`_SECTOR_MR_CONFIG`** — per-sector MR calibration from §15b/c/d/e + §16a research. Healthcare (Sharpe −0.17, WR 29.4%), Industrials (Sharpe −0.48, WR 28.6%), Real Estate (Sharpe −15) blocked via `buy_thresh: 999`. Energy `hold_days: 5` (§16a WR 70%).
- [x] **Fundamental value-trap gate** — blocks BUY when revenue <−20% YoY AND FCF yield <−5% (yfinance free data)
- [x] **5 live-validated 0% WR tickers blocked** — APH (0/4, avg −8.70%), EOG (0/2, avg −7.00%), SYK, CVX, UPS added to defensive_ticker_block (§11b ticker analysis, May 2026)
- [x] **ATR%rank ceiling ≤70 gate (§17b)** — trending-panic entries blocked; Quantpedia finding: MR in very-high-ATR regimes produces weaker bounces
- [x] **Single-day return jump filter <−6% (§17c)** — large single-day drops blocked as fundamental repricing; Alpha Architect: filtering return jumps tripled cumulative returns
- [x] **VIX 3-day slope gate** — blocks MR entry when VIX rising >+3pts over 3 days AND VIX>16; `vix_3d_slope` added to `macro.py`
- [x] **IBS + SMA20 multi-day streak gate (§17e)** — Pagonidis 2013: IBS<0.15 now requires ≥5 consecutive days below SMA20; N=3/5/7 streak variants in backtest
- [x] **Near-earnings revision soft-gate** — −4pp confidence haircut for 8-14d pre-earnings signals without positive analyst revision
- [x] **`opt_flow` param added to `_assemble_signal()`** — wired for future options-flow hard gate
- [x] **Analyst cache TTL 3600→1800s**

**Options service (`options.py`):**
- [x] **Full Polygon options chain** — `_fetch_options_polygon()` with 8-page pagination (up to 2000 contracts); accurate GEX/PCR from full chain; graceful 403 fallback to yfinance
- [x] **Options executor 3→8 workers; cache TTL 2400→300s** — intraday freshness for fast-moving options flow

**Dark pool / corporate actions (`dark_pool.py`):**
- [x] **Migrated to real Polygon endpoints** — `/v3/reference/dividends`, `/v3/reference/splits`, `/v2/reference/ftd`; returns `ex_div_soon`/`split_soon` instead of stale Massive API stubs

**Main (`main.py`):**
- [x] **Continuous intraday scanner** — replaces fixed-slot scheduler; fires at 09:30, then every `scan_interval_min` minutes until 16:00, plus a 16:02 close-of-day scan; legacy fixed-slot mode preserved when `scan_interval_min == 0`
- [x] **`RLIMIT_NOFILE` raised to 65536 at startup** — prevents socket exhaustion on long scan cycles

**Backtest / research:**
- [x] **Gate 17b (ATR ceiling), 17c (jump filter), 17e (IBS streak) added to backtest**
- [x] **Entry delay T+2 override and adaptive exit mode** in `simulate_ticker()`
- [x] **`run_section13/15/16/17.py` runners** — targeted research sweeps per alpha section
- [x] **`screen_sp500_mr_candidates.py`** — screens full S&P 500; quality bar: WR≥55%, per-trade Sharpe≥0.35, N≥5; `--fast` mode (~30min)
- [x] **`_bt_2w.py`** — 2-week rolling backtest helper

**Docs:**
- [x] **`docs/LEARNINGS.md` created** — full alpha inventory: 11 alpha sources, negative findings, timeline, best result §15f (Ann. Sharpe 1.27, WR 78.8%, N=66)
- [x] **`docs/Stats.md` updated** — §16/§17 findings

---

### v6.0 (2026-05-24) — Signal Alpha Decomp v8, Calibration Backfill, Live Gap Analysis

- [x] **Signal alpha decomposition v8** (`signal_alpha_decomposition.py`) — §13–§17 research framework; per-gate sweep, full universe analysis, live gap reporting
- [x] **Calibration backfill** — historical outcome data retroactively populates calibration curves; reduces cold-start miscalibration
- [x] **Live gap analysis** — identifies signals generated in live engine not covered by backtest universe; highlights blind spots

---

> **v5.x history (v5.0–v5.12, 2026-05-09–18) archived** — see git log for full change details.

---

## 👁️ Known Blind Spots

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | **Phantom wins** — 88 historical trades show WR 58.8% vs stop-enforced 42.2% | Critical | ✅ Fix deployed 2026-05-17. New signals resolve correctly. Historical backfill pending. |
| 2 | **Confidence gap +11pp** — model systematically overconfident | High | ✅ Calibration tightened (blend 0.97, N_FULL 15). Monitoring next training run. |
| 3 | **Sector model gaps** — XLF/XLP/XLU blocked (PF < 0.40x) | High | 🔄 Blocked until sector-specific sub-models retrained |
| 4 | **Intraday recalibration** — 34.8% WR, PF 0.73x | Medium | 🔄 Restored at ≥68% conf floor; quality improvement in progress |
| 5 | **Hardcoded owner password** | Critical | ❌ `OWNER_PASSWORD=ChangeMe123!` still in source |
| 6 | **Monolithic `run_scan`** | Medium | 🔄 Delivery gates extracted; full scanner decomposition pending |
| 7 | **Chart drawing tools** | High | ❌ Not yet implemented |
| 8 | **Autonomous execution** | Critical | ❌ OAuth broker integration not started |

---

## ⬆️ Polygon Premium Upgrade Path

The following services return `{}` on free tier — zero code changes needed to unlock:

| Service | File | Plan |
|---------|------|------|
| Full option chain GEX + 25Δ skew | `massive_options.py` | Starter ($29/mo) |
| ETF fund flow data | `etf_flows.py` | Developer ($79/mo) |
| ETF constituent weights | `etf_constituents.py` | Developer |
| Corporate guidance (EPS raise/cut) | `massive_analyst.py` | Developer |
| Real-time trade tape (dark pool) | `dark_pool.py` | Developer |
