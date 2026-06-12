# Signal.Trade — TODO

## 🔴 Pre-Launch Checklist
These are critical tasks that must be completed before public launch or marketing scale.

- [x] **1. Change owner password** — FIXED 2026-06-09 — `.env` has 32-char secure password. Startup fails on `ChangeMe123!` in production.
- [ ] **2. Deploy to public HTTPS URL** — Run `railway up` or `fly deploy`. Set `APP_URL=https://your-app.up.railway.app`. *Risk: Stripe webhooks 404, OAuth callbacks broken, HTTPS-only cookies not sent.*
- [ ] **3. Configure Stripe billing** — `STRIPE_SECRET_KEY` and price IDs set. Still needed: register webhook in Stripe Dashboard, copy `whsec_...` to `STRIPE_WEBHOOK_SECRET`. (Note: startup now logs CRITICAL if `STRIPE_WEBHOOK_SECRET` is empty in prod; webhook handler returns 500 explicitly). *Risk: checkout completes but tier never activates.*
- [ ] **4. Register Telegram webhook** — After HTTPS deploy: `curl -X POST <https://your-app>/api/telegram/set-webhook`. *Risk: subscribers cannot link Telegram.*
- [ ] **5. Configure SMTP (email)** — Add `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` to `.env`. *Risk: no email verification, no password reset, no weekly digest.*
- [ ] **6. Enable Telegram broadcast channel** — Create private channel, make bot admin, add `TELEGRAM_BROADCAST_CHANNEL_ID=-100...`. *Risk: at >50 subscribers, per-user DM loop hits Telegram rate limit.*
- [ ] **8. Configure Google OAuth** — `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`.
- [x] **9. Configure VAPID web push** — FIXED 2026-06-10 — keys generated via `py_vapid`, added to `.env`, `config.py` reads correctly. Web push ready for HTTPS deploy.
- [ ] **10. Set up Cloudflare CDN** — Point DNS to Railway/Fly. *Risk: slower global load.*
- [ ] **11. Google AdSense** — Apply at adsense.google.com. *Risk: no ad revenue from free tier.*
- [ ] **12. Add Redis in Production** — `railway add --plugin redis`. *Risk: redundant API calls under concurrent load.*
- [ ] **13. Upgrade SendGrid** — Essentials (~$20/mo) before daily signups + resets exceed 100 emails/day.

---

## 🔍 Discovered Issues (not previously tracked)
Bugs and gaps found during today's session (2026-06-11) that need fixing.

### Scanner & Delivery
- [x] **DISC-1. Alpaca WebSocket rapid reconnect loop** — FIXED: `_HEARTBEAT_SEC` raised from 15s → 45s (IEX can be quiet 30–40s). Added `_should_log_reconnect()` rate limiter: max 3 reconnect logs/hour. `backend/services/alpaca_ws.py`.
- [x] **DISC-2. Scanner logs missing after 12:42 UTC** — FIXED: Added `RotatingFileHandler` for `logging.getLogger("scanner")` in `backend/main.py` (10 MB × 5 backups → `backend/logs/scanner.log`). Alpaca WS spam no longer drowns scanner logs.
- [x] **DISC-3. `send_log` records wrong `chat_id`** — FIXED: Added `chat_id` column to `send_log` (migration `bf79f41b6f1d`). `_fanout_to_subscribers` now returns `(bool, first_chat_id)`. `_maybe_send` records the actual recipient (broadcast channel, first fan-out chat, or legacy fallback) in `SendLog.chat_id`. `backend/models.py`, `backend/services/scanner.py`, `backend/routers/signals.py`.
- [x] **DISC-4. Timezone mismatch in cooldown / daily-cap queries** — ALREADY FIXED in current code: both `_today_start` and `cutoff` use `datetime.now(timezone.utc).replace(tzinfo=None)` consistently. No change needed.

### Database & Schema
- [x] **DISC-5. pytest polluting production DB** — FIXED: Added `_PYTEST_RUNNING` guard in `backend/database.py`. If pytest is detected and `DATABASE_URL` points to PostgreSQL, it's forcibly overridden to SQLite with a warning. `conftest.py` fixture also sets `DATABASE_URL` to SQLite.
- [x] **DISC-6. Alembic migration chain gap** — ALREADY FIXED: Chain is intact: `8dab442e6933` → `abc123def456` → `4a7f6b33eb49` → `0f1099d21801`. `raw_confidence` column exists. Current alembic_version = `0f1099d21801` (HEAD).
- [x] **DISC-7. `signal_deliveries` missing `created_at`** — FIXED: Added `created_at` column with `server_default=now()` to `signal_deliveries`. Also made `sent_at` nullable (was `server_default=now()`; now set explicitly on delivery confirmation). Migration `bf79f41b6f1d`.
- [x] **DISC-8. `users.min_confidence_override` stale for user 3** — FIXED: `backend/routers/me.py::update_notification_prefs` now syncs `min_conf` from JSON prefs back to `users.min_confidence_override` column on every save.

### DevEx & Tooling
- [x] **DISC-9. `ruff` missing from `.venv`** — ALREADY FIXED: `ruff>=0.9.0` is pinned in `backend/requirements.txt` line 50 and installed in `.venv`.
- [x] **DISC-10. pre-commit hook pointed to dead Python path** — ALREADY FIXED: `.git/hooks/pre-commit` points to `.venv/bin/python3.14` which exists.

## 🚀 Next Sprint (2026-06-11)
Actionable items derived from today's session. Ordered by payoff ÷ effort.

### Security & Auth (do first — blocking everything else)
- [x] **SP1-1. Change owner password** — DONE (same as Pre-Launch #1, 2026-06-09).
- [ ] **SP1-2. Configure SMTP** — Add `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` to `.env` (SendGrid free tier is enough to start). Test: trigger password-reset flow for owner account. Unblocks: email verification, weekly digests, password resets. *Risk: users who forget passwords have no recovery path.*

### Observability & Pipeline (before next deploy)
- [ ] **SP1-3. Wire Sentry DSN** — Sign up at sentry.io, create a Python/FastAPI project, paste DSN into `backend/.env` `SENTRY_DSN=...`. Restart server, verify a test 404 appears in Sentry dashboard within 30s.
- [ ] **SP1-4. Push to GitHub & verify CI** — Commit today's changes, push to `main`, verify `.github/workflows/` passes (ruff, pytest coverage floor, gitleaks). Fix any red checks before they rot. *Risk: broken CI masks regressions.*

### Scale & Delivery (before first paying user)
- [ ] **SP1-5. Enable Telegram broadcast channel** — Create private Telegram channel, add bot as admin, set `TELEGRAM_BROADCAST_CHANNEL_ID=-100...` in `.env`. Test: send one broadcast signal, confirm it posts to the channel. Unblocks: scaling past 50 subscribers without hitting Telegram rate limits.
- [ ] **SP1-6. Add Redis** — `docker run -d -p 6379:6379 redis:7-alpine` locally, set `REDIS_URL=redis://localhost:6379` in `.env`. Verify: startup logs show "Redis worker bus active" (or similar). Unblocks: concurrent scan safety, cross-process job distribution.

### Revenue & Growth (parallel track)
- [ ] **SP1-7. Apply for Google AdSense** — 10-minute form at adsense.google.com. Use `signal.trade` domain (or whatever you plan to deploy to). Approval takes 1–14 days; starting now removes a future blocker.

---

## 🎯 Active Research & Alpha TODOs
These are targeted research and statistical modeling opportunities to improve signal edge.

### External-research agenda — §96–§103 (added 2026-06-10 evening, post-§DELIV)
**6 of 8 items COMPLETE** (§96, §97, §99, §100, §101, §103). **2 remain open:** §98 (paid, ~$99) and §102 (Nov 2026 calendar item).

- [ ] **§98. ORATS one-month sprint — make §62/§48/§49 historically testable for the first time (PAID ~$99 one-off, time-boxed).** [ORATS](https://flashalpha.com/articles/best-options-data-apis-2026) serves per-stock EOD IV indicators back to 2007 at $99/mo. Pre-register thresholds, pull ~19yr of IV history for the 111-name universe in one subscription month, and run the standard ablation on the IS window. Decision rule: deploy/keep live gates only on measured ΔSharpe.
- [ ] **§102. Tick-size regime change watch (FREE — Nov 2026 calendar item).** SEC half-penny quoting + access-fee cut takes effect the first business day of Nov 2026 for ~2,000 liquid names. Action: calendar a post-implementation review of realized spreads via the TCA service + re-tune §80 bands on Dec-2026 data.

### Free alt-data agenda — §104–§110 (added 2026-06-10 night, deep external research)
All sources verified free as of 2026-06. Selection criteria: orthogonal to price (the OHLCV well is dry), **backtestable history depth** (the §86 lesson: live-only features can't be validated), PIT-clean with explicit publication lags (the §14 FRED look-ahead lesson: lag every series by its real publication delay, not its observation date), and fit to the validated mechanism (forced selling / fear premium / squeeze fuel). Deploy path for every item: backfill → as-of-join ablation in `backtest_technicals.py` → per-fold read → **sizing tilt, never a block** → registry + SPRT. **Guardrail added 2026-06-11 (from the §104/§105 failures): pre-check the expected firing rate before ablating — a per-trade condition firing on <20% of the ~217-trade book is unfalsifiable in IS (N≈8 cohorts are pure noise: ≥7/8 wins happens ~23% of the time by luck). Rare-extreme features belong in the cross-sectional harness (breadth = N) or forward SPRT, not IS tilts. And the pre-registered threshold's verdict is THE verdict — thresholds found by re-searching the same sample only ever graduate via forward data.** Ranked by history depth × mechanism fit:

- [x] **§104. FINRA per-venue daily short-sale volume — extends the live short-volume gate from 2024+ to 2009+ (FREE, highest priority).** The live Polygon/Massive short-volume gate is historically unvalidatable (data starts ~2024-02). [FINRA publishes daily short-sale volume files](https://www.finra.org/finra-data/browse-catalog/short-sale-volume-data/daily-short-sale-volume-files) free: per-venue TRF/ADF files since **2009-08-03**, consolidated NMS since 2018-08-01 ([API available](https://developer.finra.org/docs/reg-sho-daily-short-sale-volume)). Published same evening (6pm ET) → next-day-usable, PIT-clean. **Shipped 2026-06-11:** venue-aware downloader (FNRA/FNSQ/FNYX), aggregation, `build_short_volume_panel` 2009+, re-attribution. **Verdict:** 15/15 fold coverage achieved (79%), but FINRA SV remains inside/below the placebo band at both horizons — no deployable edge.
  - [ ] §104a. Backfill loader: aggregate per-venue files (pre-2018) + consolidated (post-2018) into a `short_volume_daily_finra` panel for the 111-name universe; reconcile overlap year vs Massive data as a correctness check.
  - [x] §104b. **Ablation FAILED at the pre-registered threshold (2026-06-11) — that is the IS verdict.** `sv_ratio_5d_delta < −2.0` tilt (49 trades) underperformed baseline. The subsequently "found" `ratio>40 AND delta<−10` cohort (N=8, WR 87.5%, +1.20pp) is **data snooping, not signal**: P(≥7/8 wins | baseline 68.6% WR) ≈ 23% on ONE cut, ≥6 effective looks taken (3 deltas × ratio grid) → ≥80% chance of finding it by luck; the +1.20pp is ~0.5 SE wide at N=8. **NOT deployed.** Structural lesson promoted to guardrail: a per-trade tilt firing on <20% of a 217-trade book is unfalsifiable in IS — pre-check expected firing rate before ablating.
  - [ ] §104c. **Forward path only:** (i) keep SPRT ID 8 for the pre-registered definition; (ii) optionally register the −10/40 variant as a NEW explicitly-exploratory forward SPRT (provenance: threshold chosen on IS — forward live data is the only untouched sample that can validate it); (iii) the panel's real reuse is the cross-sectional model (§86/§100 harness) where 500-name breadth gives actual N. Live-gate data-source swap to FINRA-direct still worthwhile independently (removes the Massive dependency).
- [ ] **§105. SEC fails-to-deliver panel — the only new source covering the FULL 23-year IS window (FREE).** [SEC publishes half-month FTD files](https://nasduck.substack.com/p/how-to-read-sec-ftd-and-not-fall) since 2004 (CSV; open-source parsers exist, e.g. juszhan/Fail-To-Deliver). Persistent FTDs = settlement stress = the literal mechanics of forced selling. ⚠ PIT discipline: published ~15–30d after the settlement date — as-of-join on **publication date**, not trade date.
  - [ ] §105a. Backfill 2004→now per-ticker FTD shares / shares-outstanding panel + Reg-SHO threshold-list membership flags.
  - [x] §105b. **Ablation INCONCLUSIVE — parked, NOT deployed (2026-06-11).** FTD-percentile tilt fires on N≈5 trades (>75 pctile: 60% WR, +0.18%) — no information in either direction at that N; same unfalsifiability problem as §104b. Do NOT invert to risk-off on N=5 (the §77 inversion precedent required N≥30 of live data). Panel retained (free, 2004+): reuse where breadth gives N — (i) cross-sectional model feature (§86/§100 harness), (ii) forward accumulation via SPRT ID 9 (pre-registered definition only).
- [ ] **§106. NAAIM (2006+) + AAII (1987+) weekly positioning/sentiment — deep-history regime tilts (FREE).** ⚠ **Access paths corrected 2026-06-11 after backfill probe:** the macromicro API errors (#1158) and aaii.com is WAF'd — use these instead: (a) **NAAIM UNBLOCKED** — NAAIM publishes the full since-inception xlsx itself at `naaim.org/wp-content/uploads/<YYYY>/<MM>/USE_Data-since-Inception_<date>.xlsx` (filename is dated; loader must scrape `naaim.org/programs/naaim-exposure-index/` for the current `USE_Data-since-Inception_*.xlsx` href — verified working). (b) **AAII DEFERRED** — direct xls and Wayback both dead; optional path is Nasdaq Data Link's AAII dataset (free key) but NAAIM alone covers the positioning-washout mechanism, so don't block on it. UMCSENT (FRED) already backfilled as the consumer-sentiment leg. ⚠ Lag to release day (Wed/Thu) in the join.
  - [ ] §106a. Fetchers + cached panels (both publish full history); join to backtest dates with proper lag.
  - [ ] §106b. Ablation as L-tier sizing tilt: NAAIM bottom-quintile or AAII bear-top-quintile at entry → 1.15× (capitulation confirmation in the regime the strategy already needs). Per-fold; kill if single-epoch.
- [x] **§107. GDELT historical news tone — first-ever backtest of the news-sentiment family (FREE, bounded pilot).** The live engine scores news sentiment on every signal but the family has NEVER been historically validated. [GDELT](https://www.gdeltproject.org/) is 100% free (raw files + BigQuery), archives to 1979, GKG with per-org tone from 2015. Entity→ticker mapping is the hard part — pilot is bounded: 20 IS tickers × 2015+, company-name match in GKG organizations, daily tone z-score panel. Question: does negative-news-tone-at-oversold-entry predict the bounce (capitulation) or the knife (repricing)? Either answer recalibrates a live family that currently runs on faith. **Shipped 2026-06-11:** switched fetcher to GKG 1.0 daily zip files, added concurrent downloads, fixed cross-sectional `--gdelt` merge in `cross_sectional_alpha_model.py`. **Validated 2026-06-12:** full 2015+ panel (74,189 ticker-day rows); per-trade `--gdelt` tilt fired on **0/217** trades and produced identical metrics to baseline; cross-sectional `--gdelt --placebo --walk-forward` net Sharpe **0.304** vs baseline **0.307** (Δ -0.003, inside placebo noise). **Verdict: NOT deployed as a sizing tilt.** Infrastructure retained for live news-sentiment family and forward SPRT reuse.
- [ ] **§108. FINRA ATS dark-pool weekly per-ticker (2014+) — institutional participation context (FREE).** ⚠ **Access path corrected 2026-06-11:** the OTC Transparency *website* returns HTML — use the **FINRA Query API, which works UNAUTHENTICATED**: `POST https://api.finra.org/data/group/otcMarket/name/weeklySummary` with JSON body `{"limit":N}` returns data (verified live); per-security weekly detail is a sibling dataset in the same `otcMarket` group (enumerate via the API metadata endpoint; add `compareFilters` on `issueSymbolIdentifier` + `weekStartDate` for the universe pull). ⚠ 2-week publication lag (Tier 1) — a slow regime/quality feature, not an entry trigger: dark-pool share trend as institutional-participation context for L8-style quality sizing. 12 years backtestable; also replaces the live `dark_pool.py` real-time-only stubs with something validatable.
- [ ] **§109. Wikipedia pageviews attention spike (2015-07+) — retail panic confirmation (FREE).** [Wikimedia REST API](https://www.nature.com/articles/srep01801): daily per-article views, free, clean. Literature is mixed-to-positive ([attention L/S strategies profitable in recent work](https://www.sciencedirect.com/science/article/abs/pii/S0165176524003203)). Hypothesis fit: pageview spike + oversold print = retail-visible panic (the fear premium made measurable per-ticker). Bounded test: company-page views for the IS universe, spike z-score at entry as sizing context, 2015+ subperiod, per-fold.
- [x] **§110. Free per-stock options chain — REROUTED from OCC to CBOE delayed-quotes JSON (live-only, verified working 2026-06-11).** theocc.com is Cloudflare-challenged — but **`https://cdn.cboe.com/api/global/delayed_quotes/options/{SYMBOL}.json` works with no auth** (verified live): full chain per symbol with **bid/ask, IV, OI, volume, and greeks per contract**. Strictly better than the OCC plan: (a) per-stock PCR + OI for the live §49/§69–§72 options family, independent of yfinance and immune to Polygon 403s; (b) per-contract IV means a **self-accumulated IV-rank series** starts the day a nightly snapshot job ships — every month of accumulation shrinks what the paid §98 ORATS month has to answer (flow hypotheses become testable on own data; only deep IV *history* still needs ORATS). Action: nightly snapshot job → `options_chain_daily` table (universe tickers), wire `options.py` fallback order Polygon → CBOE → yfinance. No deep history → backtest n/a; accumulate-forward from day 1. **Shipped 2026-06-11:** `OptionsChainDaily` model + migration, `services/options_cboe.py`, `scripts/snapshot_cboe_options.py`, nightly supervised job in `main.py`, fallback rewire, tests.

- [ ] **§111. Cross-sectional model → LIVE promotion gates (pre-registered 2026-06-11, BEFORE any forward shadow data is read).** Both shadows (h=21 `crossSectionalShadowPct` since 2026-06-09, h=63 `crossSectionalShadowPctH63` since 2026-06-11) are accruing forward data. This section locks WHEN each may touch real behavior — changing these criteria after peeking at the forward sample invalidates the test (§92 discipline). Three escalating tiers:
  - [ ] §111a. **Tier 1 — sizing haircut on existing signals (h=21; criteria already locked in code).** `SHADOW_PROMOTION_CRITERIA` in `cross_sectional_shadow.py`: ≥150 resolved signals carrying the h=21 percentile AND bottom-decile (≤10th pctile) live WR ≥3pp worse than the rest AND top-decile WR ≥ bottom-decile WR. Then and only then flip `_SHADOW_SIZING_ACTIVE` (activates the 0.75× positionSizeScale haircut on bottom-decile names — a haircut, never a block). Activation must come from `check_promotion_criteria()` returning True, not a manual override.
  - [ ] §111b. **Tier 1 for h=63:** identical criteria evaluated independently on `crossSectionalShadowPctH63` (own N≥150 clock, started 2026-06-11). If both horizons pass, apply whichever shows the larger bottom-decile WR spread — never stack two XS haircuts on one signal.
  - [ ] §111c. **Tier 2 — standalone dollar-neutral L/S book with real capital (the backtest-0.616 product).** ALL of: (i) ≥12 months of live shadow rank-vs-outcome IC > 0 (monthly Spearman of percentile vs realized relative return; ≥7/12 months positive); (ii) §111a or §111b passed (proof the ranking transfers outside the research harness); (iii) short-leg execution verified — locate/borrow available at ≤150bps/yr for bottom-decile names through Alpaca/IBKR; (iv) ≥1 quarter paper-traded through the existing paper/live parity path with realized one-way slippage ≤20bps (the cost sweep says the edge dies ~40bps); (v) nested-horizon validation re-run including the forward period still selects h=63 ex ante. Initial allocation ≤5% of capital, quarterly rebalance, review after 4 rebalances.
  - [ ] §111d. **Kill criteria (equally pre-registered):** if after 12 months neither §111a nor §111b passes, or the live monthly IC is ≤0 in aggregate, retire both shadow fields, log the negative result in LEARNINGS, and do NOT re-tune thresholds against the same forward sample — a new threshold needs a new forward window.

**Explicitly rejected after research** (so they don't get re-proposed): CBOE put/call CSVs (403'd, DataShop-only — known since 2026-06-08), Google Trends (rescaling/quota artifacts make panels non-reproducible; Wikipedia pageviews dominate it), 13F-based ownership (quarterly + 45d lag — horizon mismatch, already deferred), IEX HIST pcap files (free but parsing cost ≫ value for daily signals), iBorrowDesk borrow fees (unofficial scrape, spotty history — revisit only if §104/§105 confirm the squeeze-fuel channel).

### Next Sharpe×N agenda — §87–§94 (added 2026-06-10)
Goal: raise Sharpe while holding or growing trade count. Ordering reflects expected value ÷ effort.
**Guardrails (hard-won, from §83 / exit-sweep / §86 per-fold lessons):** (1) prefer **sizing over filtering** — sizing is the only lever that has repeatedly added Sharpe at zero N cost (L7 +0.05, L8 +0.06, score-band +0.05); filters that lift per-trade Sharpe almost always lose it back through √N (ATR≤70 trap). (2) Judge changes on **per-trade Sharpe + CAGR + MaxDD**, never portfolio ANN Sharpe (event-time annualization rewards turnover; the exit-sweep "winner" was an artifact). (3) **Per-fold walk-forward** before believing any aggregate number (the §86 SI feature sold a false dawn one fold wide). (4) Per-sector application over global gates (LEARNINGS insight #5).

- [~] **§91. Short-interest rising-SI sizing tilt — wired, live read positive, backtest inconclusive (2026-06-10).** `simulate_ticker()` now accepts `si_rising_map`; applies 1.15× when `si_rising=True`. `--si-rising-sizing` flag added. Postgres `short_interest_biweekly` exported to `data/cache_si/si_panel.json` (182 tickers, 36K rows). **Live read (N=335 resolved signals):** rising SI WR 39.3% avg +1.01% vs falling SI WR 38.0% avg −1.41% — **+2.42pp avg spread**, directionally consistent with first read. **Backtest:** only 3/217 trades had SI data (most trades pre-2017). Deploy gate: live resolved N≥50 with rising SI before evaluating sizing impact. ΔN = 0.
- [x] **§95. Graduated DD-throttle — VERIFIED LIVE (2026-06-10).** Already operational in `portfolio_allocator.py` lines 415–441. Scales new positions 0.5× when >3% drawdown from peak.

- [~] **§86. Market-Neutral Cross-Sectional Ranking Architecture** — Move from time-series prediction to cross-sectional ranking. **v1 built 2026-06-09** in `backend/scripts/cross_sectional_alpha_model.py`. RESULT: OOS 2019→2026 **net Sharpe ≈ 0.44–0.50** (gross 0.73–0.78), mean IC +0.018, quintiles NOT monotonic. Beta-neutrality lowers vol but adds no alpha — "1.0+ mathematically" is a fallacy (Sharpe = IC × √breadth × √turnover-eff; generic price-factor IC ≈0.018 caps it). Honest verdict: competitive with the ~0.28 IS / ~0.14 fwd single-name engine, NOT a ceiling break. Data caveats: `cache_earnings` is dates-only (proximity feature, no surprise); short interest is Postgres bi-weekly 2017-12+ (`--short-interest` opt-in). **STATUS 2026-06-09 (Step 10):** the original 0.44–0.50 leaned on pre-survivorship-correction breadth; honest survivorship-corrected canon is net **−0.058 at the old 5d rebalance → +0.347 at 21d** (cost + stock-borrow robust). DEFAULT HORIZON raised 5→21; model deployed LIVE in SHADOW mode (observe-only). Net-positive but thin (CI grazes 0); see Step 10. **STATUS 2026-06-11 (Step 11):** First-pass alt-data results (h=21 net +0.308, h=63 net +0.769) were found to have **two implementation defects**: (1) market-wide UMCSENT/NAAIM/AAII were z-scored to death (std=0 → NaN → 0), so their claimed contribution was colsample noise; (2) FINRA SV and Wikipedia were merged same-day with ~1-day lookahead. Both defects are now fixed in code. Single-split previews with fixes: baseline 0.369, `--finra-sv` 0.414, `--wiki` 0.451, `--naaim` −0.182, `--naaim --wiki` 0.111; placebo noise 0.151–0.159. **STATUS 2026-06-11 (Step 12):** corrected WF complete — all alt-data Δs inside the placebo band (no alt-data claim stands; 0.769 permanently withdrawn). The HORIZON effect survived honest validation: `--nested-horizon` chose h=63 ex ante in 12/12 eval folds → nested net **+0.576 [CI +0.22, +0.91]**, haircut 0.000, cost/borrow-robust. **Parallel h=63 live shadow deployed** (`crossSectionalShadowPctH63`; §92 stays h=21-only). See Step 12.
  - [~] **Step 9 (decision): the ceiling is IC/data, not architecture.** Four 2023-24 "structural alpha" frameworks now evaluated against this engine's own data: (1) Meta-label+triple-barrier — **RETRAINED (2026-06-10)** on CSV with full 15 features (entry_prob, HMM, VIX term structure, sector momentum, FF ST_Rev); CV-AUC **0.4364** on N=217 — still below random, but all 15 features now have non-zero importance (was 3). `_MIN_META_AUC=0.52` gate added in `signal_ml.py`; model auto-activates only when retrain crosses threshold. Train/serve skew resolved, guard removed from `assembler.py`. Exit-sweep already "exhausted"; (2) Qlib cross-sectional — built §86, net ≤0.42; TopkDropout worse (Step 7); (3) Hierarchical RL — untrainable at N≈221, overfit guaranteed; (4) Adaptive sleeve allocation — sleeves just disabled (commit 3e4e102), 5d-rolling routing whipsaws at this N. ALL rearrange/filter existing alpha; none raise IC. Only real levers left: new ORTHOGONAL data (§62 options-IV, options-flow, short-interest velocity) or accept honest ~0.2–0.4. Paid alt-data still NOT justified until a free-data path shows IC > ~0.03. **[PARTIALLY OVERTURNED by Step 10 — see below: the ceiling claim holds for IC, but rebalance/cost structure DID cross the book to net-positive.]**
- [ ] **§85-2b. MD&A sentiment live monitoring** — `get_mda_delta()` bug fixed (2026-06-10). Historical audit: **0/566 resolved signals** had MD&A rationale. Going forward, tag signals that receive `mda_delta != 0` and compute ΔWR after N≥50 such signals accumulate. If no improvement vs baseline, disable the modifier.
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
- [ ] **QENG-3d. Execution policy simulator** — Compare market, limit, midpoint, delayed-entry, and bracket variants in paper/shadow mode. Promote only on cost-adjusted expected value.
- [x] **ACT-6. Run E2E Playwright tests** — DONE (2026-06-10). Playwright installed. 5 passed (health, landing, auth×3), 7 skipped (need owner creds in CI).
- [ ] **ACT-7. Validate bracket stop in Alpaca paper account** — Enable auto-execution for owner account on paper, trigger a manual signal delivery, and verify Alpaca dashboard shows bracket order legs correctly.
- [ ] **ACT-8. Install shap for ML-5 live audit** — Install `shap` and re-run live audit once ≥50 post-A19 resolved signals are available.
- [ ] **ACT-9. Push to GitHub to trigger CI/CD validation** — Verify the full CI/CD pipeline, including gitleaks scanning on Fernet ciphertext, coverage floor (25%), and deployment steps.

---

## 📊 Live Findings & Calibration TODOs
Actions derived from empirical performance audits on the live system.

- [ ] **WATCH-1. XLV Healthcare live WR contradicts IS promotion (2026-06-09, N=62).** Healthcare was moved to `_MR_SECTORS` (live-eligible) on the cross-sectional model's t=+2.12, but post-backfill live WR is **40.3% (−3.3pp, N=62)**. Not yet block-worthy (single ~7-week window, CI [29%–53%] straddles baseline) but no longer a small-N fluke. Re-check at N≥100; if still <45%, reconsider the IS promotion / add to watch-block.
- [ ] **OOS-1. Accumulate ≥30 live trades in OOS v7 tickers** — SYK, RMD, IDXX, ZBH, RL, DECK, POOL, NDAQ, CBOE, BR. Run `python scripts/backtest_technicals.py --oos`. If OOS v7 CLEAN Sharpe ≥ 0.10, promote to IS.
- [ ] **OOS-2. Accumulate ≥30 live trades in OOS v8 tickers** — LNC, AMG, PAYC, SIG, AEO. Cautiously evaluate the 0.2% Russell 2000 pass rate.
- [ ] **§85-2b. MD&A sentiment live monitoring (2026-06-09)** — `get_mda_delta()` bug fixed (was returning `{}` for all tickers due to broken EDGAR `-index.json` fetch). Historical audit: **0/566 resolved signals** had MD&A rationale. Going forward, tag signals that receive `mda_delta != 0` and compute ΔWR after N≥50 such signals accumulate. If no improvement vs baseline, disable the modifier.
- [ ] **CAL-1 / A25. Calibration v5** — Run `python scripts/backfill_confidence.py --force --apply` when ≥50 post-A19 resolved signals are available to reflect the corrected scoring pipeline.
- [ ] **ML-2 / A15. Sector-specific XGBoost models** — Retrain sub-models for concentrated sectors (e.g. XLK) when sector-specific resolved signals reach ≥200.
- [ ] **RISK-3. Position sizing live audit** — After N≥50 auto-executed trades, compare realized notional vs theoretical scaling. Check for rounding errors if mean size deviates >20%.
- [ ] **ACT-3. Sector-conditional calibration (CAL-V5)** — XLK Brier deviates +0.015, XLV deviates −0.016. Run `backfill_confidence.py --force --apply` with sector grouping to deploy separate isotonic curves.
- [ ] **ACT-4. Investigate live WR gap (Part b)** — Perform detailed validation on the remaining gap between live WR and IS WR after resolving EOD-batch delivery bugs.

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
- [x] **R10-7: Per-signal Kelly — RESEARCHED, NO-DEPLOY (2026-06-08).** Added `stats_kelly` + `kelly_size_mult` + the §Inv-K validator to `backtest_technicals.py`. **Key finding:** the universal 1.5s/2.0t stop/target makes reward:risk *constant* (realized b=0.83), so per-signal Kelly has no payoff term and is just a convex reshaping of conviction sizing. Exploratory half-Kelly (empirical p, wide [0.70,1.30] clamp) showed +0.022 IS Sharpe, but the **deployable** formula clamped to the live [0.85,1.15] envelope scored **−0.015 vs the incumbent linear L7** (0.25→0.24) — the gain didn't survive a realistic risk envelope (in-sample, N=221). **Decision: keep linear L7.** Future: revisit only with per-signal-varying R:R or an OOS-validated wider envelope. Validate via RISK-3 once N≥50 live trades.
- [x] **R10-8: Per-ticker friction — RESEARCHED, NO backtest change (2026-06-08).** Added the §R10-8 vol-scaled friction validator. **Findings:** (1) realistic large-cap friction ≈0.25% vs the flat 0.50%, i.e. the flat number is a deliberate ~2× conservative buffer — lowering it would manufacture fake Sharpe (0.23→0.30 is *all* lower assumed cost, not alpha), so flat 0.50% is **kept**; (2) the edge is **robust across volatility/spread terciles** (Sharpe 0.29 / 0.34 / 0.30). The backtest can't validate per-ticker friction (no historical fills). Deployable lever is sizing-down wide-NBBO-spread names live — §80 already penalises their *score*; a dedicated sizing lever is deferred (unvalidatable offline). Closing REF-1 TCA→allocator feedback + QENG-3d sim remain the live path.
- [ ] **R10-9: Sector Concentration (7.6 → 10)** — make limits **dynamic/correlation-aware** (size off the live covariance via **REF-5** HRP-in-scanner, not static 30/20%); unblock XLF/XLP/XLU/XLI by training **ML-2** sector XGBoost models that earn them back rather than hard-blocking.

### Product & Deployment
- [ ] **R10-10: Product Completeness (9.3 → 10)** — finish **FE-2** accessibility (WCAG 2.1 AA) and clear the remaining Pre-Launch items that gate user-visible flows (Telegram broadcast, SMTP digests, web push).
- [ ] **R10-11: Frontend (8.8 → 10)** — **FE-2** accessibility + lift Architecture sub-score: typed API client, ≥1 golden-path **ACT-6** E2E green in CI, and a Lighthouse perf budget enforced on PRs.
- [ ] **R10-12: Security Posture (8.0 → 10)** — rotate the **owner password** (Pre-Launch #1) out of source, enforce **HTTPS** (#2), move secrets to a vault/Railway secrets (not committed `.env`), and pass an external dependency + auth pen-test with no highs.
- [ ] **R10-13: Deployment Readiness (7.7 → 10)** — clear Pre-Launch #2/#3/#5/#9 (HTTPS, Stripe webhook, SMTP, VAPID) + **DEPLOY-2** Sentry/UptimeRobot + **DEPLOY-3** automated DB backups; demonstrate a green **ACT-9** CI/CD deploy + a restore-from-backup drill.

### Infrastructure & ML
- [~] **R10-14: ML Methodology (8.9 → 10)** ⏳gated — deploy the live entry model at **N ≥ 300** (Pre-Launch #7) once AUC delta clears 0.005; **REF-6 meta-label feature hardening DONE (2026-06-10)** — all 15 features now flow from backtest to live (14 + §89 FF ST_Rev), but CV-AUC 0.4364 < 0.52 activation threshold → meta_prob disabled until N growth pushes AUC above gate; **ML-2** sector sub-models pending (≥200 sector-resolved signals); require champion/challenger shadow-win before promotion.
- [ ] **R10-17: Data Pipeline (8.3 → 10)** — prove live reliability, not just breadth: health-scorecard + PIT feature store run a full week with 0 errors; remove the remaining dead `^TRIN`/`^NYAD`/`^BDI`/ETF-fundamentals fetches (or route them to providers that serve them); add **§84** point-in-time data so the pipeline is survivorship-correct.
- [~] **R10-18: Test Coverage (7.5 → 8.0, partial)** — **DONE (2026-06-08):** `tests/test_r10_hardening.py` (8 tests). **DONE (2026-06-10):** §69–§74 gate unit tests in `tests/test_gates_5982.py` (all passing) + SPRT monitor 12 tests + E2E framework installed. **Still open:** true end-to-end "scan persists against real Postgres" test; **TEST-4** mutation testing (>70%).

---

## 👁️ Known Issues
Ongoing known issues or constraints.

- ~~Default owner password in source~~: FIXED (2026-06-09) — `.env` has 32-char secure password.
- **XLF/XLP/XLU/XLI blocked**: Blocks in place due to negative contribution. Requires sector-specific XGBoost retraining to resolve.
- **Calibration recalibration post-A19**: Calibration v4 used pre-A19 data only. Needs recalibration once post-A19 resolved signals accrue.

---

## ✅ Completed Tasks Archive
*Note: All items completed as of v8.1 (2026-06-08) and prior versions.*

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
- **§92. Pre-specify the cross-sectional shadow activation gate (2026-06-10).** `SHADOW_PROMOTION_CRITERIA` locked; promotion criteria immutable.
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
