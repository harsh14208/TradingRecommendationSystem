# Signal.Trade — TODO

## 🔴 Pre-Launch Checklist
These are critical tasks that must be completed before public launch or marketing scale.

- [ ] **1. Change owner password** — `backend/.env`: set `OWNER_PASSWORD=<16+ chars, mixed case, symbols>`. Default `ChangeMe123!` is committed to source. *Risk: instant account takeover.*
- [ ] **2. Deploy to public HTTPS URL** — Run `railway up` or `fly deploy`. Set `APP_URL=https://your-app.up.railway.app`. *Risk: Stripe webhooks 404, OAuth callbacks broken, HTTPS-only cookies not sent.*
- [ ] **3. Configure Stripe billing** — `STRIPE_SECRET_KEY` and price IDs set. Still needed: register webhook in Stripe Dashboard, copy `whsec_...` to `STRIPE_WEBHOOK_SECRET`. (Note: startup now logs CRITICAL if `STRIPE_WEBHOOK_SECRET` is empty in prod; webhook handler returns 500 explicitly). *Risk: checkout completes but tier never activates.*
- [ ] **4. Register Telegram webhook** — After HTTPS deploy: `curl -X POST <https://your-app>/api/telegram/set-webhook`. *Risk: subscribers cannot link Telegram.*
- [ ] **5. Configure SMTP (email)** — Add `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` to `.env`. *Risk: no email verification, no password reset, no weekly digest.*
- [ ] **6. Enable Telegram broadcast channel** — Create private channel, make bot admin, add `TELEGRAM_BROADCAST_CHANNEL_ID=-100...`. *Risk: at >50 subscribers, per-user DM loop hits Telegram rate limit.*
- [ ] **7. Train and deploy XGBoost ML model** — After ≥300 resolved signals: `POST /api/ml/train`. *Risk: missing +5–8pp win rate improvement.*
- [ ] **8. Configure Google OAuth** — `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`.
- [ ] **9. Configure VAPID web push** — Generate keys via py_vapid. *Risk: no browser push notifications.*
- [ ] **10. Set up Cloudflare CDN** — Point DNS to Railway/Fly. *Risk: slower global load.*
- [ ] **11. Google AdSense** — Apply at adsense.google.com. *Risk: no ad revenue from free tier.*
- [ ] **12. Add Redis in Production** — `railway add --plugin redis`. *Risk: redundant API calls under concurrent load.*
- [ ] **13. Upgrade SendGrid** — Essentials (~$20/mo) before daily signups + resets exceed 100 emails/day.

---

## 🔄 Refinement Tasks — Improving Existing Features
The following items target refining and polishing existing capabilities to their maximum efficiency without bloating the system with unnecessary new features.

- [ ] **REF-1: Dynamic TCA Slippage Feedback**
  - *Description*: Feed realized slippage computed by `tca_service.py` back into the backtester friction model and the position allocator. If a ticker/sector exhibits persistently higher slippage than expected in live fills, dynamically scale down its target portfolio weight or adjust its entry threshold.
  - *Target Files*: [tca_service.py](file:///Users/harshv.singh/TradingRecommendationSystem/backend/services/tca_service.py), [portfolio_allocator.py](file:///Users/harshv.singh/TradingRecommendationSystem/backend/services/portfolio_allocator.py), and backtesting scripts.
- [ ] **REF-2: Replay Engine Drift Detection**
  - *Description*: Set up an automated weekly script to compare historical live signals (and their feature states) against the event-driven replay engine. Flag any parameter, score, or decision discrepancies to verify parity and catch data pipeline/logical drift.
  - *Target Files*: Replay engine tests / new monitoring scripts.
- [ ] **REF-3: Dynamic Cross-Sleeve Capital Sizing**
  - *Description*: Refine the cross-sleeve allocator (`alpha_sleeves.py`) to dynamically size capital allocations using rolling 30-day out-of-sample Sharpe ratios and drawdown statuses (e.g. dynamic Kelly or risk-parity budgeting) instead of the static Sharpe confidence allocation.
  - *Target Files*: [alpha_sleeves.py](file:///Users/harshv.singh/TradingRecommendationSystem/backend/services/alpha_sleeves.py).
- [ ] **REF-4: Causal Cohort Analytics Dashboard**
  - *Description*: Build a dedicated admin dashboard view to compare empirical win rates, average returns, and Brier scores across randomized cohort groups: `delivered`, `withheld` (control), and `shadow` (challenger policies). This will validate the actual treatment effect of newly promoted policy versions.
  - *Target Files*: Frontend/Admin views, router files.
- [ ] **REF-5: HRP Scanner Loop Integration**
  - *Description*: Integrate the Hierarchical Risk Parity (HRP) allocator dynamically into the main real-time scan/execution loop. Currently, the allocator is standalone; it should guide live order sizing based on the covariance of the scanned candidates.
  - *Target Files*: Scanner / worker processes.
- [ ] **REF-6: Meta-Labeling Feature Hardening**
  - *Description*: Expand the features used in the XGBoost meta-labeling model (`signal_ml.py`) by feeding in macro/regime indicators directly (e.g., VIX term structure, HMM macro regimes, and sector momentum metrics) to refine the classifier's probability calibration.
  - *Target Files*: [signal_ml.py](file:///Users/harshv.singh/TradingRecommendationSystem/backend/services/signal_ml.py).

---

## 🎯 Active Research & Alpha TODOs
These are targeted research and statistical modeling opportunities to improve signal edge.

- [ ] **§85-2. Audit EDGAR MD&A sentiment contribution** — `edgar.py` MD&A NLP is annual 10-K data applied to a 5-day trade. Tag live signals that received an MD&A score adjustment and compute ΔWR. If no improvement, disable. Low priority until §85-1 data is available.
- [ ] **§62. VRP per-stock** — Needs per-stock IV history (Polygon Options upgrade, ~$79-199/mo). High IVR (>80th percentile) at oversold MR entry should add an additional +6pp.
- [ ] **§84. Survivorship bias correction** — Purchase EODHD (~$20/mo) or Norgate ($33/mo) delisted constituent lists. Add delisted tickers to `TICKERS` for their active periods to make IS -> OOS gap more honest.
- [ ] **Options flow confirmation gate** — Subscribe to Unusual Whales API (~$50/mo). Enter only when options flow confirms setup (e.g. large put sweeps → −10pp, large call sweeps on oversold → +8pp). Expected ΔSharpe: +0.15–0.25.
- [ ] **GEX support levels** — SpotGamma API (~$99/mo). Enter only when `price ≤ gex_support_level × 1.01` to ensure dealer positioning reinforces mean reversion. Expected ΔSharpe: +0.10.
- [ ] **Market-neutral beta hedge** — Short 0.9× position value in SPY at entry. Requires margin account. (QuantEngine validated: IS Sharpe 0.29 = 0.12 pure alpha + 0.17 beta. True forward estimate ≈ 0.10–0.15).

---

## ⚙️ Operational, Deployment & Testing TODOs
Infrastructure, testing, and system-level follow-ups.

- [ ] **BE-1. Decompose signal_engine.py** — Decompose the ~5.2k-line `generate_signal()` sequential scorer into a scoring-context object to handle shared mutable state safely without risking regression.
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

## 👁️ Known Issues
Ongoing known issues or constraints.

- **Default owner password in source**: Critical risk, must be changed before first production user registration.
- **XLF/XLP/XLU/XLI blocked**: Blocks in place due to negative contribution. Requires sector-specific XGBoost retraining to resolve.
- **Calibration recalibration post-A19**: Calibration v4 used pre-A19 data only. Needs recalibration once post-A19 resolved signals accrue.

---

## ✅ Completed Tasks Archive
*Note: All items completed as of v8.0 (2026-06-08) and prior versions.*

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
