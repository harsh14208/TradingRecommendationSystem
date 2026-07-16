# Signal.Trade — Development Progress

> **Version: v8.9** · Updated: 2026-07-15 · Server: `uvicorn main:app --host 0.0.0.0 --port 8000`
>
> **v8.8.7 (2026-06-18) — Backtest realism, QA audit hardening, entry-score relaxation, sources removal, elite tier, and aiohttp CVE patch.** Replaced the Backtest Lab toy simulator with real `/api/signals/backtest/simulate` trade replay; shipped a major QA pass (WebSocket reconnect, a11y handlers, focus traps, mobile parity, form validation, API retry); lowered backtest `BUY_THRESH` 50→45 and live BUY score bar 35→32 (forward-validated, first live read pending); removed the dead `/api/sources` module; widened the user-tier check constraint for `'elite'`; bumped `aiohttp` to fix 8 CVEs and keep CI green. **Ratings: 8.9/10 product · 8.3/10 B+ quality** (Frontend 9.0→9.1, Product Completeness 9.4→9.5, Security Posture 8.2→8.3; headline unchanged per v8.0.1 discipline).
>
> **v8.8.5 (2026-06-12) — Dashboard UI scaling + mobile panel navigation shipped.** Removed the desktop `zoom:0.8`/`125vw` hack that clipped the right edge; replaced it with a desktop-only `styles-desktop.css` density override. Mobile dashboard is now a horizontal scroll-snap carousel (Feed/Detail/Delivery) with a bottom arrow/dot pager. Fixed missing Backtest/Watchlist/Market icons in the mobile nav, made the detail pane and topbar responsive on phones, and made the signal-card **Full detail** button jump to the center panel. **Ratings: 9.0/10 product · 8.3/10 B+ quality** (Frontend 8.8→9.0, Product Completeness 9.3→9.4).
>
> **Live-trading milestone framing:** The platform is architecturally complete for unattended broker auto-execution (Alpaca + IBKR, encrypted credentials, drawdown circuit-breaker, bracket-stop orders, per-user limits, global kill switch). The remaining gate is empirical: live win rate must be consistently > 55% before real-money auto-execute is enabled. See [RUNBOOK.md](RUNBOOK.md) §7 and [HOWTO.md](HOWTO.md) §11 for the go-live checklist.
> **v8.8 (2026-06-12) — §117 sector-specific XGBoost promotion gate implemented + tested.** Blocked sectors (XLF/XLP/XLU/XLI) are now unblocked only by an explicit, auditable QENG-1c promotion record (`ModelRegistry` + `ResearchExperiment`), never by artifact file existence — the v8.1 live-book leak pattern is structurally removed. `services/sector_ml_promotion.py` is the single source of truth; `delivery_gates.py` and `assembler.py` consume it via a runtime `promoted_sectors` override. Sector model training raised to ≥100 backtest trades + purged expanding-window CV; `scripts/promote_sector_model.py` enforces OOS AUC ≥0.55, positive cost-adjusted Sharpe, rollback plan, and expiration. New tests pass: `tests/test_delivery_gates.py` (promoted/unblocked/expired/fail-closed) and `tests/test_train_sector_model.py` (insufficient data, beats champion, registry record, promotion checklist, rejection). No sector model has been trained or promoted yet; ratings unchanged until live-and-proven.
>
> **v8.7 (2026-06-12) — Free alt-data paths wired + ablated + TCA slippage feedback loop completed.** (1) CBOE options snapshots self-accumulate into per-ticker IV history (`services/options_cboe.py` → `data/cache_options/options_iv_history.parquet`), enabling `iv_rank` without paid historical data. (2) FINRA ATS weekly dark-pool participation merged into cross-sectional panel with 2-week PIT lag (`--finra-ats`). (3) SEC FTD velocity feature `ftd_pctile_chg_1m` added and panel backfilled to 2004. (4) NAAIM/UMCSENT rolling percentiles and Wikipedia `views_z_xs` cross-sectional attention wired. (5) §118 live TCA slippage feedback wired into `portfolio_allocator`: expected/realized slippage floor sizes orders against a configurable 20 bps threshold. (6) `test_portfolio_allocator_optimizations` made deterministic via monkeypatched market data/slippage. (7) Walk-forward/placebo ablations vs baseline: **no free alt-data config clears the noise floor** at h=21; FINRA ATS historical backfill is blocked by the endpoint; CBOE IV-rank is live-forward only until ≥252 snapshots accrue. **Ratings: 8.9/10 product · 8.3/10 B+ quality** (Stats.md §15 v8.7: Data Pipeline 8.4→8.5, Execution & Friction 7.8→7.9, Test Coverage 7.9→8.0; overall unchanged).
> **v8.6 (2026-06-11, later same day) — Alt-data retraction + nested-horizon validation + parallel h=63 shadow.** (1) §104–§110 cross-sectional alt-data claims **retracted** after a code review found two harness defects (market-wide NAAIM/UMCSENT/AAII z-scored to dead all-zero columns; FINRA SV/Wikipedia merged with ~1-day lookahead) — both fixed; new `--placebo` control shows every alt-data Δ inside the ~±0.1 noise band at both horizons (no alt-data claim stands); panels migrated pickle→Parquet (numpy version-skew irreproducibility); strict merge-failure guards; pyarrow into backend/venv. (2) **First selection-clean Sharpe validation since the IS budget was declared spent:** `--nested-horizon` (per-fold ex-ante horizon choice from prior folds only, grid {21,40,63}) picked **h=63 in all 12 eval folds (2014–2025)** → nested net Sharpe **+0.576 [90% CI +0.22, +0.91]**, selection haircut 0.000; full h=63 track net 0.616 [CI +0.29, +0.94], cost-robust to 40bps (+0.481, where h=21 goes negative), borrow breakeven ≈700bps/yr. (3) **Parallel h=63 live shadow deployed** (server restarted): `*_h63.json` artifacts, `score_batch_h63()`, `crossSectionalShadowPctH63` per directional signal; §92 promotion criteria stay h=21-only. §96b close-entry A/B re-confirmed neutral (ΔSharpe +0.01, lower MaxDD; closes the fill-timing confound in live-vs-IS reconciliation). **Ratings: 8.9/10 product · 8.3/10 B+ quality** (Stats.md §15 v8.6: Backtest Infra 7.9→8.1; the h=63 result is shadow-only and moves nothing per v8.0.1 discipline).
> **v8.5 (2026-06-11) — External research agenda §96–§103 complete + infrastructure hardening.** §96a-d overnight/intraday decomposition (61% alpha from overnight gaps), §96b close-entry A/B neutral (ΔSharpe 0.00), §97a limit-order grid all failed deploy bar, §99 SPRT protocol live (4 hypotheses pre-registered, monitor built, admin surfaced), §100 SimFin fundamentals wired into cross-sectional model, §101 TSMOM sleeve Sharpe 0.57 (4/4 epochs positive, deploy bar not cleared), §103 decay monitor with VIX regime context. Infrastructure: §85-2 MD&A EDGAR bug fixed (primaryDocument endpoint), fill-rate counter bug fixed, VAPID keys generated, E2E Playwright 5 passed, §69–§74 gate unit tests added. **Ratings: 8.9/10 product · 8.3/10 B+ quality** (Stats.md §15 v8.5: Security 8.0→8.2, Deployment 7.7→7.9, Test Coverage 7.7→7.9, Backtest Infra 7.8→7.9).
> **v8.4 (2026-06-10 evening) — Live delivery overhaul: the live-vs-IS gap was mostly delivery leaks, not signal.** DB-level audit found and same-day-fixed six leaks: (1) **sector model-file "dynamic unblock"** — XLF/XLP/XLI were never actually blocked (file existence lifted the block); they were **32% of the delivered book at ≈−1.4%/trade** (clause deleted, 6 files quarantined to `data/quarantine/`); (2) **SELL delivery disabled** (35.2% net WR, −1.00%/trade, conf-35 floor bypass; backtest §32 had already disabled SELLs); (3) **all 6 `sector_rs` couplings decoupled** to static SECTOR_MAP (81% of the historical resolved sample ran with per-sector calibration silently OFF → all pre-fix live audits contaminated); (4) **§55 + §14 hard blocks deleted from delivery** (fresh canon A/B: §14 **−0.06 Sharpe, harmful**); (5) **DELIV-1 entry-validity guard** — latency was confounded with sector (clean-sector stale deliveries earn +2.12%/trade); EOD batch now skips on price escape (≥entry+0.5×ATR or ≤stop), not age; (6) **`skip_reason` persisted** (migration `4a7f6b33eb49`) — delivery funnel auditable by query. **Honest re-baseline:** clean live book (May+ BUYs ex-blocked) = **57.8% net WR, +2.06%/trade net** vs +0.25% blended old policy. **§87 verified & deployed:** weighted A/B on v10.9 canon Sharpe 0.24→**0.30 (+0.06)**, ΔN=0 → `_apply_l10_conviction_sizing()` live in `scanner.py` + first global sizing-stack clamp [0.10, 3.00] (+5 tests). **IS canon v10.9:** N=217, WR=69.1%, Sh=0.24, MC P5=0.07 ✅, Lo CI [0.10, 0.37] ✅, **deflated Sharpe FAILS at honest 744 trials** ⚠ → IS lever statistically spent; edge proof shifts to the post-fix forward window. Meta-model: v8.3 CRITICAL closed (15-feature retrain + `_MIN_META_AUC=0.52` self-gating floor → meta_prob OFF at CV-AUC 0.4364). **Ratings: 8.9/10 product · 8.2/10 B+ quality** (Stats.md §15 v8.4: Live Alpha 6.8→7.6, ML 7.2→7.8, Sector 7.8→8.3, IS 7.4→7.6, Cal 6.8→7.0). Full data: `Stats.md §DELIV`.
> **v10.8 backtest — Sharpe improvement sweep (2026-06-09):** 12 candidate approaches tested on 100-ticker/23yr IS. Score-band sizing (L7 non-linear step function) → +0.05 Sharpe, zero trade-count impact. Dynamic RSI stops (2.0× ATR when RSI<30) → embedded in baseline. MR-count=2 (≥2 MR conditions vs 1) → +0.01 Sharpe, −1 trade. Consecutive-score filter → +0.14 Sharpe (−73% trades) — best as high-conviction tier, not main flow. Score acceleration and entry-delay both hurt. Live engine updated: `assembler.py` L7 score-band sizing + `_has_mr` MR-count=2 + `helpers.py` dynamic RSI stops. See `docs/Stats.md §83`.
> **§87–§94 Sharpe×N agenda (2026-06-10):** All free-subscription items implemented and validated. §87 L10 consec-score sizing (initial +0.03 claim corrected same day — verified weighted A/B: **+0.06**, ΔN=0; deployed live in v8.4). §88 calm-regime sleeve ABANDONED (0 trades in 23yr — structural mismatch). §89 FF ST_Rev wired as 15th meta-label feature; §89a regime sizing negligible (+0.008); §89b factor attribution confirms genuine alpha (+0.87%/day, p=0.044, R²=0.05). §90 WATCH bench all rejected (0/9 trades). §91 SI rising tilt wired, live +2.42pp spread, backtest unvalidatable. §92 shadow criteria locked. §93a sector_rs bug fixed; §93c net-of-friction calibration (43.6%→40.5%); §93d gap decomposition v2 (25.5pp WR gap, midday 11–12 ET catastrophic, p=0.000). §94 per-sector hold-days (+0.04 Sharpe). Full 23yr backtest: 217 trades, 69.1% WR, 0.24 Sharpe, −2.31% MaxDD. Strategy is structurally a **VIX 20–30 stress-regime play** — 100% of trades in that window. Post-2022 epoch (rate-hike cycle) shows negative Sharpe (−0.10), explaining live underperformance.
> **Ratings live in [`docs/Stats.md §15`](Stats.md) (single source of truth, v10.11). This file is a chronological dev log.**
> ~210 tickers (incl. 52 leveraged ETFs) · 150 API endpoints · dual auto-execution brokers (Alpaca + IBKR)
> **Data: Polygon.io-first (bulk OHLCV + quotes + reference) · yfinance fallback · FRED (macro) · EDGAR (fundamentals/8-K) — pooled aiohttp + cached TLS across 20 modules**
> **Database: PostgreSQL 16 (primary) · single Alembic head · Alembic-only prod schema policy ([`SCHEMA_CHANGE_POLICY.md`](SCHEMA_CHANGE_POLICY.md))**
> **Tests: 2615 passed, 33 skipped (ex-e2e) · run the full suite with `--ignore=tests/e2e` (e2e leaves a running event loop) · Backtest IS v10.8: N=155, WR=67.1%, Sharpe=0.25 with L7 score-band sizing + MR-count=2 (survivorship-corrected + §63 ADF gate)**
> **v8.2 (2026-06-09) — Sharpe improvement sweep + live engine updates.** v10.8 backtest sweep: 12 candidate approaches on 100-ticker/23yr IS. Score-band sizing (+0.05 Sharpe, zero trade impact), MR-count=2 (+0.01 Sharpe, −1 trade), and dynamic RSI stops all validated and shipped live. IS Sharpe 0.23→0.25. See `docs/Stats.md §83`.
> **v8.1 (2026-06-09) — Survivorship correction + new live gates + correctness fixes + open-source quant-library audit.** Survivorship bias corrected via free PIT S&P constituents (the #1 named ceiling); new live gates (§14 FRED macro-regime, Polygon short-volume, dynamic sector limits + XLI ML); live correctness fixes (`sector_etf` decouple — was nulling ~81% of signals; cohort-enrichment restore; dark_pool restart-storm); §63 cointegration ADF correctness fix + macro-regime HMM→hmmlearn (both live); cross-sectional model net-positive at h=21 (net +0.347, borrow-robust) deployed in **SHADOW**. **Overall 8.8/10 product · 8.6/10 quality** (+0.1 from v8.0.1; shadow/research work excluded per "implemented ≠ working live"). See Stats.md §15.
### v8.8.9 (2026-07-15) — R7 drawdown throttle, MAX21 low-MAX filter graduation, and backtest parallelization

**R7 step-function drawdown throttle.** New positions are halved once the portfolio drawdown exceeds `DD_THROTTLE_TRIGGER_PCT` (default 3.0). The multiplier is binary — 1.0 below the trigger and `DD_THROTTLE_MULT` (default 0.5) at or above it — not a continuous ramp. `services/portfolio_allocator.py` applies this to target weights and `services/broker_svc.py` applies the same multiplier to notional order sizes. Unit tests and docs updated. The `--portfolio` backtest default now runs with the R7 throttle enabled.

**MAX21 low-MAX filter graduates at the 55th percentile.** Re-validated on the honest 26-year PIT-corrected MR-only canon (N=313, Port Sharpe 3.28, MaxDD −8.43%). Contrary to Chen et al., this vol-gated book performs better on *low*-MAX names. Isolated MAX21 effect (no R7 DD-throttle):

| `--max21-filter` | Trades kept | Port Sharpe | Max DD | CAGR |
|:---|---:|---:|---:|---:|
| baseline (off) | 313 | 3.28 | −8.43% | +4.31% |
| **0.55** | **264** | **3.75** | **−7.15%** | **+4.10%** |

The 0.55 setting keeps 84% of trades while lifting isolated Sharpe +0.47 and cutting MaxDD by ~1.3pp. When the R7 step-function DD-throttle is stacked (the current `--portfolio` default), the combined path is Port Sharpe **4.35**, MaxDD **−5.17%**, CAGR **+4.2%** — that 4.35 is the combined MAX21 + DD-throttle effect, not the isolated MAX21 lift. `services/technicals.py` now emits `max_21_q55`, `services/gates/technicals.py` `Max21Gate` blocks high-MAX BUYs against the per-ticker expanding 55th percentile, and `backend/scripts/backtest_technicals.py` defaults `--max21-filter` to 0.55. Docs in `RESEARCH_SIGNAL_ENGINE_IMPROVEMENTS.md` updated.

**Backtest parallelization.** Converted `backend/scripts/backtest_technicals.py` from `multiprocessing.Pool` to `ThreadPoolExecutor` with `_run_simulation_parallel` / `_filter_simulation_results` helpers, applied to the main run, calm-sleeve, gate validation, exit-sweep, full-signal comparison, and research sections. A 15-ticker `--quick` run dropped from ~5 min to ~22 s; the full 26-year run completes in ~8 min (was much longer). Controllable via `BACKTEST_WORKERS` env var (default 8).

**Other fixes today.** PIT constituent regeneration without the 2003-01-01 start clamp; live-engine log-audit fixes (tz bug #3, dead RSI-divergence, test-suite clobbering prod model stats); batch-1/2/3 wrong-signed/too-weak gate corrections from most-fired and mismatch audits; vol-targeting units/vol-annualization bugs fixed and claims retracted; §MAX tier analysis + §ON overnight/intraday decomposition auto-run added; patent/research-item harnesses and graduation report.

### v8.9 (2026-07-15) — Cross-sectional h=63 sleeve promoted to paper trading

**Highest-priority item from the MAX21/R7 audit reset.** The research-promoted h=63 cross-sectional model (nested-horizon net Sharpe +0.576, 90% CI excludes 0, cost- and borrow-robust) is no longer just a metadata shadow. It now runs as a standalone long/short paper sleeve inside the regular scan cycle.

- `services/cross_sectional_sleeve.py`: builds a dollar-neutral top/bottom-decile L/S book from `score_batch_h63()`, emits entry signals for today's desired legs, and emits `sleeve_exit` signals for names that fall out of the book.
- `services/scanner.py` Step 5e (`_build_cross_sectional_sleeve_signals()`): fetches live Alpaca paper equity, loads active `CrossSectional` positions, allocates capital via `services.alpha_sleeves.allocate_cross_sleeve_capital()`, and appends sleeve signals after the directional structural filters.
- `services/scanner.py` `_maybe_paper_trade()`: honors per-name `sleeve_notional`, closes shorts on `BUY` flips, closes longs on `SELL` flips, and handles `sleeve_exit` signals without opening new positions.
- Cohort discipline preserved: all sleeve signals are `cohort="shadow"`, `style="position"`, `recommendedHoldDays=63`, and paper-trade only — no Telegram/Discord spam.
- Research blend: MR × XS-h63 correlation ≈ −0.02; a 50/50 risk blend produced Sharpe ~1.31 vs MR-alone ~0.88.
- New tests: `tests/test_cross_sectional_sleeve.py` (8 cases) and `tests/test_scanner_cross_sectional_sleeve.py` (3 cases) pass.
- Docs updated: `docs/RUNBOOK.md` §6.4.1.

### v8.8.8 (2026-06-27) — Signal Engine Confidence Ontology Refactor

**Why this matters:** the live engine had overloaded `confidence` with at least
five different concepts (raw score, calibrated probability, risk overlay, peer
confirmation, scan-relative ranking).  Post-scan steps were mutating the value
after calibration, so the stored "calibrated" confidence was no longer a true
probability.  This made attribution, model training, and user communication
ambiguous.

**Changes (Stage A):**
- `services/engines/assembler.py`: split signal dict into `alphaScore`,
  `rawConfidence`, `calibratedProbability`, `displayConfidence`,
  `rankScore`, and `rankPercentile`.  `calibratedProbability` is produced by
  calibration and never mutated afterwards.  Legacy `confidence` is retained as
  an alias for `displayConfidence`.
- `services/signal_engine.py`: post-scan peer confirmation, Polygon related
  companies, supply-chain propagation, and cross-sectional ranking now mutate
  only `displayConfidence`, `rankScore`/`rankPercentile`, or
  `positionSizeScale`; `calibratedProbability` is preserved.
- `services/gates/warning.py`: extracted the final overbought/oversold warning
  deconfliction into a pure, tested function; replaced the inline replication
  in `assembler.py`.
- `models.py` + Alembic migration `700fef99ff87`: added
  `calibrated_probability`, `display_confidence`, `alpha_score`, `rank_score`,
  `rank_percentile` columns to `signals`.
- `services/scanner.py` and `services/options_scanner.py`: persist the new
  ontology columns.
- `tests/test_signal_engine_confidence.py`: now tests the real production
  function, not a local replica.
- `tests/test_confidence_invariants.py`: new invariant tests proving
  calibration is last, `calibratedProbability` is immutable post-assembly,
  bounds hold, and HOLD signals have no levels.

**Ratings impact:** no score move yet — the refactor is structural and
forward-protective.  Live win-rate attribution and calibration quality should
improve as the ontology prevents probability drift, but that must be proven in
forward data before ratings change.

**Tests:** signal-engine-related tests pass; full non-E2E suite has the same
pre-existing failures as before the refactor (broker mocks, FOMC date imports,
paper-router SecretStr issues, flaky WebSocket test).  No new regressions
introduced by this change.

### v8.8.8b (2026-06-27) — Point-in-Time Ticker Performance Gate (Stage B)

**Why this matters:** the static defensive-ticker BUY blocklist (`KO`, `PEP`,
`ABBV`, `MRK`, `LLY`, `NKE`, `V`, etc.) mixed live-validated and backtest-derived
exclusions.  Hardcoded ticker bans encode look-ahead selection bias and can
persist long after a ticker regime changes.

**Changes:**
- New `services/gates/ticker_performance.py` with:
  - Decay-weighted ticker hit-rate computation over a 180-day window.
  - Minimum sample guards (`n >= 5` to block, `n >= 3` to caution).
  - Auto-retirement: a ticker unblocks automatically when recent forward
    performance improves above the threshold.
  - ATR-rank viability guard turns marginal blocks into size reductions when
    the stock is low-friction.
- `services/signal_engine.py`: `scan_all()` refreshes the snapshot once per scan
  from the DB if it is stale/absent.
- `services/engines/assembler.py`: `TickerPerformanceGate` runs in **shadow
  mode** alongside the legacy static blocklist.  It appends rationale cards but
  does not change the action.  Disagreements between the static list and the
  dynamic gate are logged as `[ticker_perf_shadow]`.
- `tests/test_ticker_performance_gate.py`: unit tests for snapshot decay,
  windowing, blocking, caution sizing, low-ATR waiver, auto-retirement, and
  shadow mode.
- Gate can be promoted to a hard block by setting `TICKER_PERF_GATE_ENABLED=1`.

**Rollout plan (treated as an experiment):**
- Keep shadow mode active for 30 days.
- Every scan persists both decisions to `ticker_perf_shadow_decisions`.
- After signals resolve, run `scripts/analyze_ticker_perf_shadow.py` to compare:
  - Static vs dynamic decision overlap matrix
  - Forward WR and avg return for each disagreement bucket
  - Missed winners / saved losers from each gate
  - Volume impact
  - Sector skew introduced by the dynamic gate
  - Outcome-horizon alignment (`outcome_pct_7d` vs `recommendedHoldDays`)
- Promotion criteria: dynamic gate must not materially increase missed winners,
  must show comparable or better saved-loser rate, and must not introduce
  meaningful sector skew.  If criteria are met, delete `_DEFENSIVE_BUY_BLOCK`
  and default `TickerPerformanceGate` to `enabled=True`.
- Static list may be retained as a temporary emergency denylist with explicit
  expiry dates if needed, but it should not be the primary gate.

**Tests:** signal-engine / gate tests pass; no new regressions.

### v8.8.7 (2026-06-18) — Backtest Realism, QA Hardening, Entry-Score Relaxation, Sources Removal, Elite Tier, aiohttp CVE Patch

**Why this matters:** the Backtest page was advertising impossible simulated performance (Sharpe 9.12, CAGR 108.8%, Max DD −1.4%) on the same screen as the real live backtest (Sharpe 0.65, Max DD −18.5%), undermining trust. A separate QA audit found a11y/mobile gaps, the entry-score band just below the cutoff carries forward-generalizing alpha, the `elite` tier could not be persisted in Postgres, and a CVE-blocked `aiohttp` was breaking CI.

**Changes:**
- `frontend/src/cin.backtest.jsx`: removed the deterministic toy `runBacktest` simulator and parameter/comparison sliders.
- `frontend/src/cin.backtest.jsx`: now fetches `/api/signals/backtest/simulate`, sorts signals by date, compounds net returns from a $100K start, and draws the equity curve + drawdown shading from real trade replay.
- `frontend/src/cin.data.jsx`: deleted `runBacktest` and its export.
- `frontend/src/cin.backtest.jsx`: headline metric cards show CAGR/Sharpe/win rate/max drawdown computed from the replay curve; sidebar shows cost drag, stop-hit rate, and target-hit rate.
- `backend/routers/signals.py` + `backend/routers/public.py`: per-ticker Sharpe now requires ≥15 observations and is capped at 3.0, preventing absurd tiny-sample values.
- `backend/routers/sources.py`, `backend/services/source_svc.py`, `backend/tests/test_routers_sources_unit.py`: deleted.
- `frontend/src/app.views.jsx`, `frontend/src/cin.app.jsx`, `frontend/src/cin.market.jsx`, `frontend/src/cin.market-data.jsx`, `frontend/src/site.jsx`, `frontend/src/mobile.jsx`: removed source-status sections and source toggles.
- `frontend/src/app.auth.jsx`, `app.jsx`, `app.modals.jsx`, `app.signal.jsx`, `app.ui.jsx`, `styles.css`, `mobile.css`, `site.jsx`: QA audit hardening — WebSocket reconnect with exponential backoff, keyboard handlers on role="button", overlay focus traps + Escape-to-close, hash-based overlay URL state, paper-trade double-submit guard, API retry with exponential backoff, tweak-save error feedback, skeleton screens, mobile nav parity (13 items), 44px touch targets, pull-to-refresh, email/password/broker-key validation, note maxLength counter, search debounce, chart fetch timeout, aria-live signal announcements, skip-nav link, beforeunload guard for unsaved forms.
- `backend/scripts/backtest_technicals.py`: `BUY_THRESH` 50→45; new `--relax-sweep` mode; `buy_thresh_override` threaded through `run_oos_validation`.
- `backend/services/engines/helpers.py`: live BUY score bar 35→32 (conservative ~10% mirror of the backtest relaxation).
- `backend/tests/test_engines_helpers_unit.py`: updated BUY-bar boundary expectations.
- `backend/models.py`: widened `ck_user_subscription_tier` to include `'elite'`.
- `backend/alembic/versions/20260618_1325_3344e655631f_add_elite_to_user_tier_check.py`: new migration adding the elite check constraint on Postgres.
- Owner accounts migrated to `subscription_tier='elite'`, `subscription_status='active'`.
- `backend/requirements.txt`: `aiohttp==3.14.0 → 3.14.1` (CVE-2026-54273–54280).
- Docs updated: `docs/Stats.md §15` and `docs/PROGRESS.md` ratings bumped.

**Ratings impact:** Frontend 9.0→**9.1** (Backtest honesty + QA a11y/mobile hardening), Product Completeness 9.4→**9.5** (elite tier end-to-end, dead source module removed, form/overlay polish), Security Posture 8.2→**8.3** (prompt CVE patch). IS Backtest Accuracy, OOS / Forward Validation, Live Alpha Quality, and headline overall unchanged — the entry-score relaxation is forward-validated but not yet live-and-proven; per v8.0.1 discipline it earns a forward gate, not a score move. Overall headline unchanged at 8.9/8.3.

**Tests:** `npm run build` green; backend non-E2E **2615 passed, 33 skipped**; `pip-audit` clean; `npm audit --audit-level=high --omit=dev` clean.

### v8.8.5 (2026-06-12) — Dashboard UI Scaling & Mobile Panel Navigation

**Why this matters:** the dashboard was either too zoomed-in on desktop or clipped on the right, and the mobile layout hid the detail/delivery panels with no way to navigate to them.

**Changes:**
- `styles.css`: removed the desktop `zoom:0.8` + `width:125vw; height:125vh` rule that caused right-edge cutoff.
- `styles-desktop.css`: new file with 0.8× density overrides gated to `@media (min-width: 769px)`; loaded after the base stylesheet.
- Mobile breakpoint: `.main` becomes a horizontal scroll-snap flex container; each `.pane` is `flex: 0 0 100%`.
- `app.jsx`: added `mainRef`, `panelIdx`, `panelCount`, `scrollToPanel`, scroll-sync dots, and left/right pager buttons.
- `app.ui.jsx`: added missing `bar-chart`, `eye`, and `globe` icons for the mobile bottom nav.
- Mobile responsive fixes: pane headers wrap, detail rows wrap, detail tabs wrap, chart header wraps, similar-grid/MC stats stack to 1 column, and pane children are capped at `max-width:100%`.
- Topbar: dashboard logo capped at `28px`; Kill Switch and Sign-out labels hidden on phones.
- Full-detail UX: on phones, tapping **Full detail** scrolls the carousel to the detail panel.
- Logo PNGs resized to pass the 500 KB pre-commit file-size limit.

**Ratings impact:** Frontend 8.8→**9.0**, Product Completeness 9.3→**9.4**. Accessibility (147 contrast items) and E2E golden-path tests remain open.

**Tests:** `npm run build` green; backend non-E2E **2550 passed, 18 skipped**.

### v8.8.6 (2026-06-12) — Sentry Bug Fixes: SendLog Filter + yfinance Delisted-Quote Noise

- **SendLog `user_id` missing (PYTHON-FASTAPI-1Y, 25 hits):** `routers/delivery_router.py` filtered `/api/delivery/log` by `SendLog.user_id`, but the column did not exist. Added `user_id` to `models.SendLog`, created Alembic migration `17c3c714fe68`, and populated the column from both the fanout scanner path and the manual send endpoint.
- **yfinance delisted-ticker errors (PYTHON-FASTAPI-5/6, 176+ hits):** `services/market_data.py` now caps `yfinance` loggers at `WARNING`, preventing "possibly delisted" error logs from being captured by Sentry. Missing-ticker quotes are still returned as empty results.

> **v8.0 — Quant Engine (QENG) Roadmap Implementation (16/17 QENG features complete):** experiment registry, PBO report, checklist promotions, PIT feature store, replay engine, version lineage, live fill ledger, TCA service, capacity limits, portfolio allocator, HRP, cost-aware turnover control, stat-arb residual sleeve, TS momentum trend sleeve, cross-sectional factors, cross-sleeve capital allocator, triple-barrier meta-labeling, shadow-control cohort routing, and policy versioning. Overall 8.6/10 product · 8.3/10 quality (v8.0.1, revised down after a server-log audit found the PIT feature store crashing every live scan on NaN→json and the TSYS-5a health scorecard recording 0 calls due to a constraint/race — both green in the test suite; see Stats.md §15 v8.0.1).

### v8.8 (2026-06-12) — §117 Sector-Specific XGBoost Promotion Gate

**Why this matters:** v8.1 shipped a "dynamic unblock" based on the existence of `backtest_ml_model_{SECTOR}.json`. A sector model training run reopened blocked XLI three days after it was blocked, leaking ~32% of the live book at negative edge. §117 removes that entire class of bug.

**Policy changes:**
- `services/sector_ml_promotion.py` is the single source of truth for which blocked sectors are currently promoted.
- Promotion requires an approved, active `ModelRegistry` row linked to a live `ResearchExperiment` row with `decision='promoted'` and `promotion_status='live'`.
- `delivery_gates.py` consults `get_promoted_sectors_cached()`; blocked sectors fail closed if the lookup errors.
- `services/engines/assembler.py` applies a runtime `promoted_sectors` override to clear `buy_thresh` for promoted sectors.
- `scanner.py` refreshes the promoted set once per scan and caches it.

**Training bar:**
- Minimum sector backtest trades raised from 20 to 100.
- Sector models use purged expanding-window CV (3 folds) in addition to a 70/30 holdout.
- `scripts/train_backtest_ml.py` stages a pending `ModelRegistry` + `ResearchExperiment` row after training; it does NOT activate the model.

**Promotion CLI (`scripts/promote_sector_model.py`):**
- Requires `--model-id`, `--sector`, `--oos-auc`, `--cost-adjusted-sharpe`, `--rollback-plan`, `--expiration-days`.
- Enforces OOS AUC ≥ 0.55, cost-adjusted Sharpe > 0, expiration ≥ 1 day.
- Writes an `ActionAuditLog` entry and refreshes the in-memory promotion cache.

**Tests:** `tests/test_delivery_gates.py` (promoted/unblocked, expired re-block, lookup fail-closed) + `tests/test_train_sector_model.py` (insufficient data, beats champion, registry record, promotion checklist, rejection). All passing. Also fixed an f-string format bug in `train_sector_model()`'s champion-beats print statement.

**Status:** Infrastructure complete and gated. No sector model trained or promoted yet; ratings unchanged until live proof.

### v8.8.1 (2026-06-12) — Owner Kill-Switch UI + CSP Hardening

- Added an owner-only **KILL SWITCH** button to the React app top bar (`app.jsx`).
  - Polls `GET /api/admin/execution-kill-switch` and toggles via `POST /api/admin/execution-kill-switch`.
  - Button switches to **RESUME AUTO-EXEC** when paused.
- Rebuilt production bundles (`node build.mjs`): `dist/app-bundle.js` (1238 KB), `dist/site-bundle.js`, `dist/mobile-bundle.js`.
- Exposed localhost via Cloudflare quick tunnel: `https://shaped-survivor-negotiation-highlights.trycloudflare.com`.
- Verified the kill switch over the public URL: button toggles and API returns `{"execution_paused": true/false}`.
- Fixed a CSP `script-src` violation on the landing page by moving the bundle-fallback inline script into a new external file, `fallback-check.js`.
- Added public `GET /api/health/uptime` endpoint for external uptime monitors (e.g. Sentry Uptime). Returns 200 only when the DB is reachable and reports the configured `APP_URL`.
- Updated `launchd` backend service to use `.venv311/bin/python`; added `com.signal.trade.keepawake` LaunchAgent to prevent idle sleep.
- Added `scripts/setup_cloudflare_tunnel.sh` to create a named Cloudflare Tunnel with a fixed domain and a user LaunchAgent. Named tunnel `signal-trade` created for `signaltrade.org` and `app.signaltrade.org`; DNS activation pending (newly registered zone).

### v8.8.2 (2026-06-12) — Operational Hardening (Backups, Logs, Watchdog, a11y)

- DB backups: `scripts/backup_db.sh` now uses `sqlite3 .backup` for online-consistent snapshots; `com.signal.trade.backup` LaunchAgent runs daily at 04:00, keeps 7 days.
- Log rotation: `scripts/rotate_logs.sh` + `com.signal.trade.rotate-logs` LaunchAgent runs daily at 03:30, keeps 14 days of compressed logs.
- Watchdog: `scripts/watchdog.sh` polls `/api/health/uptime` and critical LaunchAgents every 5 minutes; alerts via macOS notification and `backend/logs/watchdog.log`.
- Disabled dead `^BDI` fetch in `services/supply_chain.py` (yfinance 404s).
- Accessibility audit with axe-core on landing, login, and app pages. Fixed missing labels on settings/refresh icon buttons, one nested-interactive search wrapper, and added a visually-hidden `<h1>`.
- Added kill-switch endpoint tests in `tests/test_routers_admin_unit.py`.
- Dependency audit with `pip-audit` in `.venv311`: no known vulnerabilities.

### v8.8.3 (2026-06-12) — Redis Local + Test Robustness + DNS Verification

- Started local Redis (`redis:7-alpine`) via Docker on `localhost:6379` and set `REDIS_URL=redis://localhost:6379/0` in `backend/.env`.
- Added `backend/scripts/start_redis.sh` (creates container with `--restart unless-stopped` if missing, otherwise starts it) and `com.signal.trade.redis` user LaunchAgent that runs it at login.
- Verified backend connects on startup: `[cache] Redis connected: redis://localhost:6379/0…`
- Reloaded `com.signal.trade` LaunchAgent; public uptime endpoint reports `url: http://localhost:8000`.
- Fixed test isolation issues exposed by enabling Redis:
  - `tests/test_small_services_coverage.py`: added autouse fixture to reset module-level Redis client/init flag and blank `REDIS_URL`.
  - `tests/test_worker_bus.py`: added autouse fixture forcing the asyncio.Queue backend regardless of env.
  - `tests/test_config.py`: corrected duplicate `APP_URL` in `backend/.env` (left only `http://localhost:8000`) so the JWT dev-fallback test passes.
- Full backend non-E2E suite: **2547 passed, 18 skipped**.
- `shap` already installed in `.venv311` (0.49.1); live audit remains pending ≥200 post-§82 (≥2026-05-29) resolved signals.
- **DNS / public HTTPS** — Cloudflare authoritative NS and `1.1.1.1` now resolve `signaltrade.org` and `app.signaltrade.org`. The tunnel connector is healthy. `APP_URL` updated to `https://signaltrade.org`, backend reloaded, and `curl --resolve` confirms `GET /api/health/uptime` returns 200 from the public URL. Some local resolvers (e.g., Tailscale `100.64.0.2`) still cache NXDOMAIN; full propagation will finish shortly.
- **QENG-3d execution-policy simulator** — added `services/execution_policy_simulator.py`, `scripts/run_execution_policy_simulation.py`, and `tests/test_execution_policy_simulator.py`. Evaluates market / limit / midpoint / next-open / next-close / delayed-1d on cost-adjusted expected value from a trades CSV and can register a `ResearchExperiment` row.
- **ACT-9 / SP1-4 CI/CD** — pushed v8.8.4 to GitHub `main`. CI run passed: ruff, pytest, 25% coverage floor, gitleaks, pip-audit, npm audit. Added `npm install && npm run build` to `.github/workflows/ci.yml` so `dist/app-bundle.js` exists for `test_static_js_file`.

### v8.5 (2026-06-11) — External Research Agenda §96–§103 Complete + Infrastructure Hardening

**§96 Overnight/Intraday Decomposition + Close-Entry Variant:**
- §96a: `backtest_technicals.py` tracks `overnight_pct`/`intraday_pct` per held day. **Result: 61% of alpha from overnight gaps** on full canon (217 trades).
- §96b: `--entry-at-close` A/B tested. ΔSharpe = 0.00 — neutral, safe for live use.
- §96c: `scanner.py` Step 5c: 15:45–15:55 ET scan slot tags BUYs with `entry_style=close`.
- §96d: Overnight telemetry fields persisted in trade dict.

**§97 Limit-Order Entry Frontier:**
- §97a: `--entry-limit k` tested k ∈ {0.25, 0.5, 1.0}. All variants fail deploy bar (Sharpe 0.16–0.12 vs canon 0.25). §97c blocked indefinitely.
- §97b: Cross-read wiring with §96a report sections co-located.

**§99 SPRT Forward-Validation Protocol:**
- §99a: 4 hypotheses pre-registered in `ResearchExperiment` (IDs 3–6) at 2026-06-11 00:44 UTC.
- §99b: `scripts/sprt_monitor.py` with Gaussian LLR, Wald boundaries, state persistence. 12 unit tests passed.
- §99c: Shadow promotion + OOS v7 + OOS v8 all pre-registered.
- §99d: SPRT state surfaced in `/api/admin/system-readiness`.

**§100 SimFin Fundamentals Integration:**
- `simfin_bulk_download.py` + `build_simfin_factors.py` created.
- 5 factors: earnings yield, gross profitability, accruals, asset growth, net buyback yield.
- Wired into `cross_sectional_alpha_model.py` with `--simfin` flag.

**§101 TSMOM Diversifying Sleeve:**
- `backtest_tsmom_sleeve.py`: 12-1 month sign-of-return, 8 liquid ETFs, monthly rebalance, vol-scaled 10%.
- Result: Long-flat Sharpe **0.57**, 4/4 epochs positive (2015-22 fold 0.277, just below 0.30 bar).
- Corr vs MR book: +0.27. Deploy bar not cleared; retained as research artifact.

**§103 Automated Decay Monitor:**
- §103a: `scripts/decay_monitor.py` — trailing-50 Wilson CI on clean delivered BUYs.
- §103b: Alarm wiring — `"decay"`, `"confirmation"`, or `None`.
- §103c: VIX regime context added. Calm-market decay re-labeled `"drought"` (N starvation, not true decay).

**Infrastructure & Bug Fixes:**
- §85-2 MD&A bug fix: `_fetch_filing_text()` now consumes `primaryDocument` from SEC submissions JSON (deprecated `-index.json` endpoint returned 404). All 21 edgar unit tests pass.
- Fill-rate bug fix: `_limit_signals_attempted` counter threaded through `simulate_ticker()` → `.attrs` → report. True fill rate now correct (e.g., 41.9% for k=0.5).
- VAPID keys generated via `py_vapid`, added to `.env`, `config.py` reads correctly.
- E2E tests: Playwright installed. 5 passed (health, landing, auth×3), 7 skipped (need owner creds).
- §69–§74 gate unit tests: `tests/test_gates_5982.py` created, all passing.
- §95 DD-throttle: Already live in `portfolio_allocator.py`; verified operational.

**Tests:** 596+ passed (including 55 delivery + 12 SPRT + 21 edgar + 4 options gates + gate unit tests). 2 warnings.

### Alt-Data Cross-Sectional Integration (§104–§110, 2026-06-11) — REVIEW COMPLETE

**Backfill:** FINRA daily short-sale volume (14M rows, 2019–2024), SEC fails-to-deliver (91k rows, 2017–2024), NAAIM exposure index (1,039 weekly rows, 2006–2026), Wikipedia pageviews (66k rows, 20 tickers, 2015–2024), plus FRED UMCSENT. All panels migrated from pickle to **Parquet** and cached under `backend/data/cache_*`.

**Per-trade tilt verdict:** §104b FINRA SV tilt and §105b SEC FTD tilt **FAILED/INCONCLUSIVE** as sizing boosts on the 217-trade legacy book — rare-extreme conditions produce N≈5–8 cohorts that are unfalsifiable in-sample. §106b NAAIM <30 tilt also failed. These panels are **retained for cross-sectional reuse**, not per-trade tilts.

**Cross-sectional integration — defects fixed and re-tested:**
* **Defect 1 (market-wide z-score death):** UMCSENT, NAAIM, and AAII now pass through RAW instead of being z-scored to zero.
* **Defect 2 (same-day lookahead):** FINRA SV and Wikipedia panels are shifted +1 day before `merge_asof`.
* **Strict merge-failure guard:** `build_panel()` raises `RuntimeError` if `--finra-sv`, `--sec-ftd`, `--naaim`, or `--wiki` is requested but the merge fails.
* **Reproducibility:** Panel loaders read `.parquet` and fall back to legacy `.pkl` once, then rewrite to Parquet (eliminates the numpy 1.26 vs 2.4.6 silent-unpickle failure).

**Corrected walk-forward (h=21, 10bps one-way):**
| Config | Net Sharpe | Positive folds | Mean IC |
|--------|------------|----------------|---------|
| baseline (price only) | 0.195 | 9/15 | +0.0016 |
| `--finra-sv` | 0.287 | 9/15 | +0.0032 |
| `--wiki` | 0.215 | 8/15 | +0.0033 |
| `--naaim` | 0.163 | 8/15 | +0.0085 |

**Corrected walk-forward (h=63, 10bps one-way):**
| Config | Net Sharpe | Positive folds | Mean IC |
|--------|------------|----------------|---------|
| baseline (price only) | 0.616 | 10/14 | +0.0207 |
| `--wiki` | 0.694 | 11/14 | +0.0199 |
| `--finra-sv` | 0.454 | 10/14 | +0.0205 |
| `--naaim` | 0.328 | 10/14 | +0.0176 |

**Placebo distribution (10 pure-noise seeds):**
| Horizon | Mean net Sharpe | 5%-95% band |
|---------|-----------------|-------------|
| h=21 | 0.309 | [0.286, 0.332] |
| h=63 | 0.708 | [0.688, 0.724] |

At h=21, `--finra-sv` lands inside the placebo band; `--wiki` and `--naaim` land below it. At h=63, `--wiki` lands inside the placebo band; `--finra-sv` and `--naaim` land below it.

**Paired per-fold/rebalance bootstrap (real vs baseline):** no ΔSharpe 90% CI excludes zero.

**Coverage-epoch attribution:** The h=21 alt-data Sharpe is concentrated in the 2019-2024 epoch and reverses sharply post-2024 (when coverage ends). The h=63 pre-2019 epoch is also positive, but the bootstrap still does not separate it from sampling noise.

**Horizon-as-hyperparameter:** Selecting horizon on 2012-2019 folds picks **h=63**; its out-of-sample net Sharpe on 2020-2026 folds is **+0.494** (not the full-sample +0.616).

**EDGAR fundamental factors (SimFin proxy):** SimFin bulk data requires a free `SIMFIN_API_KEY` (not on disk yet), so the same canonical monthly-horizon alpha family was tested with the existing EDGAR panel (`--fundamentals`, `--universe curated`). Result: net Sharpe **0.138 at h=21** and **0.358 at h=63**, both inside/below the placebo band and not significantly different from the curated baseline (ΔSharpe CI includes 0). Raw results: `backend/data/alt_data_fundamentals.json`.

**§96b close vs next-open entry A/B:** Pre-registered binary test on the 217-trade IS book. Close-entry: WR 66.4%, avg ret +0.92%, Sharpe 0.25, MaxDD −1.79%. Next-open canon: WR 69.1%, avg ret +0.80%, Sharpe 0.24, MaxDD −2.31%. **ΔSharpe ≈ +0.01** — close-entry is not a material edge improvement; it is at best an execution convenience. Logs: `backend/data/backtest_default.log`, `backend/data/backtest_close.log`.

**Honest status:** No alt-data config has demonstrated a reproducible, properly-lagged, selection-adjusted effect above the harness noise floor. The h=63 net 0.769 claim is **withdrawn**. Details and full tables: `docs/LEARNINGS.md §104–§110`. Analysis script: `backend/scripts/analyze_cross_sectional_alt_data.py`; raw results: `backend/data/alt_data_attribution.json` and `backend/data/alt_data_fundamentals.json`.

### v8.7 (2026-06-12) — Free Alt-Data Paths Wired + Ablated + TCA Slippage Feedback Loop

**§112–§116 cross-sectional free alt-data expansion:**
- CBOE options snapshots self-accumulate into per-ticker IV history (`services/options_cboe.py` → `data/cache_options/options_iv_history.parquet`), enabling `iv_rank` without paid historical options data.
- FINRA ATS weekly dark-pool participation merged with a 2-week PIT lag (`--finra-ats` in `cross_sectional_alpha_model.py`).
- SEC FTD velocity feature `ftd_pctile_chg_1m` added; panel backfilled to 2004 (`build_ftd_panel`).
- NAAIM/UMCSENT rolling percentiles (`naaim_exposure_pctile`, `umcsent_pctile`) and Wikipedia cross-sectional attention (`views_z_xs`) wired as market-wide/cross-sectional features.

**Walk-forward/placebo ablations (h=21, 15 expanding folds, curated 109-name universe, 10bps one-way, placebo seed=42):**

| Config | Net Sharpe | Mean IC | Coverage | Verdict |
|---|---:|---:|---:|---|
| Baseline (price + placebo) | **0.395** | +0.0203 | — | — |
| +SEC FTD velocity | 0.353 | +0.0209 | 45% | inside noise |
| +NAAIM/UMCSENT pctile | −0.040 | +0.0151 | 100%/89% | inside noise / worse |
| +Wikipedia `views_z_xs` | 0.410 | +0.0211 | 4% | inside noise |
| +All three combined | 0.029 | +0.0192 | mixed | inside noise / worse |
| +FINRA ATS | not testable | — | 0% | historical endpoint blocked |
| +CBOE IV-rank | not testable | — | <1d | live-forward only |

**Result:** no free alt-data config produced a net-of-cost Sharpe uplift distinguishable from the harness noise floor. The v8.6 alt-data retraction is reinforced. FINRA ATS historical backfill is blocked by the endpoint (returns HTML); CBOE IV-rank requires ~12 months of self-grown history before validation. Raw logs: `backend/data/alt_ablations/*.log`; machine-readable summary: `backend/data/alt_ablations_summary.json`.

**§118 live TCA feedback loop wired:** `tca_service.py` expected/realized slippage feeds `portfolio_allocator.py` sizing against a configurable 20 bps threshold. Live verification pending (RISK-3, ≥50 fills).

**Tests:** `test_portfolio_allocator_optimizations` made deterministic via monkeypatched market data/slippage.

**Ratings:** 8.9/10 product · 8.3/10 B+ quality (headline unchanged; Data Pipeline 8.4→8.5, Execution & Friction 7.8→7.9, Test Coverage 7.9→8.0 — all infrastructure-only).

## 📊 Live database stats (2026-06-10)

| Metric | Value |
|--------|-------|
| Watchlist tickers | 191 |
| Total signals generated | 7,015+ |
| Signals sent to Telegram | 543 |
| Resolved signals (outcome_pct filled) | 566 |
| Effective ticker-days (deduplicated) | 459 |
| 7d win rate (mark-to-market) | 58.8% |
| 7d win rate (stop-enforced) | 42.2% |
| 14d win rate | 65.1% |
| Win rate (friction-adjusted, best horizon) | 43.6% |
| Brier score | 0.2531 (best horizon) |
| Confidence gap | +11.0pp overconfident (raw) |
| XGBoost training samples | 566 |

> **§93d gap decomposition (2026-06-10):** Live WR 43.6% vs IS 69.1% = **25.5pp gap**. Primary driver: **regime mismatch** — live period (2022+) overlaps backtest epoch with negative Sharpe (−0.10). Secondary: midday microstructure (hour 11–12 ET WR 23.7% vs 47.8% baseline, p=0.000). Delivery latency mean ~2h (80% >5min SLA). No fill data (paper account not trading).

## 🏅 Quality Ratings — v8.2 (2026-06-09)

> Ratings maintained in **[`docs/Stats.md §15`](Stats.md)** — single source of truth.
> **Overall: 8.9/10 product audit · 8.7/10 B+ quality grade** (v8.2, 2026-06-09 — +0.1 from v8.1 driven by v10.8 Sharpe improvement sweep: score-band sizing +0.05, MR-count=2 +0.01, dynamic RSI stops all shipped live; IS Sharpe 0.23→0.25; shadow/research excluded; see Stats.md §15 + §83).
> v8.0: Quant Engine (QENG) Roadmap Implementation (16/17 items): (1) Research experiment registry, PBO report, checklist; (2) PIT feature store, event replay, lineage; (3) fill ledger, TCA service, capacity limits; (4) portfolio allocator, HRP baseline, turnover control; (5) residual stat-arb, TS momentum, weekly factor sleeves, cross-sleeve allocator; (6) triple-barrier meta-labeling, cohort routing, policy versions. 1871 tests.
> v7.8: TSYS-1→13 targeted-system hardening (auth lockout/session, Stripe reconciliation, provider scorecard/corporate action validation, gate trace/explainability, model registry, outcome audit, risk limits/key rotation, Prometheus metrics, index audit/purges, audit log/risk-ack gate). 1862 tests.
> v7.7: IBKR integration, §75 buyback window EDGAR parser, HTTP latency cached TLS / pooled sessions pass. 1646 tests.
> v7.6: BE-1 partial (signal_engine.py 7421→5848, `services/engines/`), ACT-4 EOD-batch delivery fix, DPC-1 notification prefs, ACT-1 XLI block, ACT-2 sector audit. 1636 tests.
> v7.5: 32/38 free path-to-10/10 items done. BT-2/4, RD-3/4, CAL-2/3, ML-5, PROD-3/4, SEC-2/3/4/6, FE-1/3/4, DEPLOY-4/5/6, OOS v9 (10 tickers). 1115 tests.
> v7.4: RISK-1/2/4 (bracket stops + DD circuit-breaker + kill switch), A16-UI, PROD-1/3, ML-4, CAL-4, BE-2. 1096 tests.

---

## ✅ Implemented

### v8.3 (2026-06-10) — Sharpe×N Agenda §87–§94 Complete + Gap Decomposition v2

**§87 L10 Consec-Score Sizing (`backtest_technicals.py` + `scanner.py`):**
Prev-day score ≥ BUY_THRESH → 1.3× position size; otherwise 1.0×. Preserves all trades (ΔN = 0).
- **Unweighted per-trade:** Sharpe 0.24 → 0.24 (identical by construction — sizing does not affect entry/exit).
- **Size-weighted:** Sharpe 0.24 → 0.30 (+0.06), WR 69.1% → 70.7% (+1.6pp), 50/217 trades boosted.
- **Portfolio simulation (5 slots, T-bill on idle):** CAGR +3.6% → +3.7% (+0.1pp), Ann.Sharpe 2.87 → 3.03 (+0.16, +5.6%), MaxDD −6.16% → −6.33% (−0.17pp). MC P5 = 0.07 > 0.
- **Verdict: DEPLOY.** Live engine: `_apply_l10_conviction_sizing()` in `scanner.py` Step 5b, with global L1–L10 clamp [0.10, 3.00]. Committed `ede79b2`.

**§88 Calm-Regime Sleeve — ABANDONED:**
Full 23-year backtest with `--calm-sleeve`: **0 trades generated.** ALL 217 baseline trades occurred in VIX 20–30 (stress). Zero in calm (<20) or panic (≥30). MR triggers (RSI<42, BB%B<0.22, IBS<0.15, VWAP%<−0.75) naturally only fire in fear-driven capitulation. **Structural mismatch, not a gate problem.** Code retained but deprioritized.

**§89 Fama-French ST_Rev + Factor Attribution:**
- `fetch_ff_str()` from Ken French Data Library, cached to disk. Wired as 15th meta-label feature (`ff_str`). `signal_ml.py` `_META_FEATURE_NAMES` updated to 15 features.
- §89a regime sizing: rolling 63d ST_Rev Sharpe; negative regime → 0.5× size. Result: +0.008 Sharpe (negligible). ST_Rev is NOT a useful regime predictor for this idiosyncratic strategy.
- §89b factor attribution: OLS on FF5 + ST_Rev. **Alpha = +0.87%/day (p=0.044, annualized +218%)**. HML significant positive (p=0.009), CMA significant negative (p=0.005). ST_Rev NOT significant (p=0.530). R² = 0.05 — 95% idiosyncratic.

**§90 WATCH Bench — ALL REJECTED:**
Full 22-year IS backtest on PANW, BWA, FTI, EQH, TRGP, APTV, DHI, FIVE, ITW: **0 trades across all 9 tickers.** PIT analysis: EQH/FIVE never in S&P 500; others have ample history but produce zero MR signals. The 111-name curated list is already well-filtered.

**§91 SI Rising Sizing Tilt:**
`simulate_ticker()` accepts `si_rising_map`; applies 1.15× when `si_rising=True`. Live read (N=335): rising SI avg +1.01% vs falling SI −1.41% = **+2.42pp spread**. Backtest: only 3/217 trades had SI data (pre-2017). Deploy gate: live N≥50 with rising SI.

**§92 Cross-Sectional Shadow Criteria — LOCKED:**
`SHADOW_PROMOTION_CRITERIA` immutable in `cross_sectional_shadow.py`: min 150 resolved, bottom-decile WR ≥3pp worse, monotonic top>bottom, 0.75× haircut. Wired into `signal_engine.py`. Criteria now immutable — changing them after viewing live data invalidates the forward test.

**§93 Live-vs-IS Gap Closure:**
- (a) `assembler.py:1011` — `_sector_etf_ml` falls back to `SECTOR_MAP.get(ticker.upper())` when `sector_rs` is None. Fixes 81% under-application of sector-specific entry models.
- (b) Server restarted (PID 14175). DATA-1/DATA-2 fixes active.
- (c) Net-of-friction calibration backfill: 566 samples, gross 43.6% → net 40.5%.
- (d) **Gap decomposition v2:** `live_gap_decomposition.py` — 566 resolved signals, 25.5pp WR gap (43.6% live vs 69.1% IS). Primary driver: **regime mismatch** (live period = 2022+ rate-hike epoch, backtest Sharpe −0.10). Hour 11–12 ET catastrophic: WR 23.7% vs 47.8% baseline (p=0.000). Effect is April-driven; May+ cohort too small to confirm. Scanner midday warning log added (tracking only, no hard filter).

**§94 Per-Sector Hold-Days Parity:**
`_SECTOR_MR_CONFIG` hold-days wired into `simulate_ticker()`: XLK/XLE/XLB/XLRE/XLU = 5d, XLF/XLV/XLI = 7d, others = 10d. Backtest: +0.04 Sharpe. Canon now matches live `recommendedHoldDays`.

**Meta-model retrain:**
Fresh train on 217 trades with all 15 features. CV-AUC **0.4224 ± 0.0977** — still below `_MIN_META_AUC=0.52` gate. Top features: `vix_term_ratio`, `dow`, `hmm_trans_risk`. Constraint is N (sample size), not features. Auto-activates when CV-AUC crosses 0.52.

**Full 23-year backtest canon (v10.8 + all features):** 217 trades, 69.1% WR, +0.80% avg, 0.24 Sharpe, −2.31% MaxDD. **100% of trades in VIX 20–30.** Strategy is structurally a **stress-regime contrarian play** — MR triggers don't fire in calm or panic.

**Tests:** 801 passed (ex-e2e), 1 failed (e2e Playwright fixture missing).

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

### v5.6 (2026-05-17) — Signal Lifecycle, Live UI, Send Quality & Test Suite Green
*(condensed from the retired root `updates.md`)*

- **Signal lifecycle:** `stop_monitor.py` checks live prices every 30 min, fires Telegram notifications, updates `hit_stop`/`hit_target`/`exit_type`, deactivates signals (previously stayed "active" 7 days regardless).
- **Automated nightly resolution:** `_nightly_outcome_resolution()` runs 2am ET via lifespan task (was a manual script).
- **Send quality:** 3 new `_maybe_send()` gates — pre-earnings blackout (2d), sector concentration (max 2 BUY/sector/24h), ticker-adaptive confidence floor.
- **Calibration:** isotonic regression added alongside Platt.
- **Bug:** `_is_lev_etf` made an explicit `_assemble_signal()` parameter (closure-scope failure when tests called it directly). 597 tests passing. Commits `904bc22`, `6e8b25d`, `341414b`.

### v5.5 (2026-05-16) — Validation-Driven Fixes, Quant Features & Leveraged ETF Tracker
*(condensed from the retired root `updates.md`; driven by a `validate_predictions.py` run on 529 resolved signals 2026-04-28→05-14: 7d WR 57.7%, 14d WR 63.2%, Brier 0.2899, +16pp overconfident, intraday WR 30.4% vs position WR 61.4%)*

- **Calibration/confidence:** hard ceiling 84%→72% at all 6 cap sites (75–84% bands won only 48–50%); `_MAX_BLEND` 0.80→0.90; `_N_FULL` 30→20; calibration reads `outcome_14d` first.
- **Defensive-ticker BUY gate:** 16 tickers with validated 0% BUY WR (BAC, KO, PEP, T, NEE, PG, USB, PNC, C, TGT, AIG, WM, MCO, TT, DE, TJX) gate BUY → HOLD.
- **Quant features (free-data):** FRED HY/IG OAS credit spreads in `macro.py`; analyst revision momentum (`revision_pts`, capped ±8) + scoring block; cross-sectional universe ranking at `scan_all()` tail (±3pp decile adjustments); `beta` exposed in signal dict; `GET /api/signals/alpha-decay` per-source/per-horizon endpoint.
- **Leveraged ETF tracker:** `_LEVERAGED_ETFS` frozenset (52 tickers, 3×/2× bull+bear), fundamentals bypass, position-style forced to swing (volatility decay), risk-disclosure rationale card, watchlist seed → ~210 tickers, sector mappings to underlying ETFs. Commit `114ecc4`.

> **Earlier v5.x history (v5.0–v5.4, v5.7–v5.12, 2026-05-09–18) archived** — see git log for full change details.

---

## 👁️ Known Blind Spots

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | **Phantom wins** — 88 historical trades show WR 58.8% vs stop-enforced 42.2% | Critical | ✅ Fix deployed 2026-05-17. New signals resolve correctly. Historical backfill pending. |
| 2 | **Confidence gap +11pp** — model systematically overconfident | High | ✅ Calibration tightened (blend 0.97, N_FULL 15). Monitoring next training run. |
| 3 | **Sector model gaps** — XLF/XLP/XLU blocked (PF < 0.40x) | High | 🔄 Blocked until sector-specific sub-models retrained |
| 4 | **Intraday recalibration** — 34.8% WR, PF 0.73x | Medium | 🔄 Restored at ≥68% conf floor; quality improvement in progress |
| 5 | **Hardcoded owner password** | Critical | ✅ Fixed 2026-06-09 — `.env` has 32-char secure password; startup fails on `ChangeMe123!` in production. |
| 6 | **Monolithic `run_scan`** | Medium | 🔄 Delivery gates extracted; full scanner decomposition pending |
| 7 | **Chart drawing tools** | High | ❌ Not yet implemented |
| 8 | **Autonomous execution** | Critical | 🔄 Alpaca + IBKR integration implemented; auto-execute gated on live WR > 55% and LIVE-1→LIVE-8 checklist |

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
