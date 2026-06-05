# Signal.Trade — TODO

## 🔴 Pre-Launch Checklist

### Critical — must complete before anyone pays

- [ ] **1. Change owner password** — `backend/.env`: set `OWNER_PASSWORD=<16+ chars, mixed case, symbols>`. Default `ChangeMe123!` is committed to source. Risk: instant account takeover.
- [ ] **2. Deploy to public HTTPS URL** — Run `railway up` or `fly deploy`. Set `APP_URL=https://your-app.up.railway.app`. Risk: Stripe webhooks 404, OAuth callbacks broken, HTTPS-only cookies not sent.
- [ ] **4. Configure Stripe billing** — `STRIPE_SECRET_KEY` and price IDs set. Still needed: register webhook in Stripe Dashboard, copy `whsec_...` to `STRIPE_WEBHOOK_SECRET`. **§43: startup now logs CRITICAL if `STRIPE_WEBHOOK_SECRET` is empty in prod; webhook handler returns 500 explicitly.** Risk: checkout completes but tier never activates.
- [ ] **5. Register Telegram webhook** — After HTTPS deploy: `curl -X POST <https://your-app>/api/telegram/set-webhook`. Risk: subscribers cannot link Telegram.

### 🟠 HIGH IMPACT — Do within the first week

- [ ] **6. Configure SMTP (email)** — Add `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` to `.env`. Risk: no email verification, no password reset, no weekly digest.
- [ ] **7. Enable Telegram broadcast channel** — Create private channel, make bot admin, add `TELEGRAM_BROADCAST_CHANNEL_ID=-100...`. Risk: at >50 subscribers, per-user DM loop hits Telegram rate limit.
- [ ] **8. Train XGBoost ML model** — After ≥50 resolved signals: `POST /api/ml/train`. Risk: missing +5–8pp win rate improvement.
- [ ] **9. Configure Google OAuth** — `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET`.

### 🟡 BEFORE MARKETING / SCALE

- [ ] **10. Configure VAPID web push** — Generate keys via py_vapid. Risk: no browser push notifications.
- [ ] **11. Set up Cloudflare CDN** — Point DNS to Railway/Fly. Risk: slower global load.
- [ ] **12. Google AdSense** — Apply at adsense.google.com. Risk: no ad revenue from free tier.
- [ ] **13. Add Redis** — `railway add --plugin redis`. Risk: redundant API calls under concurrent load. **§43: stampede protection added for Redis-down fallback (per-key fetch lock + LRU dict cap).**
- [ ] **14. Upgrade SendGrid** — Essentials (~$20/mo) before daily signups + resets exceed 100 emails/day.
- [x] **15a. Eliminate Babel from production — A8 complete 2026-05-31** — esbuild bundles built (app 408KB, site 53KB, mobile 50KB). `load-app.js` hardened: Babel fallback localhost-only. CSP `unsafe-eval` eliminated. React dev→production builds. `sw.js` cache v4.

---

## End-to-End System Audit — v10.5 (2026-06-03, gate validation + EDGAR Tier-3 + §76 Altman removed)

> Updated from v10.2. v10.3–v10.5 (2026-06-02/03): Dead gate removal (§59/§60/§61/§67/§64/§68/§78/TRIN/AD); --validate-live-gates flag; SIGNAL_VALIDATION.md created; §63 cointegration added to backtest scoring; EDGAR point-in-time validation (backtest_edgar.py); §76 Altman Z-Score removed from gates/fundamentals.py (74% false-positive rate on IS universe); 1054 tests pass.
> Rating scale: completeness × soundness.

### Overall Rating

| Area | Rating | Δ | Notes |
|---|---:|---|---|
| Product completeness | 8.0/10 | — | Signal product, auth, billing, Telegram, paper trading, mobile/PWA, admin tooling all present. |
| Trading/research depth | 8.8/10 | ↑ from 8.7 | Gate validation (--validate-live-gates); EDGAR Tier-3 validation; §76 Altman removed (reduces IS/live gap). IS v10.5: N=230, Sh=0.20. |
| Backtest methodology | 8.3/10 | ↑ from 8.2 | SIGNAL_VALIDATION.md created (41 gates classified). §63 cointegration added. EDGAR point-in-time (106/107 tickers cached). |
| OOS validation | 6.2/10 | — | OOS v6 CLEAN Sh=0.16 ✅. v7+v8 pre-specified (15 tickers). Need ≥30 live trades in those names. |
| Signal alpha quality | 6.2/10 | ↑ from 5.7 | §76 Altman removed (was penalising 74% of signals). §85-1 still pending ≥200 resolved signals. EDGAR §50/§73 confirmed neutral. |
| Risk management | 8.2/10 | — | Unchanged. |
| Calibration quality | 8.0/10 | — | Cal v4: Brier 0.2641. Next recal after ≥50 post-A19 resolved signals. |
| ML methodology | 8.0/10 | — | Entry model OOS AUC 0.6399 unchanged. Needs N≥300 live for deployment. |
| Backend architecture | 7.3/10 | ↑ from 7.2 | gates/statistical.py now §63-only (§59/§60/§61 scoring removed). 1054 tests. |
| Frontend architecture | 7.0/10 | — | A8 complete. |
| Security posture | 7.0/10 | — | CSP `unsafe-eval` eliminated. **Default owner password still in .env ⚠ — critical pre-launch.** |
| Testing/CI | 9.5/10 | — | 1054 passing (3 skipped). |
| Deployment readiness | 6.2/10 | — | HTTPS, Stripe webhook, SMTP, Telegram channel, VAPID all still needed. |

**Overall project rating: 7.7/10** (↑ from 7.6 — §76 Altman removed, EDGAR validation complete, gate validation infrastructure added)

> **Key honest assessment (v10.5):** IS base Sh=0.20 (N=230, v10.5 with §63 coint). OOS v6 CLEAN Sh=0.16.
> Forward: 0.13–0.18. §76 Altman removal likely reduces IS/live WR gap (was penalising 74% of signals).
> Next: §85-1 audit at ≥200 resolved signals; OOS v7 when ≥30 live trades in healthcare/consumer/exchange names.
> To reach forward 0.50: external alpha data required (options flow, order flow).

---

## 🎯 Strategic TODOs

### §31 Universe Expansion — Next Steps (2026-05-31)

> From Russell 1000 screener run. Full results in `docs/LEARNINGS.md §31`. PASS/WATCH tickers need IS validation before adding to live engine.

- [x] **§31-1. Run IS backtest with 105-ticker universe** — ✅ 2026-06-01: N=183 (↑+10), WR=70.5%, Sharpe=0.30 (↑+0.01). Exceeds v9.0 baseline (N=173, Sh=0.29). Added sector map fix: 32 TICKERS entries were missing from TICKER_TO_SECTOR (SLB/EOG/MPC/CAT/DE/LMT defaulted to XLK — now correctly XLE/XLI).
- [x] **§31-2. Validate MCO individually** — ✅ 2026-06-01: IS N=3, WR=66.7%, Avg=+1.12%. Aggregate IS with MCO: N=188, Sh=0.31 (↑+0.01). Added permanently to TICKERS (XLF, live-eligible). Sector map entry added.
- [x] **§31-3. Validate HAL** — ✅ 2026-06-01: IS N=2, WR=100%, Avg=+6.54%. Added to TICKERS as backtest research-only (XLE, blocked in live delivery_gates). Aggregate Sh maintained 0.31. PANW/APTV/BWA deferred (PANW live defensive block, APTV/BWA in HELD_OUT).
- [x] **§31-4. Energy sub-sector expansion — REJECTED** — ✅ 2026-06-01: FTI IS N=1 WR=0% Avg=−6.80%; TRGP IS N=4 WR=25% Avg=−1.30%. Adding both dragged aggregate Sh from 0.31→0.28. Both removed. Fast-mode screener WRs (FTI 83%, TRGP 71%) do not replicate in full IS. Energy sub-sector MR not viable at 2003–2026 horizon.
- [x] **§31-5. XLI already live-eligible — no gate change needed** — ✅ 2026-06-01: Checked `delivery_gates.py`: `BLOCKED_SECTORS = {"XLF", "XLP", "XLU"}`. XLI is NOT blocked. CSX/UNP/ETN/XYL are in TICKERS, mapped to XLI, and pass all delivery gates. Live signals fire without any code change. A15 (sector XGBoost) would improve ML scoring quality for XLI trades but is not a blocker.
- [x] **§31-6. Re-run screener prep done** — MCO and HAL added to `TICKERS` (which backs `_PRODUCTION_TICKERS` → `_SKIP`). Next screener run (`python scripts/screen_russell1000_mr_candidates.py --fast`) will automatically skip both. No code change needed.

### §85 Fundamental Score-Modifier Live Audit

> **§76 Altman removed 2026-06-03** from `gates/fundamentals.py` via EDGAR point-in-time validation: 74% false-positive rate (structural reasons, not distress). Remaining modifiers: §50 Piotroski, §74 Beneish, §73 Insider, §51 Forward PE, §52 SI velocity, §58 EPS revision.

- [x] **§85-1. Script ready** — `python scripts/gate_contribution_analysis.py --section85 --after 2026-06-01`. Segments by Piotroski/PE/ShortInt/Insider/Beneish/EPS-Revision (Altman removed). KEEP/WATCH/REMOVE verdicts at N≥30. **Pending live data:** needs ≥200 resolved signals. Run when ready; remove any modifier with ΔWR < −1pp + N≥30.
- [x] **§85-A. §76 Altman removed (EDGAR backtest validation)** — ✅ 2026-06-03. `scripts/backtest_edgar.py` confirmed: 74% of IS tickers always below Z'<1.23 (structural). Standalone: N 230→79, Sh −0.03. Recalibrated Z'<0: ΔSh=0.00. Removed from `gates/fundamentals.py`.
- [ ] **§85-2. Audit EDGAR MD&A sentiment contribution** — `edgar.py` MD&A NLP is annual 10-K data applied to a 5-day trade. Tag live signals that received an MD&A score adjustment and compute ΔWR. If no improvement, disable. Low priority until §85-1 data is available.

### Alpha Research (§45–§46, active)

- [x] **Validate TREND=0 ablation** — §46 complete (2026-05-29)
- [x] **Ablate CMF family** — `BASE_WEIGHTS["cmf"]=0.0` applied; live engine CMF scores ×0.5 (2026-05-30)
- [ ] ~~**Ablate VOL family**~~ — **CANCELLED.** §46 reversal: VOL is load-bearing with TREND=0 (ΔSharpe=−0.05 if removed).
- [x] **Re-run full IS backtest at OSC×1.0** — IS v9.0: WR=70.5%, Sharpe=0.29 (far exceeds §43 baseline). OSC weight confirmed 1.0 at `signal_engine.py:3126`.
- [x] **Redesign OOS universe** — Done via OOS v6 (2026-05-31): HELD_OUT_TICKERS verified 0 blocked-sector tickers (XLI/XLV/XLE). All 48 are XLK/XLY/XLC/XLB/XLF. XLF performance-laggards (STT/MTB/HBAN/ZION/CFG) in _OOS_BLOCKED_TICKERS.
- [ ] **Monitor stop-hit rate at 1.5s/2.0t** — Check after 50+ resolved signals under new 1.5s/2.0t regime to confirm R:R holds.

### §47–§58 Research Agenda — Status

All implemented. See CLAUDE.md for constants and gate details.

- [x] §47 VIX term structure backwardation — already in `macro.py`
- [x] §48 IVR gate — implemented in `signal_engine.py`
- [x] §49 Put-call skew — implemented in `signal_engine.py`
- [x] §50 Piotroski F-Score — already in `fundamentals.py`
- [x] §51 Forward PE value trap — implemented in `signal_engine.py`
- [x] §52 Short interest velocity — implemented in `signal_engine.py`
- [x] §53 Post-earnings timing — **REJECTED** (−17.4pp WR in 35–65d window)
- [x] §54 VIX<15 MR suspension — hard block in `delivery_gates.py`
- [x] §55 Cross-asset macro 3/3 headwinds — hard block in `delivery_gates.py`
- [x] §56 Kelly position sizing — VIX-conditional `positionSizeScale` in `_assemble_signal()`
- [x] §57 Thursday DOW gate — −3pp haircut in `delivery_gates.py`
- [x] §58 EPS revision momentum — proxied by existing Finnhub `revision_pts`

### §59–§83 Research Agenda — Status

All implemented. See CLAUDE.md for constants and gate details.

- [x] §59 OU halflife — hard-block gate restored to backtest (OU_HALFLIFE_MAX=25d); scoring modifier removed from `gates/statistical.py` (2026-06-02: confirmed dead as scorer; restored as hard block after v10.4 regression)
- [x] §60 Hurst exponent — same as §59; hard-block in backtest (HURST_TREND_CEIL=0.80); scoring modifier removed from `gates/statistical.py`
- [x] §61 Idiosyncratic volatility — **removed** from both backtest and `gates/statistical.py` (dead gate: ΔSh=0.00, ΔN=0 — 2026-06-02)
- [ ] §62 VRP per-stock — ⏳ needs per-stock IV history (Polygon Options upgrade)
- [x] §63 Sector cointegration — `compute_cointegration_zscore()` in `technicals.py`; **now also in backtest scoring** (rolling 252d coint_z column, +4/+2/−2 pts — 2026-06-03)
- [x] §64 Yield curve slope — `macro.py` fetch; `signal_engine.py` gate
- [x] §65 TRIN — `fetch_trin()` in `macro.py`; `signal_engine.py` gate
- [x] §66 AD breadth — `fetch_ad_breadth()` in `macro.py`; Zweig thrust gate
- [x] §67 FOMC proximity — `FOMC_DATES` in `macro.py`; `delivery_gates.py` hard block
- [x] §68 2Y Treasury rate gate — `macro.py` fetch; XLK penalty in `signal_engine.py`
- [x] §69 GEX flip level — `compute_dealer_positioning()` in `options.py`
- [x] §70 Zero-DTE put spike — `score_options()` in `options.py`
- [x] §71 Max pain convergence — `compute_max_pain()` in `options.py`
- [x] §72 VRP proxy — `score_options()` in `options.py`
- [x] §73 Insider BUY clustering — `edgar.py` unique_buyers; `signal_engine.py` gate
- [x] §74 Beneish M-Score — `compute_beneish_mscore()` in `fundamentals.py`
- [ ] §75 Active share buyback window — ⏳ EDGAR 8-K parsing complexity
- [x] §76 Altman Z-Score — **REMOVED from `gates/fundamentals.py`** (2026-06-03, EDGAR validation: 74% false-positive rate on IS universe — structural, not distress). `compute_altman_zscore()` in `fundamentals.py` still computes the value; gate no longer fires.
- [x] §77 Tax-loss window — implemented in `signal_engine.py`
- [x] §78 Sep/Oct seasonality — threshold adjustment in `delivery_gates.py`
- [ ] §79 Q1 rebalancing — ⏳ needs prior-year sector return stored at Dec-31
- [x] §80 NBBO spread quality — reads `_snapshot_cache.lastQuote`
- [x] §81 Block print detection — `get_recent_block_prints()` in `polygon_client.py`
- [x] §82 Adaptive ATR trailing stop — `trailingStopPct` in signal dict
- [x] §83 Cross-signal correlation penalty — avg pairwise corr in `scan_all()`
- [ ] §84 Survivorship bias correction — ⏳ needs Norgate/Sharadar point-in-time data (~$20–33/mo)

### Paid / Structural Alpha

- [ ] **Options flow confirmation gate** — Subscribe to Unusual Whales API (~$50/mo) or Market Chameleon. Expected ΔSharpe: +0.15–0.25 per-trade. **Highest-leverage single improvement available.**
- [ ] **GEX support levels** — SpotGamma API (~$99/mo). Enter only when `price ≤ gex_support_level × 1.01`. Expected ΔSharpe: +0.10 per-trade.
- [ ] **Market-neutral beta hedge** — Short 0.9× position value in SPY at entry. Requires margin account. **§QuantEngine validated: IS Sharpe 0.29 = 0.12 pure alpha + 0.17 beta. True forward estimate ≈ 0.10–0.15.**

### Pillar 1 — ML & Analytics

- [x] **Sector sub-model retraining** — `train_sector_model()` in `train_backtest_ml.py`; `predict_entry_prob_sector()` in `signal_ml.py` with auto-fallback to global model.
- [x] **Swing recalibration** — Floor recalibrated 70→46% post phantom-win correction (2026-05-31). `delivery_gates.py:STYLE_CONF_FLOORS["swing"]=46.0`.
- [ ] **LSTM for regime-conditioned confidence** — Shallow LSTM on rolling 30-day windows (VIX, SPY ret, yield curve, breadth) to predict regime transitions 3–5 days ahead.
- [x] **Feature importance audit** — `shap_audit()` added to `eval_ml.py §7`; flags inverted/near-zero features via TreeExplainer.

### Pillar 2 — Data Architecture

- [ ] **Commercial data feed evaluation** — Polygon Advanced ($199/mo) or Benzinga Pro ($49/mo).

### Pillar 4 — Execution

- [ ] **Telegram broadcast channel** — Enable `TELEGRAM_BROADCAST_CHANNEL_ID` before marketing push. Required at >50 subscribers.
- [x] **OAuth broker execution (live trading)** — ✅ 2026-06-05. Per-user Alpaca credentials (Fernet-encrypted). `routers/broker.py`: connect/status/disconnect/orders/settings. `services/broker_svc.py`: encryption + `execute_signal_for_user()`. `alpaca_rest.py`: live base URL + notional orders. `scanner._maybe_auto_execute_for_signal()`: Pro-gated per-user hook in delivery loop. Migration `a3f7c9d12e45`: `users` + `broker_orders` table. 27 new tests.

---

## 🔬 §QuantEngine Results — Actionable Findings (2026-05-31)

> From `--beta-hedge`, `--portfolio`, `--forecast-sizing`, `--walk-forward` backtest runs.
> See `docs/Stats.md §QuantEngine` for full tables.

- [x] **QE1. Forecast sizing in backtest** — `--forecast-sizing` flag; +0.04 Sharpe, +2.0pp WR validated.
- [x] **QE2. Conviction sizing in live engine** — Done 2026-05-31. Recalibrated 2026-06-01 after cal v4 shifted all signals to <55%. L4: `clamp((conf−40)/14+0.5, 0.5, 1.5)`. 40%→0.5×, 47%→1.0×, 54%→1.5× (was 57/62/67 — stuck at floor post-recal).
- [x] **QE3. Live min_confidence** — Recalibrated 57→40% post phantom-win correction (2026-05-31). `config.py:min_confidence=40.0`. `delivery_gates.py` L66: `driven by global min_confidence (40%)`.
- [x] **QE4. T-bill modelled in portfolio simulation** — Done 2026-05-31. `run_portfolio_simulation()` credits 3.5%/yr on idle slots; reports alongside CAGR. Live deployment (SHY/BIL actual buy) requires broker OAuth — pending A16.
- [x] **QE5. Risk docs updated** — Done 2026-05-31. `docs/Stats.md §1` now cites concurrent Max DD −7.06% (8× per-trade). Phantom wins corrected: reported WR 42.5% (was 58.6%), Sharpe 1.32 (was 5.52).

---

## 🔬 Post-§82 Research Hardening (2026-05-30)

> Items ordered by impact.

### 🔴 Critical (do immediately)

- [x] **A1. Unit tests for §59–§82 gates** — ✅ Done 2026-05-30: 30 tests in `tests/test_gates_5982.py`. Remaining without tests: §73 insider, §74 Beneish, §76 Altman, §69–§72 options gates.
- [x] **A2. IS threshold sensitivity sweep** — ✅ Done 2026-05-30: `--gate-sweep` flag in `backtest_technicals.py`.
- [x] **A3. OOS universe v5** — ✅ Done 2026-05-30: **CLEAN N=27, WR=55.6%, Avg=+0.18%, Sharpe=0.05 ⚠**. ALL N=30, WR=50.0%, Sharpe=−0.07. See A3a–A3c below.
- [x] **A3a. Apply BLOCKED_TICKERS to OOS simulation** — ✅ `_OOS_BLOCKED_TICKERS = frozenset({"AMAT", "KLAC"})` added.
- [x] **A3b. Block STT/MTB in delivery_gates** — ✅ Added to `BLOCKED_TICKERS` in `delivery_gates.py`.
- [x] **A3c. OOS v5 — grow N to ≥30** — ✅ `HELD_OUT_TICKERS` expanded 18→21 (added AVGO, ACN, MCD).

### 🟠 High Impact

- [x] **A4. Confidence re-calibration** — v3 done 2026-05-31 (Brier 0.2432 val). v4 done 2026-06-01 post-A19: Brier 0.2641, 18,656 signals updated avg −1pp (all now <55%). L4 sizing recalibrated to new 40-54% confidence band. True §82/post-A19-aware cal needs N≥50 post-A19 resolved signals.
- [x] **A5. Live gate contribution monitoring — script complete** — `python scripts/gate_contribution_analysis.py --after 2026-06-01`. Full gate audit + §85-1 fundamental-only mode (`--section85`). Pending: run when ≥200 resolved live signals available. Remove gates where ΔWR < −1pp with N≥30.
- [ ] **A6. Monitor live stop-hit rate at 1.5s/2.0t** — If live stop-hit rate exceeds 55% on the first 50 resolved signals, revert to 1.5s/2.5t.

### 🟡 Medium Priority

- [x] **A7. Extract remaining gates from `signal_engine.py`** — ✅ 2026-06-01: Created `gates/statistical.py` with `apply_statistical_gates()` covering §59 OU halflife, §60 Hurst, §61 idio vol, §63 sector cointegration. Replaced 4 inline blocks (~90 lines) in `signal_engine.py`. Gates/ now has 7 files (+ statistical.py). 1039 tests pass, no regressions.
- [x] **A17. ML-derived confidence as challenger to heuristic scoring** — Done 2026-06-01. — The entry model (`_ENTRY_FEATURE_NAMES`, 14 raw tech features) already is a pure ML ranker for the entry decision. What doesn't yet exist: a model that replaces the heuristic point accumulator in `generate_signal()` as the primary confidence source. Prototype: train XGBoost on the same 14 tech features + the 23 signal-level features → predicted 10d return (regression) or binary WR (classification). Blend its output as `raw_confidence` in `blend_confidence()` as a third model slot. Deploy as challenger only if live AUC delta > 0.005. Goal: determine whether the heuristic ±point system adds discriminating power that the ML models don't already capture from the same inputs.
- [x] **A19. Fix score double-counting: Piotroski / FCF Yield / Insider base score** — Fixed 2026-06-01. — Three signals are scored twice: once in the direct `generate_signal()` body and again via the async worker (merged at L7015). Root cause: worker architecture was added as a concurrent layer but the original synchronous blocks weren't removed.
  - **Piotroski**: remove from `fundamentals_worker` (signal_workers.py:147–175); canonical source is `apply_quality_screens` in gates/fundamentals.py (L5693).
  - **FCF Yield**: remove the direct block at signal_engine.py:5700–5726; canonical source is `fundamentals_worker` (signal_workers.py:178–204).
  - **Insider base score**: remove `score += iscore` at signal_engine.py:2722; canonical source is `institutional_worker` (signal_workers.py:425–426). Keep `apply_insider_clustering` (unique-buyers bonus at L2753) — it's separate logic not in the worker.
  - After fix: re-run IS backtest to confirm Sharpe and WR move (scores have been inflated — WR may shift slightly, calibration will need a patch run).

- [x] **A18. Friction sensitivity sweep** — ✅ 2026-06-01: `--friction` flag sweeps 0.25%–1.25% round-trip, reports N/WR/Avg/Sharpe/ΔSharpe per level, flags Sh<0.20 tipping point. ADV-participation cost model noted in output as requiring intraday ADV data not in backtest. Run: `python scripts/backtest_technicals.py --friction`.
- [x] **A8. Babel → esbuild migration** — Complete 2026-05-31 via esbuild (not Vite). Bundles: app 408KB, site 53KB, mobile 50KB. `'unsafe-eval'` eliminated from CSP. See item 15a.
- [x] **A20. Gate validation infrastructure** — ✅ 2026-06-02: `--validate-live-gates` flag added to backtest. Ablates all testable gates in IS, measures ΔSharpe. Results: §57 Thursday ✅ KEEP (−0.09 Sh), §59/§60 ⚠ REVIEW, all others ΔSh≈0. Creates `docs/SIGNAL_VALIDATION.md` tracking 41 live gates.
- [x] **A21. EDGAR Tier-3 backtest validation** — ✅ 2026-06-03: `scripts/backtest_edgar.py` downloads point-in-time SEC EDGAR data for 106/107 IS tickers. Results: §50 Piotroski ΔSh=0.00 (neutral), §73 Insider ΔSh=0.00 (neutral), §76 Altman ΔSh=−0.03 (harmful). §50+§76 apparent +0.12 Sh = BUY_THRESH=55 equivalent (OOS rejected: Sh 0.42→0.00). Cache saved to `data/edgar_fundamentals.pkl`.
- [x] **A22. §76 Altman removed from live engine** — ✅ 2026-06-03: Removed from `gates/fundamentals.py`. Was applying −15 pts to 74% of live signals (structural false positives). Tests updated (1054 passing).
- [x] **A23. §63 Sector cointegration added to IS backtest** — ✅ 2026-06-03: Rolling 252-day Engle-Granger Z-score computed post-Pool for each ticker vs its sector ETF. Added to `compute_scores()` and `score_row()` (+4/+2/−2 pts). Ablated in `--validate-live-gates`. ΔSharpe pending next full IS run.

### 🟠 Pending (data-gated — needs resolved live signals)

- [ ] **A24. §85-1 Fundamental modifier audit** — Run `python scripts/gate_contribution_analysis.py --section85 --after 2026-06-01` when ≥200 resolved post-A19 signals available (~6-8 weeks). Remove any modifier with ΔWR < −1pp at N≥30. Primary suspects: §50 Piotroski (wrong horizon), §74 Beneish (accounting focus, not 10d), §73 Insider (48h EDGAR lag).
- [ ] **A25. Calibration v5** — Run `python scripts/backfill_confidence.py --force --apply` when ≥50 post-A19 resolved signals available (~2-3 weeks). Current cal v4 used pre-A19 data only.
- [ ] **A26. OOS v7/v8 validation** — Run `python scripts/backtest_technicals.py --oos` when ≥30 live trades exist in the pre-specified OOS tickers (SYK/RMD/IDXX/ZBH, RL/DECK/POOL, NDAQ/CBOE/BR, LNC/AMG/PAYC/SIG/AEO). Healthcare/consumer/exchange-operator focus. If pass, promote to IS → N grows.
- [ ] **A27. ML model deployment** — Run `POST /api/ml/train` when N≥300 live resolved signals. Entry model at OOS AUC=0.6399 already built; waiting on data. Champion/challenger framework wired; just needs the signal count.

### ⏳ Deferred (needs paid data or infrastructure)

- [ ] **A9. §62 VRP per-stock** — Needs per-stock 52-week IV history. Revisit if Polygon Options tier upgrades.
- [ ] **A11. §75 Buyback window** — Requires EDGAR 8-K parsing for repurchase announcements.
- [ ] **A12. §79 Q1 rebalancing gate** — Needs prior-year sector ETF return stored at Dec-31.
- [ ] **A13. §84 Survivorship bias correction** — Purchase EODHD (~$20/mo) or Norgate ($33/mo) for delisted tickers. Expected: IS WR drops 2–4pp, Sharpe −0.02 to −0.05 (makes backtest honest).
- [ ] **A14. §83 cross-signal correlation** — Already implemented. Needs live validation: track `avg_corr` at entry for 200 signals and confirm sized-down entries don't underperform.
- [ ] **A15. Sector-specific XGBoost retraining** — Unblock XLF/XLP/XLU. Requires ≥200 resolved signals per sector.
- [x] **A16. Broker OAuth + order execution** — ✅ 2026-06-05. See Pillar 4 entry above for full details.

---

## 👁️ Known Issues

| Issue | Severity | Status |
|---|---|---|
| **Default owner password in source** | Critical | ❌ Must change before first paid signup |
| **§59–§82 gates — unit tests** | Resolved | ✅ §73/§74/§76 tests updated (§76 now confirms no Altman cards). 1054 passing (3 skipped). |
| **OOS v6 CLEAN N=51, Sharpe=0.16** | Resolved | ✅ Pre-specified 30 new tickers (2026-05-31). Curation bias gap −0.08 (smallest ever). Edge generalises. |
| **XLF/XLP/XLU blocked** | High | 🔄 Requires sector-specific XGBoost retraining |
| **Autonomous execution** | High | ✅ Broker execution complete (2026-06-05). Per-user Alpaca credentials + notional orders wired into scan delivery loop. |
| **Monolithic signal_engine.py (8k+ lines)** | Medium | 🔄 Delivery gates + scanner decomposed. Full engine decomposition deferred — see A7 |
| **Score double-counting: Piotroski/FCF/Insider** | Resolved | ✅ Fixed 2026-06-01. Piotroski removed from worker (canonical: apply_quality_screens). FCF removed from engine body (canonical: fundamentals_worker). Insider base score removed from engine body (canonical: institutional_worker). Confidence penalty kept in engine (reads accumulated score). |
| **Calibration v3 applied** | Resolved | ✅ Brier 0.2432, gap −0.5pp. True §82-aware cal needs N≥200 post-§82 resolved (~29wk). |
| **Calibration recal post-A19** | Partial | ⚠ Cal v4 run 2026-06-01: Brier 0.2641, 18,656 signals updated avg −1pp (all now <55%). Pre-A19 data only (0 post-A19 resolved signals in DB). Re-run `backfill_confidence.py --force --apply` after ≥50 post-A19 resolved signals for a clean calibration. |
| **TICKER_TO_SECTOR bug (fixed 2026-06-01)** | Resolved | ✅ 32 TICKERS entries (SLB/EOG/MPC/CAT/DE/LMT etc.) were missing — defaulted to XLK. "Live-equivalent" IS stats included blocked-sector trades. All 107 tickers now correctly mapped. |
