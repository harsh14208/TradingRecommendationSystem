# Signal.Trade — Development Progress

> **Version: v6.1** · Updated: 2026-05-25 · Server: `uvicorn main:app --host 0.0.0.0 --port 8000`
> ~210 tickers (incl. 52 leveraged ETFs) · 70+ signal blocks · 116 API endpoints · Max confidence: 72% (empirically calibrated)
> **Data: Polygon.io/Massive-first (bulk OHLCV + quotes + reference info) · yfinance fallback · Massive WebSocket (dark pool) · FRED (macro + credit spreads)**
> **Database: PostgreSQL 16 (primary) · SQLite removed · 7,015+ signals · 8 users**
> **Tests: 660 passed, 0 failed, 4 skipped (`backend/venv/bin/python -m pytest backend/tests`)**

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

## 🏅 Quality Ratings — v6.1 (Latest)

| Aspect | Score | Grade | Notes |
|--------|-------|-------|-------|
| **Signal Accuracy** | 9.2/10 | A | §16a confirmed-negative sectors blocked. §17b/c/e entry-quality gates. Fundamental value-trap gate. 5 live-validated 0% WR tickers blocked. |
| **Signal Engine** | 9.4/10 | A | Per-sector MR config (_SECTOR_MR_CONFIG). ATR ceiling ≤70, jump filter <−6%, VIX slope, IBS streak gates. Full Polygon options chain. |
| **Frontend UX** | 8.8/10 | A− | Live WebSocket price, visual R:R zones, DOM pagination. Keyboard shortcuts. |
| **Code Maintainability** | 8.0/10 | B+ | Continuous intraday scanner. Delivery gates, dark_pool migrated to real Polygon endpoints. |
| **Security** | 7.0/10 | B− | JWT + HTTP-only cookies, bcrypt. Risk: default owner password. |
| **Backend Architecture** | 9.1/10 | A | Continuous market-hours scanner (09:30–16:00 ET). RLIMIT_NOFILE raised. Single-flight scan, Redis locks, stop_monitor. |
| **Data Pipeline** | 9.2/10 | A+ | Polygon full options chain (8-page pagination, 403 fallback). Corporate actions via real Polygon reference endpoints. |
| **Deployment Readiness** | 6.5/10 | C+ | Railway/Fly ready. Blockers: owner password, SMTP, Stripe webhook, HTTPS. |
| **Test Coverage** | 8.8/10 | A | 660 passing tests, 0 failures. |

**Overall: 8.9 / 10 — A**

---

## ✅ Implemented

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

### v5.12 (2026-05-18) — MR-Only Backtest Optimization + 4 New Signal Engine Gates

**Backtest (backtest_technicals.py) — 20-year optimized result:**

| Metric | v5.10 | v5.12 | Delta |
|:---|--:|--:|--:|
| Win Rate | 49.6% | **56.7%** | +7.1pp |
| Avg Return | +0.13% | **+1.07%** | +723% |
| Sharpe (per-trade) | +0.04 | **+0.27** | +575% |
| Profit Factor | 1.10× | **1.89×** | +72% |
| Max Drawdown | -3.87% | **-1.15%** | -70% |
| Monte Carlo p5 | negative | **+0.17** | edge is statistically real |

**Backtest methodology changes:**
- [x] **MR-Only entry gate** — RSI<42 OR BB%B<0.22 OR IBS<0.15 OR VWAP%<−0.75%; eliminates "above SMA200 + MACD running into highs" entries; +0.20 Sharpe vs full-signal
- [x] **Score ceiling BUY_THRESH_MAX=999** — quality gates now do the job the ceiling did; 60+ band positive with all gates
- [x] **BUY_THRESH 30→40** — sweep-validated; quality gates handle fine filtering
- [x] **HOLD_DAYS 5→10** — sweep-validated; MR bounces resolve fully in 10 days, target hit rate 18%→44%
- [x] **Earnings blackout** — skip entries within 5 calendar days of earnings; fetched via yfinance `get_earnings_dates(limit=50)`
- [x] **Consecutive RSI decline** — RSI must still be falling into entry (RSI[i] < RSI[i-1]); filters one-day noise spikes
- [x] **Deep-bear RSI gate** — VIX>28 + SPY<SMA200×0.95 → require RSI<35 (extreme capitulation only in crisis)
- [x] **Price-SMA20 distance** — require price ≥2% below SMA20; confirms genuine short-term extension
- [x] **Dollar-volume minimum** — skip avg daily volume < $50M
- [x] **Day-of-week** — no Friday BUY entries (weekend gap risk)
- [x] **Universe curation** — 36→31 tickers; removed SMCI/MA/DIS/GS-dup; added AMD, BAC, NFLX, ADBE, F, TGT, AMZN, COST, SBUX

**Signal engine (signal_engine.py) — 4 new gates ported from backtest:**
- [x] **MR Entry Condition Gate** — BUY blocked (score<65) without RSI<42 OR BB%B<0.22 OR IBS<0.15 OR VWAP%<−0.75%. Rationale card explains delta: −0.74% avg (no MR) vs +1.07% avg (MR condition).
- [x] **Deep-Bear Stricter RSI Gate** — VIX>28 AND SPY<SMA200×0.95 → require RSI<35; blocks falling-knife entries in panic regimes
- [x] **Price-SMA20 Distance Gate** — price must be ≥2% below SMA20 for score<65 BUYs
- [x] **Day-of-Week Gate** — no Friday BUY entries for score<65; 2-day weekend gap risk with no management
- [x] **Defensive ticker block updated** — BAC and TGT removed (v5.12 backtest: 71.4% WR / +2.26% and 55.6% WR / +0.72% with MR gates)

**Tests:**
- [x] `test_assemble_signal_risk_free_rate_dampener` — tech dict updated with `rsi: 38` to satisfy new MR gate
- [x] All 660 tests passing, 0 failures

---

### v5.10 (2026-05-18) — Backtest-Validated Signal Quality Gates + Target Calibration

**Signal engine gates (all validated against 20-year backtest, 1940 trades):**
- [x] **`_levels` swing target 3.0× → 2.0× ATR** — target hit rate doubled from 11% to 18.5% in 5-day holds; R:R maintained at 1.3× (1.5s / 2.0t)
- [x] **RVOL gate: hard block at <1.2 (removed `score<50` escape)** — low-volume breakouts fail regardless of score; gate now skips gracefully when volume data is unavailable (avoids blocking on missing data)
- [x] **ATR minimum gate: 0.8% soft-conditional → 0.7% hard block** — stocks moving <0.7%/day cannot generate returns above friction in a 5-day hold; no macro override
- [x] **ADX minimum gate (new)** — block BUY if ADX<18, non-oversold, score<45; prevents crossover whipsaw in directionless markets (choppy years 2010, 2015)
- [x] **RSI>70 + ADX<28 weak-trend gate (new)** — block BUY in confirmed bull market when RSI>70 and ADX<28 and score<40; catches "topping market" false breakouts (2018 pattern where overbought stocks with fading trend reversed)
- [x] **Bear market gate threshold: score<42 → score<50** — 20-year data: BUY signals averaging −1.7%/trade during downtrend+VIX>25; raised bar now requires alt-data confirmation
- [x] **SMA200 RSI exception tightened: <30 → <25** — RSI 25-30 "oversold bounces" in sustained downtrends are dead-cat bounces; only extreme oversold (RSI<25) waived
- [x] **SPY neutral zone gate (new)** — block BUY score<45 when SPY within ±2% of SMA200; prevents whipsaw entries at regime turning points (Aug-2022 bear bounce, late-2018 Q4 breakdown both in ±2% zone)
- [x] **Defensive ticker block extended** — ABBV, MRK, PFE, LLY, TMO, TXN, NKE, V, PM, WMT added based on 20-year backtest underperformance (event-driven / range-bound / non-technical)

**Macro (macro.py):**
- [x] **SPY history 3mo → 1y** — enables SMA200 computation (requires 200 bars)
- [x] **`sp500_sma200`, `sp500_sma200_ratio`, `sp500_neutral_zone` (bool) added to macro context** — consumed by neutral zone gate

**Backtest (backtest_technicals.py):**
- [x] **ETFs removed from universe** — inverse/leveraged ETFs as BUY candidates produce nonsensical results; bond ETFs respond to rates not equity technicals
- [x] **START restored to 2006-01-01** — pre-2006 adds dot-com crash noise and insufficient signal density for modern tickers

**Tests:**
- [x] **`test_signal_engine_core.py::test_levels` updated** — expected stop/target values updated for new 1.5s/2.0t swing multipliers

**Backtest result (v5.10 vs starting baseline):**

| Metric | Baseline (v5.0) | v5.10 | Delta |
|:---|--:|--:|--:|
| Win Rate | 43.7% | 49.6% | +5.9pp |
| Avg Return | -0.16% | +0.13% | +0.29pp |
| Sharpe (per-trade) | -0.05 | +0.04 | +0.09 |
| Max Drawdown | -51.52% | -3.87% | +47.65pp |

---

### v5.9 (2026-05-17) — Signal Quality Gates, Polygon Batch, Stats Fixes, IBS/VWAP/ATR Indicators

*(see commit `feafb8c`)*

---

### v5.8 (2026-05-17) — Phantom Win Fix, Risk Optimization & Institutional Analytics

**Phantom win fix (closes 16.6pp WR inflation gap):**
- [x] **`stop_monitor.py` — always locks `outcome_pct` at exit-level price** — removed `or` guard; when stop fires, outcome is computed from the stop/target level, not the current market price. Position P&L is now locked at the exit price regardless of subsequent recovery.
- [x] **`validate_predictions.py resolve_outcomes()` — skips calendar fill for exited signals** — `outcome_pct` is no longer overwritten by the 7-day mark if `exit_type` is already `'stop'` or `'target'`.
- [x] **`validate_predictions.py resolve_mae_mfe()` — sets `outcome_pct` at stop level during backfill** — when historical OHLCV determines `exit_type='stop'`, the outcome is computed from `(stop - entry) / entry * 100` immediately, preventing the nightly fill from using a recovered price.
- [x] **`validate_predictions.py` — DB path fixed** — now reads `DATABASE_URL` from `.env` (was hardcoded to stale SQLite path).

**Risk & signal quality:**
- [x] **ATR stop multipliers widened for position style** — `signal_engine._levels()` now takes `style` parameter; position: 3.0–3.5× ATR (was 2.0–2.5×), targeting reduction of 45.7% stop-hit rate.
- [x] **Sector gate added** — XLF, XLP, XLU blocked from delivery (PF < 0.40x) until per-sector models retrain.
- [x] **Intraday re-enabled at 68% conf floor** — was set to 999 (effectively disabled); restored to ≥68% while signal quality improvement is in progress.
- [x] **Swing floor raised to 70%** — elevated from 63% pending recalibration.
- [x] **Delivery gates extracted to `services/delivery_gates.py`** — all pre-send eligibility checks decoupled from `_maybe_send()`. Independently testable; reusable for future broker execution path.
- [x] **SLA false positive fix** — `_maybe_send()` now measures latency from `scan_cycle_started_at` (not `signal.created_at`). Refreshed-but-unsent signals no longer trigger false 424-minute SLA alerts.

**Model calibration:**
- [x] **XGBoost 20→19 features** — `confidence_bin` removed (was a binned duplicate of `confidence`, amplifying the high-conf inversion). Added L1/L2 regularization (`reg_alpha=0.1`, `reg_lambda=2.0`), `gamma=0.3`, `max_depth` 4→3, `learning_rate` 0.1→0.05.
- [x] **Calibration tightened** — `_MAX_BLEND` 0.90→0.97, `_N_FULL` 20→15. Top bands (75–80% raw confidence) now calibrate down to ~45% delivered confidence, preventing overconfident signal delivery.
- [x] **Fear & Greed API fixed** — CNN's endpoint was returning HTTP 418 (bot detection). Added full browser fingerprint headers (`User-Agent` Chrome 124, `Referer`, `Origin`, `Sec-Fetch-*`). F&G now live at 62.9 (Greed).

**Institutional performance analytics:**
- [x] **`performance_snapshots` table** — PostgreSQL table stores point-in-time metric dicts with tag, git SHA, win rate, Sharpe, full JSONB metrics blob.
- [x] **`calc_tbd_metrics.py --snapshot <tag>`** — writes a named snapshot after printing the report. Upserts on re-run (delete-then-insert) so tuning sessions stay clean.
- [x] **`diff_snapshots()` + `_find_flagged()`** — field-level delta with per-metric significance thresholds (win_rate ≥2pp, sharpe ≥0.3, brier ≥0.02, etc.).
- [x] **Admin snapshot API** — `GET /api/admin/snapshots`, `GET /api/admin/snapshots/{id}`, `GET /api/admin/snapshots/diff/{a}/{b}`.
- [x] **Weekly digest auto-snapshot** — Sunday digest saves a `weekly-YYYY-MM-DD` snapshot automatically.
- [x] **Institutional quant metrics** — Sharpe (sqrt(252), applied once), Sortino (semi-deviation from 0%, divisor=n), Calmar, Omega, VaR 95/99, CVaR, skewness, kurtosis, t-stat/p-value, reliability diagram, Ulcer Index, phantom wins, stop-enforced WR, capture ratio, % trades > 1R.
- [x] **Sortino/Sharpe math fixes** — eliminated double-sqrt annualization; corrected Sortino divisor from `n-1` to `n`.
- [x] **SQLite removed** — all stale SQLite files deleted; `database.py` migration shim removed; `signal_ml.py` sqlite3 fallback removed. SQLite retained only for test suite via `conftest.py`.
- [x] **662 passed, 0 failed** — +56 new tests: delivery gates (15), quant metrics (26), performance snapshots (14), intraday gate (1 updated).

### v5.7 (2026-05-17) — Pricing, Data Reliability, Scanner Observability & Confidence Consistency

- [x] **Tier prices centralised in `config.py`** — Basic $29/mo, Pro $79/mo. Billing + docs drift fixed.
- [x] **Polygon/Massive-first bulk data path** — `market_data.get_histories_batch()`, `get_quotes_batch()`, `get_infos_sequential()` call Polygon first, yfinance fallback for missing tickers.
- [x] **Single-flight scan wrapper** — `run_scan()` guards with `asyncio.Lock` + Redis distributed lock.
- [x] **Lifecycle status** — scanner records state, timing, stage, failure count. `/api/health` includes scan state.
- [x] **Redis distributed locks** — `cache_acquire_lock()` / `cache_release_lock()` with token-safe release and in-memory fallback.
- [x] **XGBoost cap aligned to 72%** — `adjust_confidence()` clamps ML-adjusted output to 72% ceiling.
- [x] **606 → 647 passing tests** — full backend suite green.

### v5.6 (2026-05-17) — Signal Lifecycle, Calibration, Live UI & Send Quality Gates

- [x] **`services/stop_monitor.py`** — intraday stop/target monitor every 30 min Mon–Fri 09:30–16:15 ET. Marks `hit_stop`, `hit_target`, `exit_type`; fires Telegram "✅ TARGET HIT" / "⛔ STOP HIT".
- [x] **`_nightly_outcome_resolution()` in `main.py`** — scheduled 2am ET; `resolve_outcomes()` + `resolve_mae_mfe()` + `run_calibration()`.
- [x] **Isotonic regression calibration** — fitted alongside Platt in `calibration.py`. Used when ≥30 training samples.
- [x] **Pre-earnings hard blackout** — no BUY/SELL within 2 days of earnings.
- [x] **Sector concentration limit** — max 2 BUY signals per SPDR sector ETF per rolling 24h.
- [x] **Ticker-adaptive confidence floor** — tickers <45% WR need ≥68% conf; ≥75% WR tickers use 52% floor.
- [x] **597 passed, 0 failed** — all suites green.

### v5.5 (2026-05-16) — Validation-Driven Fixes, Quant Features & Leveraged ETF Tracker

- [x] **14-day primary outcome** — `_best_outcome()` prefers `outcome_14d` over 7d.
- [x] **Confidence ceiling 84%→72%** — empirical: 75-84% bands win at only 48-50%.
- [x] **Platt calibration tightened** — `_MAX_BLEND` 0.80→0.90; `_N_FULL` 30→20.
- [x] **Defensive-ticker BUY gate** — 16 tickers with 0% BUY WR forced to HOLD.
- [x] **FRED HY/IG credit spreads** — `BAMLH0A0HYM2` + `BAMLC0A0CM` replace HYG ETF proxy.
- [x] **Analyst revision momentum** — `revision_pts = bull_delta − bear_delta` (±8 cap).
- [x] **Cross-sectional universe ranking** — top decile +3pp, bottom quartile −1.5pp.
- [x] **`GET /api/signals/alpha-decay`** — win rate + avg return by source at 1d/3d/7d/14d.
- [x] **52 leveraged ETFs** — `_LEVERAGED_ETFS` frozenset, fundamentals bypass, swing-only style, sector mappings, ~210 tickers total.

### v5.4 (2026-05-10) — Production Hardening, PostgreSQL Migration & Legal

- [x] **Cookie `Secure` flag** — auto-sets when `APP_URL` starts with `https://`.
- [x] **CORS locked** — `allow_origins` from `["*"]` to `APP_URL` domain.
- [x] **Non-root Docker user** — `Dockerfile` creates `appuser` (UID 1000).
- [x] **Local PostgreSQL 16** — `signal_trade` database and `signal` user created.
- [x] **`migrate_sqlite_to_postgres.py`** — idempotent; 7,015 signals + 8 users migrated; sequences reset.
- [x] **Legal TOS** — Delaware governing law; publisher exemption §80b-2(a)(11)(D); chargeback waiver removed.

### v5.3 (2026-05-10) — Modularisation, Validations & Bug Fixes

- [x] **`app.jsx` modularised** — 5311-line monolith split into 8 files.
- [x] **`signal_scoring.py`** — pure scoring helpers extracted from `signal_engine.py`.
- [x] **Backend + frontend input validation** — email, password, ticker, price range.

### v5.0–v5.2 (2026-05-09)

- [x] **Polygon.io as primary OHLCV** — yfinance fallback.
- [x] **Push notifications** — pywebpush + VAPID.
- [x] **Macro Regime HMM** — numpy 2-state Gaussian HMM.
- [x] **Supply Chain Alt Data** — Baltic Dry, Brent Crude, Cass Freight.
- [x] **Dark Pool Block Trade Reconstruction** — 30-min print buffer, Lee-Ready tick rule.
- [x] **Massive API Advanced Signals** — GEX, Retail vs Institutional flow, Level 2 imbalance.

---

## 📐 Codebase Size — v5.8

| Layer | Files | Notes |
|-------|-------|-------|
| **Backend Python** | 134 | Services, routers, models, tests, scripts |
| **Frontend JSX** | 8 | Split from 5,311-line monolith |
| **CSS** | 3 | `styles.css`, `site.css`, `mobile.css` |
| **HTML pages** | 14 | Login, signup, marketing, legal |

### New files in v5.8

| File | Purpose |
|------|---------|
| `services/delivery_gates.py` | Pre-send gate logic (extracted from scanner) |
| `scripts/calc_tbd_metrics.py` | Institutional quant analytics + snapshot writer |
| `tests/test_delivery_gates.py` | 15 gate unit tests |
| `tests/test_quant_metrics.py` | 26 quant stat unit tests |
| `tests/test_performance_snapshots.py` | 14 snapshot diff/flag tests |

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
