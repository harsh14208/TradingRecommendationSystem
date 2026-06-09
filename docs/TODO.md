# Signal.Trade — TODO

## 🔴 Pre-Launch Checklist
These are critical tasks that must be completed before public launch or marketing scale.

- [ ] **1. Change owner password** — `backend/.env`: set `OWNER_PASSWORD=<16+ chars, mixed case, symbols>`. Default `ChangeMe123!` is committed to source. *Risk: instant account takeover.*
- [ ] **2. Deploy to public HTTPS URL** — Run `railway up` or `fly deploy`. Set `APP_URL=https://your-app.up.railway.app`. *Risk: Stripe webhooks 404, OAuth callbacks broken, HTTPS-only cookies not sent.*
- [ ] **3. Configure Stripe billing** — `STRIPE_SECRET_KEY` and price IDs set. Still needed: register webhook in Stripe Dashboard, copy `whsec_...` to `STRIPE_WEBHOOK_SECRET`. (Note: startup now logs CRITICAL if `STRIPE_WEBHOOK_SECRET` is empty in prod; webhook handler returns 500 explicitly). *Risk: checkout completes but tier never activates.*
- [ ] **4. Register Telegram webhook** — After HTTPS deploy: `curl -X POST <https://your-app>/api/telegram/set-webhook`. *Risk: subscribers cannot link Telegram.*
- [ ] **5. Configure SMTP (email)** — Add `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` to `.env`. *Risk: no email verification, no password reset, no weekly digest.*
- [ ] **6. Enable Telegram broadcast channel** — Create private channel, make bot admin, add `TELEGRAM_BROADCAST_CHANNEL_ID=-100...`. *Risk: at >50 subscribers, per-user DM loop hits Telegram rate limit.*
- [x] **7. Train and deploy XGBoost ML model** — N≥300 reached (566 resolved: 495 BUY / 71 SELL, 101 tickers). Manual train run 2026-06-09 via `train_model()`: trained 396 / tested 170, **OOS AUC 0.6872** (95% CI [0.607, 0.767]) vs champion **0.6883** → **rejected** (Δ−0.0011, needs +0.005); champion kept, live model untouched. Top features are structural (`has_fundamentals_source`, `target_pct`, `n_rationale`) not alpha — consistent with entry-alpha-exhausted. NOTE: caveat — all 566 resolved trades fall in a single ~7-week window (2026-04-20→06-09), so effective independent N (for a trustworthy comparison) is far below 566; the Δ is deep in noise. **Auto-retrain already live**: `_weekly_ml_retrain` (main.py:588) runs Sun 11am ET, calls the same self-gating `train_model()` — will auto-deploy a challenger only once it genuinely beats the champion by ≥0.005 AUC across more accumulated regimes. No manual action needed.
- [ ] **8. Configure Google OAuth** — `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`.
- [ ] **9. Configure VAPID web push** — Generate keys via py_vapid. *Risk: no browser push notifications.*
- [ ] **10. Set up Cloudflare CDN** — Point DNS to Railway/Fly. *Risk: slower global load.*
- [ ] **11. Google AdSense** — Apply at adsense.google.com. *Risk: no ad revenue from free tier.*
- [ ] **12. Add Redis in Production** — `railway add --plugin redis`. *Risk: redundant API calls under concurrent load.*
- [ ] **13. Upgrade SendGrid** — Essentials (~$20/mo) before daily signups + resets exceed 100 emails/day.

---

## 🎯 Active Research & Alpha TODOs
These are targeted research and statistical modeling opportunities to improve signal edge.

- [~] **§86. Market-Neutral Cross-Sectional Ranking Architecture** — Move from time-series prediction to cross-sectional ranking. **v1 built 2026-06-09** in `backend/scripts/cross_sectional_alpha_model.py`. RESULT: OOS 2019→2026 **net Sharpe ≈ 0.44–0.50** (gross 0.73–0.78), mean IC +0.018, quintiles NOT monotonic. Beta-neutrality lowers vol but adds no alpha — "1.0+ mathematically" is a fallacy (Sharpe = IC × √breadth × √turnover-eff; generic price-factor IC ≈0.018 caps it). Honest verdict: competitive with the ~0.28 IS / ~0.14 fwd single-name engine, NOT a ceiling break. Data caveats: `cache_earnings` is dates-only (proximity feature, no surprise); short interest is Postgres bi-weekly 2017-12+ (`--short-interest` opt-in).
  - [x] **Step 1: Data Ingestion & Merge** — survivorship-bias-free universe from `sp500_historical_constituents.json` point-in-time intervals (181 names ∩ cache, ETFs excluded); merges `cache_ohlcv` + `cache_earnings` + optional Postgres short interest.
  - [x] **Step 2: Cross-Sectional Normalization** — per-day z-scores, winsorized ±3σ, same-day only (no lookahead).
  - [x] **Step 3: Model Training** — XGBoost regressor; target = 5d forward return MINUS cross-sectional mean (relative return); chronological split + HORIZON embargo.
  - [x] **Step 4: Portfolio Allocation** — dollar-neutral top/bottom decile, non-overlapping 5d rebalances, turnover costs, gross+net Sharpe / IC / monotonicity / maxDD.
  - [x] **Step 5: Robustness validation (2026-06-09)** — added purged expanding-window walk-forward CV (retrain per fold, HORIZON embargo, block-bootstrap Sharpe CI) + cost-sensitivity sweep (`--walk-forward --cost-sweep`). FINDINGS: WF net Sharpe **0.42** (matches single-split 0.42 → NOT a window artifact ✅), but **90% CI [+0.00, +0.84]** — floor sits on zero, statistically fragile. Regime-dependent: only **10/15 folds positive** (2014/2015/2023 deeply negative). IC unstable (yearly +0.002 → +0.036). Cost-fragile: net Sharpe 0.70→0.42→0.06 at 0/10/20 bps, negative by 40 bps; avg turnover 1.3×/rebalance. VERDICT: reproducible but thin and cost-sensitive — do NOT scale capital on it as-is.
  - [x] **Step 6: Full-S&P-500 expansion (2026-06-09)** — pulled complete PIT membership from github.com/fja05680/sp500 (`data/sp500_ticker_start_end.csv`, 1202 names) and backfilled OHLCV via new `scripts/fetch_sp500_ohlcv.py` (619 fetched, 366 delisted/unavailable on free yfinance → cache 970). Universe grew ~200 → 835. RESULT: expansion **HURT**, didn't help. WF net Sharpe **+0.42 (curated 200) → −0.02 ($10M floor) → −0.23 ($100M floor)**. Three confirmed causes: (1) free-data contamination — recycled/delisted ticker symbols splice unrelated companies → spurious ±1000% weekly prints that detonated the short leg (vol 406%, maxDD −1523%) until a ±50% `FWD_RET_CAP` winsorizer was added; irreducible without a paid PIT security master (§84). (2) Signal dilution: IC 0.016 → ~0.011. (3) Turnover rose 1.1→1.4× and the smaller gross spread (6.5%/yr) no longer covers cost. The √breadth benefit is real but far too small to offset 1–3. LESSON: the curated large-cap list was doing genuine work; breadth from free data is net-negative.
  - [x] **Step 7: Qlib TopkDropout / hold-until-dropout (2026-06-09)** — implemented hysteresis exits (`--exit-decile`: enter top `decile`, hold until name leaves wider `exit_decile` band) + a `--universe {full,curated}` switch (curated = `backtest_technicals.TICKERS`, the 109-name live IS set). WF on curated: baseline net −0.03 (turn 1.35) → exit 0.20 net −0.11 (turn 1.34) → exit 0.40 net −0.12 (turn **1.22**). TopkDropout STRICTLY WORSE. Diagnosis: hysteresis cuts turnover only when rankings PERSIST; at IC ≈0.013 the cross-sectional ranking re-randomizes every 5 days, so names scatter rather than linger near the entry boundary — nothing to hold. The turnover isn't fixable plumbing, it's a direct symptom of weak signal persistence. (Also note: curated-109 baseline ≈ −0.03, below the original ~200-name 0.42 — that earlier figure leaned on broader breadth + pre-winsorization; honest curated-IS cross-sectional edge is ~0.)
  - [x] **Step 8: Short-interest velocity feature test (2026-06-09)** — added SI level + VELOCITY features (`si_chg_1`/`si_chg_3` = %Δ shares-short vs prior/3rd FINRA settlement; `dtc_chg_1` = Δdays-to-cover) via as-of join from Postgres `short_interest_biweekly` (2017-12+, 109/111 curated tickers). Fixed `load_short_interest` DB accessor (`config.settings`→`database.DATABASE_URL`). WF curated 2018+: aggregate looked like a WIN (IC 0.0086→0.0109, gross Sh 0.26→0.59, net −0.05→**+0.26**) — BUT per-fold breakdown kills it: the entire lift is ONE fold (2025: baseline −0.94 → +SI +3.01, Δ+3.95); SI made 5 of 9 folds WORSE, and a single-split 2022+ test was net −0.66. SI features also rank BELOW the top-6 (all price) in importance. VERDICT: short-interest velocity is a single-regime (2025 squeeze) artifact, NOT a stable cross-sectional edge; fails the walk-forward stability bar. The per-fold harness caught a false dawn the aggregate number would have sold.
  - [ ] **Step 9 (decision): the ceiling is IC/data, not architecture.** Four 2023-24 "structural alpha" frameworks now evaluated against this engine's own data: (1) Meta-label+triple-barrier — already shipped (`meta_label_model.json`, CV-AUC 0.42 on N=221, worse-than-random) + exit-sweep already "exhausted"; (2) Qlib cross-sectional — built §86, net ≤0.42; TopkDropout worse (Step 7); (3) Hierarchical RL — untrainable at N≈221, overfit guaranteed; (4) Adaptive sleeve allocation — sleeves just disabled (commit 3e4e102), 5d-rolling routing whipsaws at this N. ALL rearrange/filter existing alpha; none raise IC. Only real levers left: new ORTHOGONAL data (§62 options-IV, options-flow, short-interest velocity) or accept honest ~0.2–0.4. Paid alt-data still NOT justified until a free-data path shows IC > ~0.03.
- [ ] **§85-2. Audit EDGAR MD&A sentiment contribution** — `edgar.py` MD&A NLP is annual 10-K data applied to a 5-day trade. Tag live signals that received an MD&A score adjustment and compute ΔWR. If no improvement, disable. Low priority until §85-1 data is available.
- [ ] **§62. VRP per-stock** — Needs per-stock IV history (Polygon Options upgrade, ~$79-199/mo). High IVR (>80th percentile) at oversold MR entry should add an additional +6pp.
- [ ] **§84. Survivorship bias correction** — Purchase EODHD (~$20/mo) or Norgate ($33/mo) delisted constituent lists. Add delisted tickers to `TICKERS` for their active periods to make IS -> OOS gap more honest.
- [ ] **Options flow confirmation gate** — Subscribe to Unusual Whales API (~$50/mo). Enter only when options flow confirms setup (e.g. large put sweeps → −10pp, large call sweeps on oversold → +8pp). Expected ΔSharpe: +0.15–0.25.
- [ ] **GEX support levels** — SpotGamma API (~$99/mo). Enter only when `price ≤ gex_support_level × 1.01` to ensure dealer positioning reinforces mean reversion. Expected ΔSharpe: +0.10.
- [ ] **Market-neutral beta hedge** — Short 0.9× position value in SPY at entry. Requires margin account. (QuantEngine validated: IS Sharpe 0.29 = 0.12 pure alpha + 0.17 beta. True forward estimate ≈ 0.10–0.15).

---

## ⚙️ Operational, Deployment & Testing TODOs
Infrastructure, testing, and system-level follow-ups.

- [ ] **DEPLOY-2. Sentry + UptimeRobot Setup** — Configure Sentry (free tier) for Python exception tracking and UptimeRobot for endpoint availability monitoring. Add `SENTRY_DSN` to `.env` and wire it in `main.py`.
- [ ] **DEPLOY-3. DB Backups** — Automated daily backup of `trading.db` to a Cloudflare R2 or S3 bucket (Railway volumes are ephemeral). Retention: 7 daily, 4 weekly.
- [ ] **FE-2. Accessibility audit (WCAG 2.1 AA)** — Run `axe-core` or Lighthouse accessibility audit. Fix: keyboard navigation for all interactive elements, ARIA labels on icon buttons, color contrast, screen reader compatibility.
- [ ] **TEST-4. Mutation testing** — Run `mutmut` on `delivery_gates.py` and the scoring logic in `signal_engine.py`. Target mutation score >70% to identify tests passing on broken logic.
- [ ] **QENG-3d. Execution policy simulator** — Compare market, limit, midpoint, delayed-entry, and bracket variants in paper/shadow mode. Promote only on cost-adjusted expected value.
- [ ] **ACT-6. Run E2E Playwright tests** — Run `pytest tests/e2e/ --base-url http://localhost:8000 -v` after installing dependencies and verify golden paths.
- [ ] **ACT-7. Validate bracket stop in Alpaca paper account** — Enable auto-execution for owner account on paper, trigger a manual signal delivery, and verify Alpaca dashboard shows bracket order legs correctly.
- [ ] **ACT-8. Install shap for ML-5 live audit** — Install `shap` and re-run live audit once ≥50 post-A19 resolved signals are available.
- [ ] **ACT-9. Push to GitHub to trigger CI/CD validation** — Verify the full CI/CD pipeline, including gitleaks scanning on Fernet ciphertext, coverage floor (25%), and deployment steps.

---

## 📊 Live Findings & Calibration TODOs
Actions derived from empirical performance audits on the live system.

- [ ] **OOS-1. Accumulate ≥30 live trades in OOS v7 tickers** — SYK, RMD, IDXX, ZBH, RL, DECK, POOL, NDAQ, CBOE, BR. Run `python scripts/backtest_technicals.py --oos`. If OOS v7 CLEAN Sharpe ≥ 0.10, promote to IS.
- [ ] **OOS-2. Accumulate ≥30 live trades in OOS v8 tickers** — LNC, AMG, PAYC, SIG, AEO. Cautiously evaluate the 0.2% Russell 2000 pass rate.
- [ ] **ALPHA-2 / A24. Run §85-1 fundamental modifier audit** — `python scripts/gate_contribution_analysis.py --section85 --after 2026-06-01` at ≥200 resolved signals. Remove modifiers with ΔWR < −1pp. Primary targets: §50 Piotroski, §74 Beneish, §73 Insider.
- [ ] **CAL-1 / A25. Calibration v5** — Run `python scripts/backfill_confidence.py --force --apply` when ≥50 post-A19 resolved signals are available to reflect the corrected scoring pipeline.
- [ ] **ML-2 / A15. Sector-specific XGBoost models** — Retrain sub-models for concentrated sectors (e.g. XLK) when sector-specific resolved signals reach ≥200.
- [ ] **RISK-3. Position sizing live audit** — After N≥50 auto-executed trades, compare realized notional vs theoretical scaling. Check for rounding errors if mean size deviates >20%.
- [ ] **ACT-3. Sector-conditional calibration (CAL-V5)** — XLK Brier deviates +0.015, XLV deviates −0.016. Run `backfill_confidence.py --force --apply` with sector grouping to deploy separate isotonic curves.
- [ ] **ACT-4. Investigate live WR gap (Part b)** — Perform detailed validation on the remaining gap between live WR and IS WR after resolving EOD-batch delivery bugs.
- [ ] **ACT-5. Full backtest flag validation runs** — Run parameter sensitivity sweeps (`--param-sweep`), bootstrap CI checks (`--validate-live-gates`), and regime splits (`--regime-split`).

---

## 🏁 Path to 10/10 — Per-Aspect Rating TODOs
Concrete work to take each [Stats.md §15](Stats.md#L359) rating aspect to 10/10. Honesty note: aspects marked **⏳gated** cannot reach 10 by code alone — they need paid point-in-time/options data, an accrued live sample (N), or elapsed time. A literal 10 on IS/OOS is aspirational (survivorship + sample-size ceilings the doc itself flags at 8/7); the tasks below are what *would* close the gap, not a promise the gap closes this quarter.

### Signal & Research
- [ ] **R10-1: IS Backtest Accuracy (7.9 → 10)** ⏳gated — bust the survivorship ceiling: complete **§84** (EODHD/Norgate delisted constituents, add to `TICKERS` for active periods) + **ACT-5** full flag-validation sweeps + the **--pbo** CSCV report showing PBO < 5%. Honest IS WR will *drop* a few pp; the score rises because the number becomes trustworthy.
- [ ] **R10-2: OOS / Forward Validation (6.5 → 10)** ⏳gated — accrue resolved signals to **N ≥ 387** (clears SR=0 from the 95% CI) via **OOS-1** (v7) + **OOS-2** (v8); then run expanding **--walk-forward** and confirm OOS CLEAN Sharpe ≥ 0.10 with the curation gap < 0.10.
- [ ] **R10-3: Live Alpha Quality (7.0 → 10)** ⏳gated — run **§85-1 audit** (ALPHA-2, ≥200 resolved) to prune negative modifiers; prove a *causally positive* treatment effect via the **REF-4** cohort dashboard (delivered vs withheld); sustain live Sharpe ≥ IS midpoint over ≥2 quarters.
- [ ] **R10-4: Gate Stack §47–§83 (8.8 → 10)** ⏳gated — wire the last 2 of 31 strategies: **§62 VRP per-stock** + the **Options-flow** and **GEX** confirmation gates (all need paid options data); validate each adds ΔSharpe via `--validate-live-gates`.
- [ ] **R10-5: Backtest Infrastructure (7.8 → 10)** — give the just-fixed PIT feature store (QENG-2a) a burn-in window with zero persist errors; ship **REF-2** replay-parity drift detection (weekly live-vs-replay diff = 0); fold in **§84** point-in-time data so snapshots are survivorship-correct.
- [ ] **R10-6: Confidence Calibration (7.6 → 10)** ⏳gated — **CAL-1** Calibration v5 on ≥50 post-A19 signals + **ACT-3** per-sector isotonic curves; target val-Brier ≤ 0.23 and reliability-diagram ECE < 0.03.

### Risk & Execution
- [~] **R10-7: Per-signal Kelly — RESEARCHED, NO-DEPLOY (2026-06-08).** Added `stats_kelly` + `kelly_size_mult` + the §Inv-K validator to `backtest_technicals.py`. **Key finding:** the universal 1.5s/2.0t stop/target makes reward:risk *constant* (realized b=0.83), so per-signal Kelly has no payoff term and is just a convex reshaping of conviction sizing. Exploratory half-Kelly (empirical p, wide [0.70,1.30] clamp) showed +0.022 IS Sharpe, but the **deployable** formula clamped to the live [0.85,1.15] envelope scored **−0.015 vs the incumbent linear L7** (0.25→0.24) — the gain didn't survive a realistic risk envelope (in-sample, N=221). **Decision: keep linear L7.** Future: revisit only with per-signal-varying R:R or an OOS-validated wider envelope. Validate via RISK-3 once N≥50 live trades.
- [~] **R10-8: Per-ticker friction — RESEARCHED, NO backtest change (2026-06-08).** Added the §R10-8 vol-scaled friction validator. **Findings:** (1) realistic large-cap friction ≈0.25% vs the flat 0.50%, i.e. the flat number is a deliberate ~2× conservative buffer — lowering it would manufacture fake Sharpe (0.23→0.30 is *all* lower assumed cost, not alpha), so flat 0.50% is **kept**; (2) the edge is **robust across volatility/spread terciles** (Sharpe 0.29 / 0.34 / 0.30). The backtest can't validate per-ticker friction (no historical fills). Deployable lever is sizing-down wide-NBBO-spread names live — §80 already penalises their *score*; a dedicated sizing lever is deferred (unvalidatable offline). Closing REF-1 TCA→allocator feedback + QENG-3d sim remain the live path.
- [ ] **R10-9: Sector Concentration (7.6 → 10)** — make limits **dynamic/correlation-aware** (size off the live covariance via **REF-5** HRP-in-scanner, not static 30/20%); unblock XLF/XLP/XLU/XLI by training **ML-2** sector XGBoost models that earn them back rather than hard-blocking.

### Product & Deployment
- [ ] **R10-10: Product Completeness (9.3 → 10)** — finish **FE-2** accessibility (WCAG 2.1 AA) and clear the remaining Pre-Launch items that gate user-visible flows (Telegram broadcast, SMTP digests, web push).
- [ ] **R10-11: Frontend (8.8 → 10)** — **FE-2** accessibility + lift Architecture sub-score: typed API client, ≥1 golden-path **ACT-6** E2E green in CI, and a Lighthouse perf budget enforced on PRs.
- [ ] **R10-12: Security Posture (8.0 → 10)** — rotate the **owner password** (Pre-Launch #1) out of source, enforce **HTTPS** (#2), move secrets to a vault/Railway secrets (not committed `.env`), and pass an external dependency + auth pen-test with no highs.
- [ ] **R10-13: Deployment Readiness (7.7 → 10)** — clear Pre-Launch #2/#3/#5/#9 (HTTPS, Stripe webhook, SMTP, VAPID) + **DEPLOY-2** Sentry/UptimeRobot + **DEPLOY-3** automated DB backups; demonstrate a green **ACT-9** CI/CD deploy + a restore-from-backup drill.

### Infrastructure & ML
- [ ] **R10-14: ML Methodology (8.9 → 10)** ⏳gated — deploy the live entry model at **N ≥ 300** (Pre-Launch #7) once AUC delta clears 0.005; ship **REF-6** meta-label feature hardening (VIX term structure/HMM regime/sector momentum) and **ML-2** sector sub-models; require champion/challenger shadow-win before promotion.
- [x] **R10-16: Backend Architecture (8.5 → 9.0)** — **DONE (2026-06-08):** aux-data persistence (gate traces, shadow scores, feature snapshot) now wrapped in a SAVEPOINT in `_persist_scan_signals` so one bad ticker rolls back only its aux data — the core Signal still commits and the cycle continues; also fixed a latent bug where `ModelShadowScore` rows were built but never `db.add`-ed. Added `_async_exception_handler` (installed in lifespan) so unretrieved fire-and-forget task exceptions are logged with task name + traceback instead of swallowed. *Files: [scanner.py](file:///Users/harshv.singh/TradingRecommendationSystem/backend/services/scanner.py), [main.py](file:///Users/harshv.singh/TradingRecommendationSystem/backend/main.py).*
- [ ] **R10-17: Data Pipeline (8.3 → 10)** — prove live reliability, not just breadth: health-scorecard + PIT feature store run a full week with 0 errors; remove the remaining dead `^TRIN`/`^NYAD`/`^BDI`/ETF-fundamentals fetches (or route them to providers that serve them); add **§84** point-in-time data so the pipeline is survivorship-correct.
- [~] **R10-18: Test Coverage (7.5 → 8.0, partial)** — **DONE (2026-06-08):** `tests/test_r10_hardening.py` (8 tests) — NaN/Inf recursive fuzzing on the json writer, the real `save_feature_snapshot` sanitization path, `uq_provider_endpoint` constraint presence, and duplicate-row `record_endpoint_call` resilience (both bug tests fail against the pre-fix code). **Still open:** an end-to-end "scan actually persists a signal + feature snapshot" test against a real (test) Postgres; **TEST-4** mutation testing (>70%); and the missing **§69–§74** gate unit tests.

---

## 👁️ Known Issues
Ongoing known issues or constraints.

- **Default owner password in source**: Critical risk, must be changed before first production user registration.
- **XLF/XLP/XLU/XLI blocked**: Blocks in place due to negative contribution. Requires sector-specific XGBoost retraining to resolve.
- **Calibration recalibration post-A19**: Calibration v4 used pre-A19 data only. Needs recalibration once post-A19 resolved signals accrue.

---

## ✅ Completed Tasks Archive
*Note: All items completed as of v8.1 (2026-06-08) and prior versions.*

<details>
<summary><b>v8.1 Quant Refinements & Decomposition (2026-06-08)</b></summary>

- **REF-1: Dynamic TCA Slippage Feedback** — Fed realized slippage from `fills` and `broker_orders` tables back to dynamically scale down HRP target weights if realized slippage exceeds threshold (42 bps).
- **REF-2: Replay Engine Drift Detection** — Set up `drift_detector.py` comparing live DB signals vs. Replay Engine outcomes using point-in-time snapshots and updated it to copy signal metadata to verify parity and catch data pipeline/logical drift.
- **REF-3: Dynamic Cross-Sleeve Capital Sizing** — Refined the cross-sleeve allocator (`alpha_sleeves.py`) to size sleeve allocations dynamically using rolling 30-day simulated and real out-of-sample Sharpe ratios.
- **REF-4: Causal Cohort Analytics Dashboard** — Added the `/cohort-analytics` API endpoint in `admin.py` to compare empirical win rates, average returns, and Brier scores across randomized cohort groups.
- **REF-5: HRP Scanner Loop Integration** — Wired HRP batch portfolio execution directly into the scanner scan/execution path and implemented `execute_portfolio_for_user()` inside `broker_svc.py` to calculate target sizes, enforce limits, and execute orders.
- **REF-6: Meta-Labeling Feature Hardening** — Expanded the XGBoost meta-label model features with VIX ratio, VIX9D ratio, and sector momentum. Updated `train_metalabel_model.py`, `signal_ml.py`, and `assembler.py` to support 14-feature schemas, and retrained the meta-label model on the new dataset.
- **BE-1. Decompose signal_engine.py** — Decomposed the massive `generate_signal()` sequential scorer into a scoring-context object `ScoringContext` (in `services/engines/context.py`) and scoring blocks (in `services/engines/scorers.py`) to handle state safely with zero regression.
- **R10-15: Signal Engine / Gate Stack (8.5 → 10)** — Completed BE-1, decomposing `generate_signal()` with parity tests and zero behavior change.
</details>

<details>
<summary><b>v8.0 Quant Engine (QENG) Implementation (2026-06-08)</b></summary>

- **QENG-1a: Research experiment registry** — Added a `ResearchExperiment` table/log for every screener, parameter sweep, gate ablation, ML training run, and factor-mining run.
- **QENG-1b: Combinatorially symmetric cross-validation / PBO report** — Added a `--pbo` report for strategy variants and factor-mining outputs to calculate Probability of Backtest Overfitting.
- **QENG-1c: Model/policy promotion checklist** — Required every promoted gate/model to have registry entry, locked OOS universe, replay result, live shadow result, cost-adjusted result, rollback plan, and expiration/retest date.
- **QENG-2a: Point-in-time feature store** — Persisted immutable feature snapshots keyed by ticker, observation time, effective time, provider timestamp, retrieval time, provider, adjusted/raw values, feature vector hash, and signal policy version.
- **QENG-2b: Event-driven as-of replay engine** — Built a replay harness that runs the same live `generate_signal()` + delivery gates against historical point-in-time feature snapshots.
- **QENG-2c: Dataset/version lineage** — Versioned data pulls and feature transforms so every backtest, ML model, calibration run, and signal can be traced to exact inputs.
- **QENG-3a: Live fill ledger** — Extended `BrokerOrder` into full order/fill/event tracking: NBBO mid, spread, route/order type, requested qty, filled qty, average fill, fees, and final execution status.
- **QENG-3b: Transaction Cost Analysis service** — Computes realized slippage, spread capture, implementation shortfall, and cost by ticker/time/spread. (Implemented in `services/tca_service.py`).
- **QENG-3c: Capacity and participation limits** — Added per-ticker capacity estimates using ADV, spread, volatility, and realized fill quality. Sizes down trades when expected implementation shortfall consumes the signal edge.
- **QENG-4a: Portfolio allocator service** — Built allocator converting active signals into orders under cash, exposure, covariance, turnover, cost, and concentration constraints. (Implemented in `services/portfolio_allocator.py`).
- **QENG-4b: Hierarchical Risk Parity baseline** — Implemented HRP/risk-budgeting as the robust first allocator, benchmarked against equal weight.
- **QENG-4c: Cost-aware turnover control** — Added no-trade bands / buy-hold spread logic so small expected-edge changes do not trigger unnecessary churn.
- **QENG-5a: PCA/ETF residual stat-arb sleeve** — Researched Avellaneda-Lee style residual mean reversion (regress stocks on sector ETF/PCA factors, trade residual z-scores with OU half-life and stationarity filters). (Implemented in `services/alpha_sleeves.py`).
- **QENG-5b: Time-series momentum / trend sleeve** — Added trend momentum tracking for SPY/QQQ/TLT/GLD/DXY/HYG to diversify mean-reversion focus.
- **QENG-5c: Lower-turnover cross-sectional factor sleeve** — Added factor ranking based on blended Value, Quality, and Momentum features.
- **QENG-5d: Cross-sleeve capital allocator** — Allocates capital dynamically across MR, residual stat-arb, trend, and factor sleeves based on live Sharpe confidence.
- **QENG-6a: Operationalize triple-barrier meta-labeling** — Operationalized ML prediction within `signal_ml.py` to screen signals when meta-label probability is low.
- **QENG-6b: Shadow-control framework** — Logged policy version and assignments (`delivered`, `paper-only`, `withheld-control`, `challenger-policy`) to causally measure gate changes.
- **QENG-6c: Policy versioning in every signal** — Persisted scoring version, gate version, calibration version, ML model ids, and allocator version in each signal row.
- **Lineage and Cohort Service Version Bump** — Updated `cohort_service.py` and `lineage.py` to `v8.0` with 1871 passing tests.
</details>

<details>
<summary><b>v7.8 Hardening & Targeted Systems (2026-06-08)</b></summary>

- **TSYS-1: Auth, OAuth & Account Hardening** — OAuth state/nonces persisted in Redis/DB with TTL (1a); repeated failed login locks accounts and writes an audit trail (1b); active device/session revocation APIs added (1c); email change requires double confirmation (1d).
- **TSYS-2: Billing & Subscription Entitlements** — Nightly Stripe entitlement reconciliation job implemented (2a); explicit grace periods and dates surfaced in UI (2b); full billing audit log in place (2c); security check that checkout updates only the authenticated owner (2d).
- **TSYS-3: Notifications, Webhooks & Delivery** — Delivery receipt table tracking provider statuses added (3a); exponential backoff queues for failed deliveries (3b); quiet-hours and timezone preferences added (3c); signing-secret rotation and test endpoint for user webhooks (3d).
- **TSYS-4: Scanner & Worker Hardening** — Background jobs logs persisted (4a); scan-cycle ID attached to all generated entities (4b); distributed singleton locks for scanners and workers (4c); API quota usage and fallback telemetry logged (4d).
- **TSYS-5: Market Data Reliability** — Provider health scorecard tracking errors and latency (5a); raw responses saved for schema-drift checking (5b); corporate-action split/dividend adjustment validation (5c); rate-limit budget tracking (5d).
- **TSYS-6: Signal Engine Explainability** — Machine-readable gate trace stored for every signal (6a); central gate registry created (6b); config versioning for signals (6c); gate decomposition parity tests (6d).
- **TSYS-7: Calibration & Model Operations** — Model registry artifact created (7a); feature schema validation before inference (7b); shadow scoring for challenger models (7c); calibration rollback support (7d).
- **TSYS-8: Backtests & Outcome Analytics** — Outcome resolver audit log (8a); path snapshots stored (8b); analytics cache invalidation (8c); analytics validation consistency checks (8d).
- **TSYS-9: Broker & Risk Management** — Broker reconciliation jobs (9a); user-level runtime risk limits (9b); paper/live parity dashboard (9c); credential encryption key rotation (9d).
- **TSYS-10: Admin & Observability** — Incident timeline tracking (10a); `/api/admin/system-readiness` endpoint (10b); Prometheus/OpenTelemetry metrics export (10c); alert thresholds configured (10d).
- **TSYS-11: Frontend & Mobile UX** — Execution preview screen (11a); stale-data UI indicators (11b); version badges in analyst views (11c); frontend-backend contract validation tests (11d).
- **TSYS-12: Database & Migrations** — Alembic production policy (12a); table data retention rules (12b); hot-path indexing (12c); migration smoke testing (12d).
- **TSYS-13: Compliance & Legal** — Language audit on regulated advice (13a); suitability and risk warnings in UI (13b); immutable admin action logs (13c); GDPR account deletion verifier (13d).
</details>

<details>
<summary><b>Prior Versions (v7.4 - v7.7, June 2026)</b></summary>

- **Multi-Broker Integration (IBKR)** — Integrated Interactive Brokers Client Portal REST API into `services/ibkr_rest.py`. (v7.7)
- **Active Share Buyback Window (§75)** — Parsing of EDGAR 8-K filings for active repurchase announcements. (v7.7)
- **HTTP Latency Pass** — Wired cached TLS and pooled session reuse across 20 modules via `services/http_client.py`. (v7.7)
- **Playwright E2E Golden Path** — Created automated end-to-end user path tests in `tests/e2e/test_golden_path.py`. (v7.5)
- **Interactive Broker Connections UI** — Modal forms for user connection/settings, auto-execution settings, and live warnings. (v7.5)
- **Emergency Kill Switch** — `AppSettings`-based immediate scan loop pause. (v7.4)
- **Babel Removal** — Replaced Babel build chain with modern fast esbuild targets. (v7.5)
- **Signal Notification Preferences** — Persisted settings for user score/sector/action notification filters. (v7.5)
- **Admin Analytics Dashboard** — Structured analytical API reporting signal volumes, Wilson confidence intervals, and Brier scores. (v7.5)
</details>
