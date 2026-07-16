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

**Completed by agent (2026-06-18):**
- ✅ CI/CD `continue-on-error` removed from secrets-scan and deploy jobs.
- ✅ Pricing restructured: $19 Basic / $49 Pro / $99 Elite (hidden). Paper trading moved to Basic.
- ✅ Free tier quota reduced: 5→3 signals/day.
- ✅ Midday 11–12 ET microstructure filter (−3pp confidence haircut) deployed in `delivery_gates.py`.
- ✅ Signal Journal endpoint (`/api/signals/journal`) added for free-tier proof-before-pay.
- ✅ Product Classification table added to ToS.
- ✅ Honest track record page updated with 43% WR, gap decomposition, and fix roadmap.
- ✅ Blog post "The 25.5pp Gap" written for SEO and differentiation.

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
> See [RUNBOOK.md](RUNBOOK.md) §7 and [HOWTO.md](HOWTO.md) §11 for detailed procedures.

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

- [~] **§MAX. Low-MAX-21 filter — INCLUDED, tracked for re-evaluation (2026-07-15).** Live-wired (`Max21Gate` in `assembler.py`, blocks BUY when trailing-21d max daily return > ticker's own causal expanding 55th percentile) and set as the unconditional `backtest_technicals.py` default (`--max21-filter 1.0` to disable). Decision: keep shipped, but the evidence is genuinely mixed — do not treat as fully validated.
  - **For:** walk-forward OOS on the pre-specified, uncontaminated 73-ticker `HELD_OUT_TICKERS` universe is directionally consistent with IS on every metric — per-trade Sharpe 0.17→0.20, WR 66.9%→69.6%, PF 1.47×→1.59×, MaxDD −1.67%→−0.98% (N=139→112 clean).
  - **Against:** IS paired block-bootstrap (filtered vs. same-block baseline, N=264/313, `scripts/max21_bootstrap_ci.py`) gives a 90% CI on the delta of **[−0.028, +0.062]** (median +0.017) — includes zero, not significant. The exciting IS *portfolio-level* Sharpe jump (3.28→3.75/4.35) that motivated graduating this does **not** replicate OOS — portfolio Sharpe there goes 4.35→3.59 (filter hurts), likely small-N noise (139/112 trades) but a real, directly-measured contradiction, not hand-waved away.
  - **Re-evaluation trigger:** re-run `scripts/max21_bootstrap_ci.py` (paired delta bootstrap) once the live delivered book has enough resolved signals to test the SAME per-trade lift on genuinely live (not backtested) data — mirrors the promotion-gate pattern already used for §86/§91/§111. Bar: promote to "confirmed" once the 90% CI lower bound on the paired delta exceeds 0, either via live data or a larger/longer OOS backtest sample. If the live delivered book shows the filter *hurting* WR (matching the OOS portfolio-Sharpe reversal, not the OOS per-trade improvement), reconsider reverting to opt-in.
  - Full numbers: this session's conversation log; summarized in `docs/RESEARCH_SIGNAL_ENGINE_IMPROVEMENTS.md` §1.2.

### External-research agenda — §96–§103
- [x] **§98. ORATS one-month sprint (DONE 2026-06-18)** — purchased (~$100); panel built → Postgres `orats_daily_features` (115 trading days **2026-01-02→06-17**, ~5,900 tickers/day, EOD IV/skew/GEX/DEX/PC-ratios). Pipeline: download CSVs → `build_orats_panel.py --save-to-db` → `backtest_technicals.py --orats`. Standalone research harness (not wired to live): `scripts/orats_opportunity_model.py` (`--mode direction|vol`) + `scripts/orats_recommendation_engine.py`. Findings recorded as **§120–§125** below; live-integration plan in `LEARNINGS.md`/memory.
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
- [~] **§62. VRP per-stock** — TESTED on the §98 ORATS panel (see §120). Variance risk premium is large and real on 2026 data: realized 2d move ≈ 0.72× implied (median 0.57×), 74-78% of names move LESS than implied. Per-stock IV now in hand for 2026; deeper multi-regime history still needs a Polygon Options upgrade (~$79-199/mo).
- [ ] **§84. Survivorship bias correction** — Purchase EODHD (~$20/mo) or Norgate ($33/mo) delisted constituent lists.
- [ ] **Options flow confirmation gate** — Subscribe to Unusual Whales API (~$50/mo).
- [ ] **GEX support levels** — SpotGamma API (~$99/mo).
- [ ] **Market-neutral beta hedge** — Short 0.9× position value in SPY at entry. Requires margin account.

### ORATS options-data findings — §120–§125 (backtested 2026-01-02 → 06-17, the §98 panel)
Purged walk-forward on the in-hand year; harness = `scripts/orats_opportunity_model.py` + `orats_recommendation_engine.py`. **All numbers are single-regime (risk-on 2026 H1, no vol spike) — treat as upper bounds.**

- [x] **§120. ORATS VRP / volatility-premium harvest — REAL, validated edge.** ORATS IV predicts move *size* with huge robust IC (atm_iv_30d vs next-day |move|: IC +0.38, t=+67; walk-forward move-size forecast IC +0.36 companies / +0.55 ETF). Rank by richness = implied/forecast move; rich-decile = options overprice the move → sell premium. Tail-capped short-straddle backtest (premium≈0.8×implied, stop −3×prem, 5% cost): **companies net +0.82%/2d-trade, win 69%, worst −32%; ETF net +1.19%, win 93%, worst −12%.** Premium-seller base rate 74-78%. This is the one durable edge the $100 bought — it requires the *implied* move (free realized vol forecasts size slightly better, IC 0.50 vs 0.42, so the data's value is the implied side for rich-vs-cheap). Live path = §122.
- [x] **§121. ORATS *direction* model — NEGATIVE result (do not re-run).** Predicting the *sign* of forward return from ORATS aggregates has no per-name edge: headline L/S decile Sharpe 1.4-1.9 is a pure volatility/beta tilt — `corr(pred, IV)≈+0.5`, **within-IV-tercile IC ≈ 0** (t<1 both horizons), top-decile hit rate ≈ coin-flip (50-51%). Consistent with the spent-IS-lever invariant below. Recorded so this dead end isn't repeated.
- [~] **§122. Fusion recommendation engine → live `optionsStrategy` tag (option-B path, deferred).** `orats_recommendation_engine.py` fuses live engine direction (`signals` table) + §120 VRP + earnings into one action: SELL_CASH_SEC_PUT / BUY_STOCK / SELL_STRANGLE / LONG_STRADDLE / AVOID_EARNINGS. To productionize: add `impliedMove2d`/`forecastMove2d`/`vrpRichness`/`optionsStrategy` to the live signal dict (`assembler.py`), deploy as a SHADOW field first (like §86/§111 `xs_shadow_pct`) — log without changing action/sizing — then promote after a real vol regime. Only the VRP view, never the §121 direction model.
- [ ] **§125. HF realized vol from Massive minute flat files — free model upgrade (explored 2026-06-18).** Stocks+Options Starter only allow 4 downloadable datasets (day/minute aggs; indices/quotes/trades/futures = 403, so NO VIX or bid-ask). The useful one is **`us_stocks_sip/minute_aggs_v1` → high-frequency realized vol** (391 1-min bars/session). Close-to-close — what the VRP forecast denominator uses now — **systematically understates true vol on choppy days**, which causes false 'rich' sells into turbulence. Aug-5-2024 proof (HF 1-min realized vol vs close-to-close move): SPY 31% vs 1.5%, AAPL 73% vs 5.3%, JPM 35% vs 0.8% (whipsawed, closed flat). On Aug 5 SPY IV≈29% ≈ HF-realized 31% → options were FAIRLY priced, but the close-to-close model would flag them RICH and sell into the spike. **Action:** add `rvol_hf` (realized variance from 1-min returns) to `_VOL_FEATURES` and as a turbulence risk-gate (don't sell premium when HF realized vol is running hot). Needs a minute-stock download (~23MB/day, stream→per-ticker RV→discard). `us_options_opra/minute_aggs_v1` (IV at a fixed time) is real but limited: ATM options print only ~12 bars/day (sparse), so use 'last bar ≤ 15:55' for time-consistency, not a full 15:55 surface.
- [ ] **§123. Hard preconditions before any §122 live deploy.** (1) **Tail UNTESTED** — 2026 H1 sample has no vol spike; straddle hit-tail-cap=0%, worst 2d trade −32%; need a Feb'18/Mar'20-style window or paper-trade through one. (2) Exclude leveraged/inverse ETFs from sell-premium (SOXL/SNXX/MUU/FAS/SQQQ 170-213% IV can move 15-19%/2d legitimately). (3) Mandatory earnings filter — excluding top-IV-decile ≈halved worst-case (−32%→−15%); use real `days_to_earnings`. (4) P&L realism — model ignores gamma path/bid-ask/assignment; validate vs real chains. (5) Options routing/margin approval the platform may lack.
- [ ] **§124. Trading VIX directly = the WORST expression of §120 (do not — recorded 2026-06-18).** VIX is the pure short-VRP trade, but the data argues against it: the *market-level* VRP is thinner & tail-heavier than the diversified single-name book — SPY (≈spot VIX, ranged 11.5-26.6% in 2026) realized/implied **mean 0.93** (vs 0.72 cross-sectional), QQQ **1.02** (no edge), median-vs-mean gap = the undiversifiable tail that destroyed XIV (−96% in a day, Feb'18). Trading VIX (a) strips the cross-sectional diversification that produced the 69-93% win rates, (b) concentrates 100% into the untested-tail (§123-1), (c) needs VIX-futures **term-structure roll** data we DON'T have (live `macro.py` §47 VIX/VIX3M is the right tool, independent of ORATS), (d) VIX ETPs (VXX/UVXY/SVXY) add decay/leverage path-dependency the data can't price. Sane market-level expression = **defined-risk SPY/SPX premium** via `orats_recommendation_engine.py --universe index` (SELL_DEFINED_RISK: iron condor / put spread; gated on the term structure), never VIX ETPs.

> **Critical invariant:** the IS Sharpe ceiling appears spent (Deflated Sharpe fails at 744 trials). Future edge must come from orthogonal data (options flow, short-interest velocity, cross-sectional ranking) or execution cost reduction, not more OHLCV parameter sweeps. **§120 (ORATS VRP) is the first orthogonal source to clear walk-forward — but it's a volatility product with real tail risk, not directional alpha for the long-only MR engine.**

### Options / ORATS / Massive — next steps (post-session 2026-06-18)
All items are standalone research / tooling; nothing is wired into the live engine yet.

- [x] **MASSIVE-1. IV agreement audit (ORATS vs Massive, 2026 overlap).** DONE — 16,065 overlapping pairs / 140 tickers. ATM IV: overall r = 0.50, per-ticker median r = 0.79, top names > 0.98. Skew is noisy (r = 0.04). Massive is sufficient for ATM IV / VRP; do not use it for skew signals.
- [x] **MASSIVE-2. Complete 2-year Massive VRP tail backtest.** DONE — companies h=2d: full 2y net +0.53%/trade, win 71%, Sharpe +3.0, worst −16.4%, hit-cap 1%; Aug-2024 spike week net +1.06%, win 82%, worst −5.9%. Worst single trade WDAY −15.4% on an earnings jump.
- [ ] **MASSIVE-3. Add HF realized vol (`rvol_hf`) to the vol model.** Use `us_stocks_sip/minute_aggs_v1` to compute 1-min realized variance; add to `_VOL_FEATURES` and as a turbulence sell-gate so the model does not sell premium into choppy/rich-realized days.
- [ ] **MASSIVE-4. Stale-signal filter in recommender.** Drop `BUY_STOCK` / `SELL_CSP` recommendations whose entry/stop/target are inconsistent with current spot.
- [x] **MASSIVE-5. Live signal for options strategy.** Added `option_strategy`/`option_richness`/etc. to `Signal` and exposed in `routers/signals.py`; scanner persists option VRP signals daily. Default `User.options_mode='signal'` (alert-only); paper/live require explicit opt-in.
- [~] **MASSIVE-6. Satisfy §123 preconditions before any live capital:** tail tested through Aug-2024 spike, leveraged-ETF exclusion added to options_engine, mandatory earnings filter active (horizon+1), paper/live execution stubs in place (Alpaca/IBKR) but not yet validated against real chains/margin.

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

Completed sprint history lives in [PROGRESS.md](PROGRESS.md). This file tracks only **open** work.
