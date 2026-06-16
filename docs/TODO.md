# Signal.Trade — TODO

---

## 🔴 Pre-Launch Checklist
Critical tasks that must be completed before public launch or marketing scale.
Completed items (#1, #2, #2a, #9, #10) are archived below.

- [ ] **3. Configure Stripe billing** — `STRIPE_SECRET_KEY` and price IDs set. Still needed: register webhook in Stripe Dashboard, copy `whsec_...` to `STRIPE_WEBHOOK_SECRET`. (Note: startup now logs CRITICAL if `STRIPE_WEBHOOK_SECRET` is empty in prod; webhook handler returns 500 explicitly). *Risk: checkout completes but tier never activates.*
- [ ] **4. Register Telegram webhook** — After HTTPS deploy: `curl -X POST <https://your-app>/api/telegram/set-webhook`. *Risk: subscribers cannot link Telegram.*
- [ ] **5. Configure SMTP (email)** — Add `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` to `.env`. *Risk: no email verification, no password reset, no weekly digest.*
- [ ] **6. Enable Telegram broadcast channel** — Create private channel, make bot admin, add `TELEGRAM_BROADCAST_CHANNEL_ID=-100...`. *Risk: at >50 subscribers, per-user DM loop hits Telegram rate limit.*
- [x] **8. Configure Google OAuth** — `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`.
- [ ] **11. Google AdSense** — Apply at adsense.google.com. *Risk: no ad revenue from free tier.*
- [ ] **12. Add Redis in Production** — `railway add --plugin redis`. *Risk: redundant API calls under concurrent load.*
- [ ] **13. Upgrade SendGrid** — Essentials (~$20/mo) before daily signups + resets exceed 100 emails/day.

---

## 🟢 Live Trading Readiness Checklist

These gates must be cleared before broker auto-execute is enabled with real money.
They are separate from public-launch readiness; a launched product can (and should)
remain on paper trading until the empirical bar is met.

- [ ] **LIVE-1. Paper track record** — ≥ 100 resolved paper trades or ≥ 3 months of auto-execution on Alpaca paper.
- [ ] **LIVE-2. Live win rate > 55%** — Clean delivered BUY win rate from `/api/admin/live-wr-stats` over ≥ 100 resolved signals. **Diagnosis 2026-06-15 (`gate_contribution_analysis.py`, N=570): baseline 43.7%; edge is sector-concentrated — XLK 54.4% is the only sector >50%** (XLF 34, XLP 30, XLV 41, XLI 36). Addressed via sector-specific calibration (R10-6) rather than hard blocks; the real fix is upstream entry alpha (orthogonal data) or narrowing to tech-MR.
- [ ] **LIVE-3. Calibration check** — Brier ≤ 0.30 and confidence gap ≤ 10pp on the backtest calibration tab.
- [ ] **LIVE-4. Risk limits configured** — `max_daily_orders`, `max_ticker_notional`, `auto_execute_qty_dollars`, `auto_execute_min_conf` set conservatively.
- [ ] **LIVE-5. Drawdown simulation** — Simulated max DD < 10% at intended live size.
- [ ] **LIVE-6. Kill switch tested** — `POST /api/admin/signals/pause` executed and verified from a mobile device.
- [ ] **LIVE-7. Risk acknowledgement recorded** — `POST /api/me/risk-acknowledge` called and `risk_acknowledged_at` populated.
- [ ] **LIVE-8. Live broker keys verified** — `/api/me/broker/status` returns `connected: true` for a live Alpaca/IBKR account.
- [ ] **LIVE-9. Decay monitor green** — No `"decay"` alarm from `scripts/decay_monitor.py` for 30 consecutive days.
- [ ] **LIVE-10. First-live day protocol** — Start with $100/trade, max 3 daily orders, 75% min confidence; review fills at market close.

> **Do not enable live auto-execute until LIVE-1 through LIVE-8 are complete.**
> See [RUNBOOK.md](RUNBOOK.md) §7, [HOWTO.md](HOWTO.md) §11, and the single-user localhost checklist in [`SINGLE_USER_LIVE_CHECKLIST.md`](SINGLE_USER_LIVE_CHECKLIST.md) for detailed procedures.

---

## 🚀 Next Sprint (2026-06-12)
Actionable items still open. Completed sprint items are archived below.

### Security & Auth (do first — blocking everything else)
- [ ] **SP1-2. Configure SMTP** — Add `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` to `.env` (SendGrid free tier is enough to start). Test: trigger password-reset flow for owner account. Unblocks: email verification, weekly digests, password resets. *Risk: users who forget passwords have no recovery path.*

### Observability & Pipeline
- [x] **SP1-3. Sentry DSN signup & verification** — DSN added to `backend/.env`. Fixed `main.py` to load `.env` at import time before the Sentry SDK init, restarted the `com.signal.trade` LaunchAgent, and verified `/api/health/sentry` returns `configured:true` with a real `event_id`.

### Scale & Delivery (before first paying user)
- [ ] **SP1-5. Enable Telegram broadcast channel** — Create private Telegram channel, add bot as admin, set `TELEGRAM_BROADCAST_CHANNEL_ID=-100...` in `.env`. Test: send one broadcast signal, confirm it posts to the channel. Unblocks: scaling past 50 subscribers without hitting Telegram rate limits.

### Revenue & Growth (parallel track)
- [ ] **SP1-7. Apply for Google AdSense** — 10-minute form at adsense.google.com. Use `signal.trade` domain. Approval takes 1–14 days; starting now removes a future blocker.

---

## 🎯 Active Research & Alpha TODOs
Targeted research and statistical modeling opportunities to improve signal edge.
Items marked [~] are partially wired but not yet proven/deployed.

### External-research agenda — §96–§103
- [ ] **§98. ORATS one-month sprint** — make §62/§48/§49 historically testable for the first time (PAID ~$99 one-off, time-boxed).
- [ ] **§102. Tick-size regime change watch** — SEC half-penny quoting + access-fee cut Nov 2026 calendar item.

### Free alt-data agenda — §104–§110 / follow-ups
- [ ] **§104c. FINRA SV forward path only** — keep SPRT ID 8 for the pre-registered definition; optionally register the −10/40 variant as a NEW explicitly-exploratory forward SPRT; the panel's real reuse is the cross-sectional model (§86/§100 harness).
- [ ] **§111. Cross-sectional model → LIVE promotion gates** — Promotion criteria locked; activation must come from `check_promotion_criteria()` returning True, not a manual override. **BUGFIX 2026-06-15:** the shadows had been accruing **ZERO** data since 2026-06-09 — `_price_features` needs ≥253 daily bars (12-1 momentum `close.shift(252)`) but the scan fetched `period="1y"` (≈251 bars), so `score_batch()` returned `{}` every scan and no signal was ever tagged (verified: 0 signals carry `xs_shadow_pct`). Fixed: `scanner.py` batch history `1y→2y` (verified: full 173-ticker watchlist now returns 173 percentiles vs 0 at 1y). Forward accrual toward the 150-signal gate begins from the next directional scan; counter is still at 0, so the prior "accruing forward data" status was false.
  - [ ] §111a. Tier 1 sizing haircut on existing signals (h=21).
  - [ ] §111b. Tier 1 for h=63 (independent N≥150 clock).
  - [ ] §111c. Tier 2 standalone dollar-neutral L/S book.
  - [ ] §111d. Kill criteria after 12 months if neither passes.
- [ ] **§119. Point-in-time survivorship-bias correction** — Paid EODHD/Norgate path; required before claiming IS/OOS above 8/10 rating.

### Next-best alpha-improvement candidates — §112–§119
- [~] **§91. Short-interest rising-SI sizing tilt** — wired, live read positive (+2.42pp spread, N=335), backtest unvalidatable (pre-2017). Deploy gate: live resolved N≥50 with rising SI.
- [~] **§86. Market-Neutral Cross-Sectional Ranking Architecture** — v1 built and deployed in SHADOW mode. Nested h=63 WF net +0.576 [90% CI +0.22, +0.91]; live promotion gated by §111.
- [ ] **§62. VRP per-stock** — Needs per-stock IV history (Polygon Options upgrade, ~$79-199/mo).
- [ ] **§84. Survivorship bias correction** — Purchase EODHD (~$20/mo) or Norgate ($33/mo) delisted constituent lists.
- [ ] **Options flow confirmation gate** — Subscribe to Unusual Whales API (~$50/mo).
- [ ] **GEX support levels** — SpotGamma API (~$99/mo).
- [ ] **Market-neutral beta hedge** — Short 0.9× position value in SPY at entry. Requires margin account.

> **Critical invariant:** the IS Sharpe ceiling appears spent (Deflated Sharpe fails at 744 trials). Future edge must come from orthogonal data (options flow, short-interest velocity, cross-sectional ranking) or execution cost reduction, not more OHLCV parameter sweeps.

---

## ⚙️ Operational, Deployment & Testing TODOs

- [ ] **ACT-7. Validate bracket stop in Alpaca paper account** — Enable auto-execution for owner account on paper, trigger a manual signal delivery, and verify Alpaca dashboard shows bracket order legs correctly.
- [~] **ACT-8. Install shap for ML-5 live audit** — `shap` installed in `.venv311` (0.49.1). Re-run live audit remains gated on ≥200 post-§82 (≥2026-05-29) resolved signals.
- [x] **OPS-2. Frontend accessibility pass** — axe-core audit of `/app` reports 0 violations across the default dashboard, expanded signal rows, and the Tweaks/settings panel. Color-contrast tokens now meet WCAG AA in both dark and light themes, modal backdrops no longer create nested-interactive controls, chart canvases have accessible names, and form inputs in Tweaks are labeled.
- [x] **OPS-4. Watchdog self-heal for unloaded LaunchAgents (2026-06-13)** — `scripts/watchdog.sh` now auto-reloads (`launchctl bootstrap`) any critical agent found UNLOADED (`com.signal.trade`, `keepawake`, `cloudflared`) — the state `KeepAlive` cannot recover from. Waits up to 60s for backend warm-up before judging health; a loaded-but-hung backend stays alert-only (never auto-kills a busy process); self-heals are logged as `OK (self-healed: …)`. Validated end-to-end by booting out `keepawake` and confirming restore. Triggered by the 2026-06-13 ~25-min outage (commit `51dae3f`).
- [ ] **OPS-5. Root-cause the 2026-06-13 10:16 PT backend unload** — `com.signal.trade` shut down *cleanly* (graceful `Application shutdown complete`, not a crash) and was then booted out of launchd, so `KeepAlive` couldn't restart it; recovered manually via `launchctl bootstrap`. Source of the `bootout` is unknown (manual `launchctl`, logout/login, OS/update event, or a script). If it recurs, check `log show --predicate 'process == "launchd"' --last 1h` around the unload timestamp and Console for system events. OPS-4 now auto-recovers it regardless, but the trigger should be identified.

---

## 📊 Live Findings & Calibration TODOs

- [ ] **WATCH-1. XLV Healthcare live WR contradicts IS promotion (2026-06-09, N=62).** Re-check at N≥100; if still <45%, reconsider the IS promotion / add to watch-block.
- [ ] **OOS-1. Accumulate ≥30 live trades in OOS v7 tickers** — SYK, RMD, IDXX, ZBH, RL, DECK, POOL, NDAQ, CBOE, BR. Run `python scripts/backtest_technicals.py --oos`. If OOS v7 CLEAN Sharpe ≥ 0.10, promote to IS.
- [ ] **OOS-2. Accumulate ≥30 live trades in OOS v8 tickers** — LNC, AMG, PAYC, SIG, AEO. Cautiously evaluate the 0.2% Russell 2000 pass rate.
- [ ] **§85-2b. MD&A sentiment live monitoring (2026-06-09)** — tag signals that receive `mda_delta != 0` and compute ΔWR after N≥50 such signals accumulate.
- [ ] **CAL-1 / A25. Calibration v5** — Run `python scripts/backfill_confidence.py --force --apply` when ≥200 post-§82 (≥2026-05-29) resolved signals are available.
- [ ] **ML-2 / A15. Sector-specific XGBoost models** — Retrain sub-models for concentrated sectors when sector-specific resolved signals reach ≥200.
- [ ] **RISK-3. Position sizing live audit** — After N≥50 auto-executed trades, compare realized notional vs theoretical scaling.
- [ ] **ACT-3. Sector-conditional calibration (CAL-V5)** — Run `backfill_confidence.py --force --apply` with sector grouping.
- [ ] **ACT-4. Investigate live WR gap (Part b)** — Detailed validation on the remaining gap between live WR and IS WR after resolving EOD-batch delivery bugs.

---

## 🏁 Path to 10/10 — Per-Aspect Rating TODOs
Concrete work to take each [Stats.md §15](Stats.md#L359) rating aspect to 10/10.
Aspects marked **⏳gated** cannot reach 10 by code alone.

### Signal & Research
- [ ] **R10-1: IS Backtest Accuracy (7.9 → 10)** ⏳gated — complete §84 (EODHD/Norgate delisted constituents) + ACT-5 full flag-validation sweeps + `--pbo` CSCV report showing PBO < 5%. **PBO measured 2026-06-13: `--pbo` ran clean (after fixing a `simulate_ticker` crash on missing `ff_str`/`sector_momentum` date keys — bare `float(None)`); BUY_THRESH 45–55 sweep over S=8 CSCV partitions → PBO = 0.200 (WARNING, > 0.15 code bar and > 0.05 target). Test-rank dist P10/P50/P90 = 9.1%/100%/100% (bimodal: selected param is usually OOS-best but bottom-half in ~20% of folds). Registered as `ResearchExperiment` ID 12. The PBO sub-task does NOT pass; consistent with the spent-IS-lever finding. R10-1 remains gated by §84 regardless.**
- [ ] **R10-2: OOS / Forward Validation (6.5 → 10)** ⏳gated — accrue resolved signals to N ≥ 387 via OOS-1 + OOS-2; expanding walk-forward with OOS CLEAN Sharpe ≥ 0.10.
- [ ] **R10-3: Live Alpha Quality (7.0 → 10)** ⏳gated — run §85-1 audit (≥200 resolved) and prove causally positive treatment effect via REF-4 cohort dashboard.
- [ ] **R10-4: Gate Stack §47–§83 (8.8 → 10)** ⏳gated — wire §62 VRP per-stock, options-flow, and GEX confirmation gates (all need paid options data).
- [~] **R10-5: Backtest Infrastructure (7.8 → 10)** — ~~zero PIT feature-store persist errors~~ **DONE (2026-06-13): hot-scalar extraction in `feature_store.save_feature_snapshot()` now routes all 7 indexed columns through `_safe_float()` (coerces to a finite float or None), so a malformed provider value ("N/A", wrong type, non-finite) nulls the column instead of raising `ValueError`/`TypeError` and aborting the snapshot — closes the persist-error class that `_json_safe` only covered for the JSON column. Also fixed `atr_pct`/`quality_score` falsy-`0.0` fallthrough (was `a or b`). Regression tests added in `tests/test_r10_hardening.py`.** **REF-2 audit + wiring DONE (2026-06-13): audit found the archive overstated it — `scripts/drift_detector.py` existed but was a manual script only (no scheduler, no launchd plist, no test; the `drift` hits in `main.py` were all provider-schema/ML-feature drift, a different feature). Refactored `detect_drift()` to return a structured result dict (no more `sys.exit` in the core path; CLI `main()` keeps the exit code), wired a supervised weekly job `_weekly_drift_detection` in `main.py` (Sun 11:30am ET, after ML retrain; non-zero drift → `log.error` so it surfaces in Sentry), and added a controlled regression test in `tests/test_qeng_features.py`.** Remaining: fold §84 point-in-time data (⏳gated).
- [~] **R10-6: Confidence Calibration (7.9 → 10)** — **ACT-3 per-sector isotonic curves DONE (2026-06-15):** sector-specific calibration in `calibration.py` (sector→regime→global priority), built across all resolved (sector from `SECTOR_MAP` since ~81% null `sector_etf`); weak sectors calibrate below the floor (no hard block), XLK ~56% delivers. Also fixed calibration being **silently off** — the self-gate's single temporal split false-rejected a CV-skilled map; now gates on K-fold CV (Brier 0.244 < 0.25 → deployed). Caveat: built on the full window incl. pre-§82 — refresh once post-§82 per-sector N≥40 accrues. Remaining: CAL-1 Calibration v5 refresh on ≥200 post-§82 (≥2026-05-29) signals ⏳gated (12/200, ~16 wks).

### Risk & Execution
- [ ] **R10-9: Sector Concentration (7.6 → 10)** — make limits dynamic/correlation-aware via REF-5 HRP-in-scanner; unblock XLF/XLP/XLU/XLI via ML-2 sector XGBoost models.

### Product & Deployment
- [ ] **R10-10: Product Completeness (9.3 → 10)** — finish FE-2 accessibility (WCAG 2.1 AA) and clear Pre-Launch items gating user-visible flows.
- [~] **R10-11: Frontend (8.8 → 10)** — FE-2 accessibility **DONE** (2026-06-12, 0 axe-core violations on /app) + Lighthouse perf budget **GREEN locally (2026-06-13)**: `.lighthouserc.js` asserts error-level thresholds calibrated to the heavy `/app` dashboard (FCP ≤3500 ms, LCP ≤12000 ms, CLS ≤0.05, TBT ≤200 ms, performance ≥0.65, accessibility ≥0.95, best-practices ≥0.93) and a `lighthouse` job added to CI with authenticated Puppeteer login. Thresholds are intentionally generous until the dashboard is code-split/lazy-loaded. Remaining: typed API client + ≥1 golden-path ACT-6 E2E green in CI.
- [ ] **R10-12: Security Posture (8.0 → 10)** — rotate owner password out of source, enforce HTTPS, move secrets to vault/Railway secrets, pass auth pen-test.
- [ ] **R10-13: Deployment Readiness (7.7 → 10)** — clear Pre-Launch #2/#3/#5/#9 + DEPLOY-2 Sentry/UptimeRobot + DEPLOY-3 automated backups; green deploy + restore drill.

### Infrastructure & ML
- [~] **R10-14: ML Methodology (8.9 → 10)** ⏳gated — live entry model at N ≥ 300 once AUC delta clears 0.005; ML-2 sector sub-models pending; champion/challenger shadow-win required.
- [~] **R10-17: Data Pipeline (8.3 → 10)** — dead fetches removed; remaining: 1-week zero-error health scorecard + PIT store + §84 PIT data.
- [~] **R10-18: Test Coverage (7.5 → 8.0, partial)** — ~~true end-to-end Postgres test~~ **DONE (2026-06-13): `tests/test_postgres_e2e.py` runs a real multi-table round-trip (Instrument ← Signal ← FeatureSnapshot) against actual PostgreSQL — builds its own engine from `TEST_POSTGRES_URL` in a throwaway schema (never touches the DISC-5-guarded global SQLite engine; safe against a dev DB), and asserts a Postgres-only behavior SQLite physically cannot catch: the `json` column rejecting raw `NaN` (the production crash class), proving `_json_safe` is load-bearing. Verified PASS against `postgres:16-alpine` in Docker; auto-skips when `TEST_POSTGRES_URL` is unset/unreachable so the SQLite suite stays green. CI `test` job now provides a `postgres:16-alpine` service + `TEST_POSTGRES_URL` so the path is exercised on every run, not skipped.** ~~TEST-4 mutation testing (>70%)~~ **RUN (2026-06-13): mutmut now executes cleanly for `services/delivery_gates.py` after fixing the sandbox import (`also_copy`) and adding `mutate_only_covered_lines` + `do_not_mutate_patterns` for logging/reason-string lines. Score: 28/92 killed (30.4%); target >70% not yet met. Remaining survivors are condition/operator mutants in exception-handling / logging branches and higher-level gating logic that need additional focused boundary tests.

---

## 👁️ Known Issues

- **XLF/XLP/XLU/XLI blocked** — Hard blocks remain in place due to negative contribution. Sector-specific unblocking is now gated by an explicit QENG-1c promotion record (§117 infrastructure complete); training/promotion requires ≥100 resolved backtest trades per sector.
- **Calibration recalibration post-§82** — Calibration v4 used pre-A19 data only. Needs recalibration once post-§82 resolved signals accrue.

---

## ✅ Completed Tasks Archive

<details>
<summary><b>v8.8.4 Sprint Close-out (2026-06-12)</b></summary>

### Pre-Launch
- **#1 Owner password** — fixed 2026-06-09 (32-char secure password; startup fails on `ChangeMe123!` in prod).
- **#2 Deploy to public HTTPS URL** — public HTTPS served via Cloudflare Tunnel to `signaltrade.org` and `app.signaltrade.org`; `APP_URL=https://signaltrade.org` set and backend reloaded.
- **#2a Verify DNS + tunnel** — Cloudflare authoritative NS and `1.1.1.1` resolve both domains; tunnel connector healthy; `/api/health/uptime` returns 200 via public URL.
- **#9 VAPID web push** — keys generated via `py_vapid`, added to `.env`, `config.py` reads correctly.
- **#10 Cloudflare CDN** — traffic proxies through Cloudflare (orange-clouded A/CNAME records); caching + DDoS + SSL active at edge.

### Sprint SP1
- **SP1-3 Sentry SDK wired** — `sentry-sdk[fastapi]` added, integrations initialized in `main.py`, `/api/health/sentry` endpoint added. Remaining: signup + DSN paste.
- **SP1-4 Push to GitHub & verify CI** — pushed v8.8.4 to `main`; CI run passed ruff, pytest, 25% coverage floor, gitleaks, pip-audit, npm audit. Missing `dist/` bundles fixed by adding `npm install && npm run build`.
- **SP1-6 Add Redis** — local `redis:7-alpine` container on `localhost:6379`, `REDIS_URL` set, LaunchAgent added; test isolation fixed.

### Operational
- **DEPLOY-2 Public health endpoint + local watchdog** — `GET /api/health/uptime` added; `scripts/watchdog.sh` + LaunchAgent alert if backend/tunnel agents die.
- **DEPLOY-3 DB Backups (local)** — `scripts/backup_db.sh` with `sqlite3 .backup`; daily LaunchAgent keeps 7 days.
- **DEPLOY-3a Log rotation** — `scripts/rotate_logs.sh` + LaunchAgent keeps 14 days compressed.
- **OPS-1 Remove dead ^BDI fetch** — `_fetch_bdi()` returns `None` instead of hitting unavailable yfinance ticker.
- **OPS-2 Frontend accessibility pass (partial)** — fixed missing button labels and one nested-interactive violation; 147 color-contrast items remain.
- **OPS-3 Kill-switch endpoint tests** — added status/toggle/create/403 tests in `tests/test_routers_admin_unit.py`.
- **ACT-9 Push to GitHub for CI/CD validation** — pushed; CI passed.

### Research & Alpha
- **§112 CBOE options IV history** — snapshot accumulation wired; validation gated on ≥252 nightly snapshots.
- **§113 FINRA ATS dark-pool participation** — weekly `ats_ratio` merged with 2-week PIT lag; historical backfill blocked by endpoint.
- **§114 SEC FTD panel** — backfilled to 2004 + velocity feature; ablated, no edge.
- **§115 NAAIM/UMCSENT regime sizing** — backfilled + ablated, no edge.
- **§116 Wikipedia pageviews attention spike** — backfilled + ablated, no edge at 4% coverage.
- **§117 Sector-specific XGBoost promotion gate** — `services/sector_ml_promotion.py` SSoT; promotion requires `ModelRegistry` + `ResearchExperiment` record; training bar raised to ≥100 samples; tests pass.
- **§118 Live realized-spread TCA feedback loop** — expected/realized slippage feeds `portfolio_allocator` sizing against 20 bps threshold.
- **QENG-3d Execution policy simulator** — `services/execution_policy_simulator.py`, CLI script, and tests added.
</details>

<details open>
<summary><b>v8.8.5 UI Scaling & Mobile Panel Navigation (2026-06-12)</b></summary>

### Dashboard UX
- **Desktop scaling fix** — removed the `zoom:0.8` + `125vw/125vh` block from `styles.css` that was clipping the right edge; added `styles-desktop.css` with real 0.8× token/spacing overrides gated to `min-width: 769px`.
- **Mobile horizontal panels** — `styles.css` turns `.main` into a scroll-snap carousel on `≤768px` (Feed → Detail → Delivery); each `.pane` is `flex: 0 0 100%`.
- **Mobile pager** — added a bottom arrow/dot pager in `app.jsx` + `styles.css`; arrows and swipe both navigate; dots stay in sync with scroll.
- **Missing mobile nav icons** — added `bar-chart`, `eye`, and `globe` SVGs to the `Icon` component so Backtest, Watchlist, and Market show logos.
- **Responsive detail pane** — pane headers, detail rows, tabs, chart headers, similar-grid, and MC stats now wrap/stack on phones so content is no longer cut off.
- **Responsive topbar** — constrained dashboard logo to `28px` and hid text labels on Kill Switch / Sign-out buttons on mobile.
- **Full-detail jump** — clicking **Full detail** on a mobile signal card now scrolls the carousel to the center (detail) panel.
- **Asset cleanup** — resized `logo-full.png` and `logo-icon.png` to stay under the pre-commit 500 KB file-size limit.

### Verification
- `npm run build` succeeded (`dist/app-bundle.js` rebuilt).
- Backend non-E2E tests: **2550 passed, 18 skipped**.
</details>

<details open>
<summary><b>v8.8.6 Sentry Bug Fixes (2026-06-12)</b></summary>

- **SendLog `user_id` missing (PYTHON-FASTAPI-1Y, 25 hits)** — `routers/delivery_router.py` filtered `/api/delivery/log` by `SendLog.user_id`, but the column did not exist. Added `user_id` to `models.SendLog`, created Alembic migration `17c3c714fe68`, and populated it from both the scanner fanout path and the manual send endpoint.
- **yfinance delisted-ticker noise (PYTHON-FASTAPI-5/6, 176+ hits)** — `services/market_data.py` now caps `yfinance` loggers at `WARNING` so "possibly delisted" messages are not captured as Sentry errors. Missing-ticker quotes continue to be omitted gracefully.
</details>

<details>
<summary><b>v8.6 Alt-Data Validation, Discovered-Issue Fixes & TCA Wiring (2026-06-11/12)</b></summary>

### Free alt-data agenda §104–§110 (full verdicts)
- **§104. FINRA per-venue daily short-sale volume — SHIPPED, NO EDGE (2026-06-11).** Venue-aware downloader (FNRA/FNSQ/FNYX), aggregation, `build_short_volume_panel` 2009+, re-attribution. 15/15 fold coverage (79%), but FINRA SV stays inside/below the placebo band at both horizons — no deployable edge. Forward path continues as §104c.
- **§104b. Ablation FAILED at the pre-registered threshold (2026-06-11) — that is the IS verdict.** `sv_ratio_5d_delta < −2.0` tilt (49 trades) underperformed baseline. The subsequently "found" `ratio>40 AND delta<−10` cohort (N=8, WR 87.5%, +1.20pp) is **data snooping, not signal**: P(≥7/8 wins | baseline 68.6% WR) ≈ 23% on ONE cut, ≥6 effective looks taken → ≥80% chance of finding it by luck. **NOT deployed.** Lesson promoted to the section guardrail (pre-check firing rate before ablating).
- **§105b. SEC FTD ablation INCONCLUSIVE — parked, NOT deployed (2026-06-11).** FTD-percentile tilt fires on N≈5 trades (>75 pctile: 60% WR, +0.18%) — no information at that N. Do NOT invert to risk-off on N=5 (§77 inversion precedent required N≥30 live). Panel retained (2017–2024 backfilled; reuse continues as §114 + SPRT ID 9).
- **§106. NAAIM/AAII sentiment — backfilled, tilt FAILED (2026-06-11).** NAAIM since-inception xlsx backfilled (1,039 weekly rows, 2006+; aaii.com WAF'd → AAII deferred); UMCSENT (FRED) backfilled. NAAIM <30 sizing tilt failed; raw-level `--naaim` cross-sectional config inside/below placebo band. Percentile-feature follow-up continues as §115.
- **§107. GDELT historical news tone — SHIPPED, NOT DEPLOYED (validated 2026-06-12).** GKG 1.0 daily zips, concurrent downloads, fixed `--gdelt` merge. Full 2015+ panel (74,189 ticker-day rows); per-trade tilt fired on **0/217** trades (identical metrics to baseline); cross-sectional `--gdelt --placebo --walk-forward` net Sharpe 0.304 vs baseline 0.307 (Δ −0.003, inside placebo noise). Infrastructure retained for live news-sentiment family + forward SPRT reuse.
- **§110. Free per-stock options chain via CBOE delayed-quotes JSON — SHIPPED (2026-06-11).** `cdn.cboe.com/api/global/delayed_quotes/options/{SYMBOL}.json` (no auth): bid/ask, IV, OI, volume, greeks per contract. `OptionsChainDaily` model + migration, `services/options_cboe.py`, `scripts/snapshot_cboe_options.py`, nightly supervised job in `main.py`, fallback rewire Polygon → CBOE → yfinance, tests. Live-only; IV-rank self-accumulation continues as §112.

### §118 TCA feedback loop — WIRED (2026-06-12)
- `portfolio_allocator.py` scales weights against configurable `TCA_SLIPPAGE_THRESHOLD_BPS` (20bps, was hard-coded 42) and prices each order's expected slippage via Almgren-Chriss with the 30-day realized average as a floor (`tca_service.fetch_avg_realized_slippage()`); `check_capacity_limits()` blends realized history. Live verification pending (RISK-3).

### Discovered issues (2026-06-11 session) — all 10 fixed
- **DISC-1. Alpaca WebSocket rapid reconnect loop** — `_HEARTBEAT_SEC` 15s → 45s + `_should_log_reconnect()` rate limiter (max 3 logs/hour). `backend/services/alpaca_ws.py`.
- **DISC-2. Scanner logs missing after 12:42 UTC** — `RotatingFileHandler` for the scanner logger in `main.py` (10 MB × 5 → `backend/logs/scanner.log`).
- **DISC-3. `send_log` wrong `chat_id`** — `chat_id` column added (migration `bf79f41b6f1d`); `_maybe_send` records the actual recipient.
- **DISC-4. Timezone mismatch in cooldown/daily-cap queries** — already consistent (`datetime.now(timezone.utc).replace(tzinfo=None)`).
- **DISC-5. pytest polluting production DB** — `_PYTEST_RUNNING` guard in `database.py` forces SQLite under pytest.
- **DISC-6. Alembic migration chain gap** — chain verified intact; HEAD = `0f1099d21801`.
- **DISC-7. `signal_deliveries` missing `created_at`** — added with `server_default=now()`; `sent_at` made nullable. Migration `bf79f41b6f1d`.
- **DISC-8. `users.min_confidence_override` stale** — `update_notification_prefs` now syncs `min_conf` back to the column.
- **DISC-9/10. ruff in `.venv` + pre-commit Python path** — both verified already fixed.
- **SP1-1 / Pre-Launch #1. Owner password** — `.env` has 32-char secure password (2026-06-09).
</details>

<details>
<summary><b>v10.x Daily Operations & Research (2026-06-10)</b></summary>

### Pre-Launch
- **7. Train and deploy XGBoost ML model** — N≥300 reached (566 resolved: 495 BUY / 71 SELL, 101 tickers). Manual train run 2026-06-09 via `train_model()`: trained 396 / tested 170, **OOS AUC 0.6872** (95% CI [0.607, 0.767]) vs champion **0.6883** → **rejected** (Δ−0.0011, needs +0.005); champion kept, live model untouched. Auto-retrain already live: `_weekly_ml_retrain` runs Sun 11am ET.

### Active Research — External Agenda
- **§96a. Decomposition pass** — `overnight_pct`/`intraday_pct` tracked per held day in `simulate_ticker()` exit loop. **FIXED 2026-06-10 night:** day-0 overnight logic corrected (only counts for close-entry), canon plain run added, reconciliation check added. **Result: 61% of alpha from overnight gaps on full canon (217 trades).**
- **§96b. Close-entry A/B** — `--entry-at-close` flag added. **FIXED 2026-06-10 night:** honest cross-run A/B verified. **Result: ΔSharpe = 0.00 — neutral, safe for live use.** Close-entry tag-only telemetry remains active in `scanner.py`.
- **§96c. Live wiring** — `scanner.py` 15:45–15:55 ET close-slot detection tags BUY signals with `entry_style=close`. Verified tag-only (observe-only telemetry, no entry/delivery change) — safe to leave collecting forward data despite §96b being below bar.
- **§96d. Overnight-leg telemetry** — fields added to trade dict in backtest; live infrastructure ready.
- **§97a. Backtest grid** — `--entry-limit k` flag added. **FIXED 2026-06-10 night:** `_limit_signals_attempted` counter threaded through `simulate_ticker()` → `.attrs` → report. True fill rate now correct (e.g., 41.9% for k=0.5). **Substantive verdict unchanged:** all k variants fail deploy bar (Sharpe 0.16–0.12 vs canon 0.25). **§97 KILLED.**
- **§97b. Skip-the-gap interaction** — §97a and §96a report sections co-located for cross-read. DONE.
- **§99a. Pre-register the hypotheses NOW** — `scripts/sprt_preregister.py` run 2026-06-11 00:44 UTC. Four SPRT rows created in `ResearchExperiment` (IDs 3–6).
- **§99b. `scripts/sprt_monitor.py`** — built with Gaussian LLR, Wald boundaries, per-experiment state persistence. 12 unit tests passed.
- **§99c. Reuse for the other two pending decisions** — §92 shadow promotion and OOS v7/v8 pre-registered.
- **§99d. Surface in admin** — SPRT state added to `/api/admin/system-readiness` response.
- **§103a. Metric job** — `scripts/decay_monitor.py` computes trailing-50 Wilson CI on clean delivered BUYs.
- **§103b. Alarm wiring** — `evaluate_alarm()` returns `"decay"`, `"confirmation"`, or `None`.

### Next Sharpe×N Agenda
- **§87. Conviction-tier sizing — DEPLOYED (2026-06-10).** `--consec-score-sizing` flag added; corrected earlier unmeasurable deployment. Weighted A/B: Sharpe 0.24 → **0.30 (+0.060)**, ΔN=0. Deployed live as `_apply_l10_conviction_sizing()` in `scanner.py` with global clamp [0.10, 3.00].
- **§88. Calm-regime sleeve — ABANDONED (2026-06-10).** 0 trades generated in 23-year backtest. Structural, not a gate problem.
- **§89. Fama-French Short-Term Reversal factor** — `fetch_ff_str()` added; wired as 15th meta-label feature.
- **§90. Universe expansion batch 3 — all rejected (2026-06-10).** 0 trades across PANW, BWA, FTI, EQH, TRGP, APTV, DHI, FIVE, ITW.
- **§92. Pre-specify the cross-sectional shadow activation gate (2026-06-10).** `SHADOW_PROMOTION_CRITERIA` locked (min_resolved_signals=150, bottom-decile WR ≥3pp worse, top≥bottom); promotion criteria immutable. ⚠ **The data collection feeding this gate was dead 2026-06-09 → 2026-06-15** (scan history 1-bar short of the 253 needed — see §111 bugfix); counter genuinely at 0 resolved. Real accrual starts post-fix.
- **§93. Close the live-vs-IS gap — DONE (2026-06-10).**
  - (a) `sector_rs` scoring-path bug fixed at `assembler.py:1011`.
  - (b) launchd server restarted.
  - (c) net-of-friction calibration backfill: 566 samples, gross 43.6% → net 40.5%.
  - (d) ACT-4 gap decomposition v2: catastrophic 11–12 ET hours (t=-6.06, p=0.000), sector leak was >50% of BUY book.
- **DELIV-1. Stale-entry guard replaced (2026-06-10 evening, live).** Price-proximity entry-validity check replaces 120-min cutoff.
- **RE-BASELINE (2026-06-10 evening).** IS canon: N=217, Sharpe **0.24**, Deflated Sharpe FAILS (expected max 0.25 > 0.24). Live May+ cohort: 57.8% net WR, +2.06%/trade.
- **§94. Per-sector hold-days parity (2026-06-10).** `_SECTOR_MR_CONFIG` wired into backtest canon. +0.04 Sharpe. Committed `6295eb2`.

### Cross-Sectional Architecture (§86)
- **Step 1: Data Ingestion & Merge** — survivorship-bias-free universe from PIT intervals.
- **Step 2: Cross-Sectional Normalization** — per-day z-scores, winsorized ±3σ.
- **Step 3: Model Training** — XGBoost regressor on relative return target.
- **Step 4: Portfolio Allocation** — dollar-neutral top/bottom decile, 5d rebalances.
- **Step 5: Robustness validation (2026-06-09)** — expanding-window walk-forward CV + cost-sensitivity sweep. WF net Sharpe 0.42, 90% CI [+0.00, +0.84].
- **Step 6: Full-S&P-500 expansion (2026-06-09)** — HURT: +0.42 (curated 200) → −0.02 ($10M floor) → −0.23 ($100M floor).
- **Step 7: Qlib TopkDropout (2026-06-09)** — STRICTLY WORSE; hysteresis fails at IC≈0.013.
- **Step 8: Short-interest velocity feature test (2026-06-09)** — single-regime (2025 squeeze) artifact; fails walk-forward stability.
- **Step 10: WQ-101 screen + horizon sweep + borrow test + LIVE SHADOW deploy (2026-06-09).** Horizon sweep unlock: 5→21d raises net Sharpe **−0.058 → +0.347**. DEFAULT HORIZON raised 5→21. Shadow deployed live.
- **Step 11: Alt-data feature integration + horizon/cost sweep (2026-06-11) — UNDER REVIEW.** FINRA SV, SEC FTD, UMCSENT, NAAIM, and Wikipedia pageviews wired into `cross_sectional_alpha_model.py` as optional features (`--finra-sv`, `--sec-ftd`, `--naaim`, `--wiki`). First-pass results claimed h=21 net +0.308 and h=63 net 0.769, but a code review found two defects: (1) market-wide UMCSENT/NAAIM/AAII were z-scored to death (std=0 → NaN → 0), so their contribution was colsample noise; (2) FINRA SV and Wikipedia were merged same-day with ~1-day lookahead. Both fixed in code. Single-split previews with fixes: baseline 0.369, `--finra-sv` 0.414, `--wiki` 0.451, `--naaim` −0.182, `--naaim --wiki` 0.111; placebo noise 0.151–0.159. Corrected walk-forward: every alt-data Δ inside the placebo band at both horizons — **no alt-data claim stands; h=63 0.769 permanently withdrawn** (resolved in Step 12).
- **Step 12: Nested-horizon validation + parallel h=63 live shadow (2026-06-11) — DONE.** The horizon effect itself put through honest validation: `--nested-horizon` selects the horizon per walk-forward fold from PRIOR folds only (grid {21,40,63}, burn-in 2, full universe, price features only). **h=63 won ex ante in all 12 eval folds (2014–2025)** → nested net Sharpe **+0.576 [90% CI +0.22, +0.91]**, selection haircut **0.000** vs fixed h=63 (h=21 same folds: +0.419); corroborated by the independent single-split test (+0.494 OOS 2020–2026). Full h=63 WF track: net 0.616 [CI +0.29, +0.94], 10/14 folds positive, MaxDD −11.8%; **cost-robust** (+0.481 @40bps one-way, where h=21 goes negative) and **borrow-robust** (breakeven ≈700bps/yr vs ~50–150bps realistic GC). Caveat: grid descends from the contaminated sweep → validates 63-beats-21/40, not 63-optimal. **Deployed as PARALLEL live shadow** (server restarted 2026-06-11): `--save-model --horizon 63` → `*_h63.json`; `score_batch_h63()`; `scan_all` attaches `crossSectionalShadowPctH63`. §92 promotion criteria remain h=21-only; backtest default `HORIZON` stays 21. See LEARNINGS §104–§110 addendum + Stats.md §15 v8.6.

### Operational
- **TEST-4. Mutation testing (2026-06-09)** — Ran `mutmut` on `delivery_gates.py`. 43.7% mutation score (278/636 killed, 358 survived). Target >70%.
- **FE-2. Lighthouse accessibility audit (WCAG 2.1 AA) — DONE (2026-06-11).** Score: 89 → **100**. Fixes: `--text-faint` lightened `#56617a` → `#7585a3` (29 contrast failures); flow-step `<h4>` → `<h3>` and footer `<h5>` → `<p className="foot-hd">` (heading-order); `<div className="site-shell">` → `<main>` (landmark). Bundle rebuilt.

### Live Findings & Calibration
- **DATA-1. sector_etf null-coupling bug — FIXED + backfilled (2026-06-09).** 81% of signals had NULL `sector_etf`; fixed at `assembler.py:1241`. 2,252 historical signals backfilled.
- **DATA-2. policy_version was never written — WIRED (2026-06-09).** Now stamped `v10.3/v8.0` at `scanner.py:1585`.
- **ALPHA-2 / A24. Run §85-1 fundamental modifier audit (2026-06-09, N=566)** — no modifiers to remove. §50 Piotroski strongly additive (+13.1pp).
- **CLEAN-1. Keep `src` symlink + document pyproject.toml (2026-06-09).**
- **CLEAN-2. Dead fetch audit sweep (2026-06-09).** All 15 yfinance symbols verified alive.
- **ACT-5. Full backtest flag validation runs (2026-06-09).** Param-sweep, validate-live-gates, regime-split all completed.

### Path to 10/10
- **§89a + §89b + §93d + meta-retrain: New findings (2026-06-10).** ST_Rev regime sizing negligible (+0.008 Sharpe). Factor attribution: Alpha = +0.87%/day (p=0.044). Meta-model CV-AUC 0.4224 < 0.52 gate.
- **R10-16: Backend Architecture (8.5 → 9.0) — DONE (2026-06-08).** SAVEPOINT wrapping for aux-data persistence; `_async_exception_handler` installed.
</details>

<details>
<summary><b>v8.5 External Research & Infrastructure (2026-06-11)</b></summary>

### Active Research — External Agenda (remaining items)
- **§100. SimFin fundamentals integration — DONE.** `simfin_bulk_download.py` + `build_simfin_factors.py` created. 5 factors (earnings yield, gross profitability, accruals, asset growth, net buyback yield) wired into `cross_sectional_alpha_model.py` with `--simfin` flag. PIT audit: 90-day lag fallback documented.
- **§101. TSMOM diversifying sleeve — DONE.** `backtest_tsmom_sleeve.py` created. Result: Long-flat Sharpe **0.57**, 4/4 epochs positive (2015-22 fold 0.277, just below 0.30 bar). Corr vs MR book: +0.27. Deploy bar not cleared; retained as research artifact.
- **§103c. Decay monitor VIX regime context — DONE.** `scripts/decay_monitor.py` now classifies VIX regime (calm/normal/elevated) per signal. Calm-market decay re-labeled `"drought"` (N starvation, not true decay).

### Infrastructure & Bug Fixes
- **§85-2. MD&A EDGAR bug fix — DONE (2026-06-10).** `_fetch_filing_text()` now consumes `primaryDocument` from SEC submissions JSON (deprecated `-index.json` endpoint returned 404). All 21 edgar unit tests pass.
- **Fill-rate bug fix — DONE (2026-06-10).** `_limit_signals_attempted` counter threaded through `simulate_ticker()` → `.attrs` → report. True fill rate now correct.
- **VAPID keys — DONE (2026-06-10).** Generated via `py_vapid`, added to `.env`, `config.py` reads correctly.
- **ACT-6. E2E Playwright tests — DONE (2026-06-10).** 5 passed (health, landing, auth×3), 7 skipped (need owner creds in CI).
- **§69–§74 gate unit tests — DONE (2026-06-10).** `tests/test_gates_5982.py` created, all passing.
- **§95. DD-throttle — VERIFIED LIVE (2026-06-10).** Already operational in `portfolio_allocator.py` lines 415–441.
</details>

<details>
<summary><b>v8.1 Quant Refinements & Decomposition (2026-06-08)</b></summary>

- **REF-1: Dynamic TCA Slippage Feedback** — Fed realized slippage from `fills` and `broker_orders` tables back to dynamically scale down HRP target weights if realized slippage exceeds threshold (42 bps).
- **REF-2: Replay Engine Drift Detection** — Set up `drift_detector.py` comparing live DB signals vs. Replay Engine outcomes using point-in-time snapshots and updated it to copy signal metadata to verify parity and catch data pipeline/logical drift.
- **REF-3: Dynamic Cross-Sleeve Capital Sizing** — Refined the cross-sleeve allocator (`alpha_sleeves.py`) to size sleeve allocations dynamically using rolling 30-day simulated and real out-of-sample Sharpe ratios.
- **REF-4: Causal Cohort Analytics Dashboard** — Added the `/cohort-analytics` API endpoint in `admin.py` to compare empirical win rates, average returns, and Brier scores across randomized cohort groups.
- **REF-5: HRP Scanner Loop Integration** — Wired HRP batch portfolio execution directly into the scanner scan/execution path and implemented `execute_portfolio_for_user()` inside `broker_svc.py` to calculate target sizes, enforce limits, and execute orders.
- **REF-6: Meta-Labeling Feature Hardening** — Expanded the XGBoost meta-label model features with VIX ratio, VIX9D ratio, and sector momentum. Updated `train_metalabel_model.py`, `signal_ml.py`, and `assembler.py` to support 14-feature schemas, and retrained the meta-label model on the new dataset. **COMPLETED (2026-06-10):** `backtest_technicals.py` now stores all 15 meta features per trade (14 + §89 FF ST_Rev); HMM regime pre-computed with 21-day stride; VIX3M fetched for term structure; sector momentum from ETF 5d returns; entry_prob from live entry model. Meta-model retrained (CV-AUC 0.4364, all 15 features non-zero importance). `_MIN_META_AUC=0.52` quality gate in `get_meta_model()` auto-disables weak models. `_meta_prob = None` hardcoded guard removed from `assembler.py`.
- **BE-1. Decompose signal_engine.py** — Decomposed the massive `generate_signal()` sequential scorer into a scoring-context object `ScoringContext` (in `services/engines/context.py`) and scoring blocks (in `services/engines/scorers.py`) to handle state safely with zero regression.
- **R10-15: Signal Engine / Gate Stack (8.5 → 10)** — Completed BE-1, decomposing `generate_signal()` with parity tests and zero behavior change.
- **R10-7: Per-signal Kelly — RESEARCHED, NO-DEPLOY (2026-06-08).** Added `stats_kelly` + `kelly_size_mult` + the §Inv-K validator to `backtest_technicals.py`. The universal 1.5s/2.0t stop/target makes reward:risk *constant* (realized b=0.83), so per-signal Kelly has no payoff term and is just a convex reshaping of conviction sizing. Deployable formula clamped to the live [0.85,1.15] envelope scored −0.015 vs the incumbent linear L7 (0.25→0.24). **Decision: keep linear L7.** Revisit only with per-signal-varying R:R or an OOS-validated wider envelope.
- **R10-8: Per-ticker friction — RESEARCHED, NO backtest change (2026-06-08).** §R10-8 vol-scaled friction validator added. Realistic large-cap friction ≈0.25% vs the flat 0.50% — the flat number is a deliberate ~2× conservative buffer; lowering it would manufacture fake Sharpe (0.23→0.30 is *all* lower assumed cost). Flat 0.50% **kept**. Edge robust across volatility/spread terciles (Sharpe 0.29 / 0.34 / 0.30). Live path: §80 score penalty + TCA→allocator feedback (closed 2026-06-12 as §118) + QENG-3d sim.
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
- **QENG-6a: Operationalize triple-barrier meta-labeling** — Operationalized ML prediction within `signal_ml.py` to screen signals when meta-label probability is low. **UPDATED (2026-06-10):** Meta-model retrained on full 15-feature CSV (HMM, VIX term structure, sector momentum, FF ST_Rev, entry_prob all real values — no NaN skew). `_MIN_META_AUC=0.52` gate prevents weak models from degrading blends; guard removed from `assembler.py`. Model auto-activates when CV-AUC crosses threshold.
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
