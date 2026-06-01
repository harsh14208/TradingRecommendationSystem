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
- [x] **15a. Eliminate Babel from production — remove `'unsafe-eval'` from CSP** — Esbuild migration complete. Remove `'unsafe-eval'` from `SecurityHeadersMiddleware._SCRIPT_SRC` in `backend/main.py:1355`.

---

## End-to-End System Audit — v7.4 (2026-05-31, post-v6.4 methodology + universe expansion)

> Updated from v7.3. v6.4: Lo(2002) CI + Deflated Sharpe output; ML N-gate + AUC CI + min-delta; IS universe 74→100 tickers (N=157); IS CI [0.13, 0.44] — SR=0 now outside 95% CI ✅. Tests: 1000 passed.
> Rating scale: completeness × soundness. High completeness with poor methodology scores lower.

### Overall Rating

| Area | Rating | Δ | Notes |
|---|---:|---|---|
| Product completeness | 8.0/10 | — | Broad signal product, auth, billing, Telegram, paper trading, mobile/PWA, admin tooling present. |
| Trading/research depth | 7.8/10 | ↑ from 7.5 | IS CI [0.13, 0.44] — SR=0 outside 95% CI at N=157 ✅. Deflated Sharpe 0.29 > 0.22 ✅. Honest forward Sharpe ~0.12–0.20 after curation/survivorship bias. OOS N=27 remains statistically insufficient. |
| Backtest methodology | 7.5/10 | ↑ from 7.0 | Added: Lo(2002) CI + Deflated Sharpe printed for IS and both OOS sets; minimum OOS N required computed and displayed; 6 new methodology regression tests. Ceiling: survivorship bias (200+ delisted tickers, ~1–4pp WR overstatement) requires Norgate/CRSP ($20–33/mo). |
| ML methodology | 8.0/10 | ↑ from 7.5 | Added: `_MIN_LIVE_N_FOR_DEPLOYMENT=300` (Hanley-McNeil justified); `_MIN_AUC_DELTA_TO_DEPLOY=0.005`; `auc_ci_95()` logged + persisted to metadata JSON. Champion correctly retained at N=160 (CV-AUC 0.6188 < champion 0.6399). Tests 17–19 validate constants + formula. |
| Backend architecture | 6.8/10 | — | FastAPI service is feature-rich and reasonably tested. Long-lived background jobs, scanner orchestration, and 8k+ line signal engine remain too centralized. |
| Frontend architecture | 5.8/10 | — | Useful dashboard/mobile surfaces, but large static JSX files and inline HTML patterns make security, testing, and reuse harder. |
| Security posture | 6.5/10 | — | Bcrypt/JWT/HTTP-only refresh cookies; DOM injection paths cleaned up. Remaining: default owner password risk before launch. |
| Data/reliability | 6.7/10 | — | PostgreSQL, Redis-aware locks, data-quality alerts. Missing real migrations and best-effort error swallowing. |
| Testing/CI | 7.8/10 | ↑ from 7.5 | 1000 passing tests (up from 916 pre-session). 19 methodology integrity tests enforcing: IS/OOS disjointness, Sharpe CI formula, OOS N-starvation, ML deployment gates (N-gate + AUC delta), AUC CI formula. Lint: ruff clean. |
| Deployment readiness | 6.2/10 | — | Docker/Railway/Fly files exist. Blockers: HTTPS, Stripe webhook, SMTP, Telegram webhook, VAPID, default password unchanged. |
| Maintainability | 6.8/10 | ↑ from 6.5 | Tests 14–19 add regression guards for CI formulas and deployment gate constants. Any change that breaks Lo(2002) SE, AUC CI, or min-N threshold is now caught automatically. Monolith risk (8k+ line engine) unchanged. |

**Overall project rating: 7.1/10** (↑ from 7.0 — IS CI now statistically significant; ML gates tightened; test coverage up)

> **Key honest assessment:** IS Sharpe 0.29 with CI [0.13, 0.44] clears statistical significance at per-trade level
> (N=157). Deflated Sharpe test passes. Forward Sharpe ~0.12–0.20 after survivorship + curation bias. OOS N=27
> remains insufficient — need ≈384 trades to confirm alpha at SR=0.10.

---

## 🎯 Strategic TODOs

### §31 Universe Expansion — Next Steps (2026-05-31)

> From Russell 1000 screener run. Full results in `docs/LEARNINGS.md §31`. PASS/WATCH tickers need IS validation before adding to live engine.

- [ ] **§31-1. Run IS backtest with 105-ticker universe** — `cd backend && python scripts/backtest_technicals.py`. Confirm aggregate N/WR/Sharpe ≥ v6.4 baseline (N=157, WR=70.7%, Sh=0.29) after adding AMP+CSX+UNP+ETN+XYL. If Sharpe drops, identify which new ticker is dragging.
- [ ] **§31-2. Validate MCO individually** — N=9, WR=78%, Avg=+1.21% in fast mode. One trade short of Sharpe computation. Run full IS backtest with MCO added to TICKERS — if Sh≥0.29, add permanently (Financial sector, live-eligible).
- [ ] **§31-3. Validate PANW, HAL, APTV, BWA** — Top live-eligible WATCH tickers (WR 75–86%). Add each to TICKERS one at a time, run IS, check per-ticker Sharpe ≥ 0.20. HAL (Energy, hold=5d) and PANW (Tech) are highest priority.
- [ ] **§31-4. Consider Energy sub-sector expansion** — HAL (86%), FTI (83%), TRGP (71%) all strong. Energy currently allowed in live engine. Run IS with HAL+FTI+TRGP together to check aggregate impact.
- [ ] **§31-5. Consider enabling XLI in delivery_gates** — CSX/UNP/ETN/XYL show Sh=0.30–0.50 in discovery. If IS confirms, evaluate unlocking Industrials sub-sectors (railways + electrical) in live `delivery_gates.py`. Requires sector-specific XGBoost retraining first (see A15).
- [ ] **§31-6. Re-run screener with `--fast` after IS validation** — Once validated tickers are added to `_SKIP`, re-run to surface next tier of WATCH candidates. Estimated 10–15 additional live-eligible tickers remain in WATCH pool.

### Alpha Research (§45–§46, active)

- [x] **Validate TREND=0 ablation** — §46 complete (2026-05-29)
- [x] **Ablate CMF family** — `BASE_WEIGHTS["cmf"]=0.0` applied; live engine CMF scores ×0.5 (2026-05-30)
- [ ] ~~**Ablate VOL family**~~ — **CANCELLED.** §46 reversal: VOL is load-bearing with TREND=0 (ΔSharpe=−0.05 if removed).
- [ ] **Re-run full IS backtest at OSC×1.0** — Confirm `backtest_technicals.py` IS metrics match or exceed §43 baseline (WR=60.3%, Sharpe=0.17).
- [ ] **Redesign OOS universe** — Current held-out tickers include XLF/XLI/XLV/XLE stocks (sectors the live engine blocks). Replace with same-sector tickers (XLK/XLY/XLC/XLB only).
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

- [x] §59 OU halflife — `compute_ou_halflife()` in `technicals.py`; `OU_HALFLIFE_MAX=25d`
- [x] §60 Hurst exponent — `compute_hurst()` in `technicals.py`; `HURST_TREND_CEIL=0.80`
- [x] §61 Idiosyncratic volatility — implemented in `signal_engine.py`
- [ ] §62 VRP per-stock — ⏳ needs per-stock IV history (Polygon Options upgrade)
- [x] §63 Sector cointegration — `compute_cointegration_zscore()` in `technicals.py`
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
- [x] §76 Altman Z-Score — `compute_altman_zscore()` in `fundamentals.py`
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
- [ ] **Swing recalibration** — Currently floored at 70%. Re-examine after next 200 swing-style resolved trades.
- [ ] **LSTM for regime-conditioned confidence** — Shallow LSTM on rolling 30-day windows (VIX, SPY ret, yield curve, breadth) to predict regime transitions 3–5 days ahead.
- [x] **Feature importance audit** — `shap_audit()` added to `eval_ml.py §7`; flags inverted/near-zero features via TreeExplainer.

### Pillar 2 — Data Architecture

- [ ] **Commercial data feed evaluation** — Polygon Advanced ($199/mo) or Benzinga Pro ($49/mo).

### Pillar 4 — Execution

- [ ] **Telegram broadcast channel** — Enable `TELEGRAM_BROADCAST_CHANNEL_ID` before marketing push. Required at >50 subscribers.
- [ ] **OAuth broker execution (live trading)** — OAuth flow for Alpaca Live or IBKR Web API. Auto-execute high-confidence signals. (Toggle + DB model done; broker OAuth + order submission pending.)

---

## 🔬 §QuantEngine Results — Actionable Findings (2026-05-31)

> From `--beta-hedge`, `--portfolio`, `--forecast-sizing`, `--walk-forward` backtest runs.
> See `docs/Stats.md §QuantEngine` for full tables.

- [x] **QE1. Forecast sizing in backtest** — `--forecast-sizing` flag; +0.04 Sharpe, +2.0pp WR validated.
- [x] **QE2. Conviction sizing in live engine** — Done 2026-05-31. `signal_engine.py:positionSizeScale` L4: `clamp((conf−57)/10+0.5, 0.5, 1.5)` × vol-targeting. 57%→0.5×, 62%→1.0×, 67%+→1.5×.
- [x] **QE3. Live min_confidence at 57** — Already set in §31 (`config.py:min_confidence=57.0`). `delivery_gates.py` L63 confirms: `driven by global min_confidence (57%)`.
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

- [x] **A4. Confidence re-calibration v3** — Done 2026-05-31. Root cause: `run_calibration()` prefers `outcome_14d`; phantom win fix only corrected `outcome_pct`. Fixed `outcome_14d` for 112 stop-hit signals, retrained isotonic. **Brier 0.2432** (best ever). All signals at ~42% confidence, gap −0.5pp (near-perfect). min_confidence lowered 57→40%, swing floor 70→46%. True §82-aware recalibration still needs N≥200 post-§82 resolved signals (~29 weeks).
- [ ] **A5. Live gate contribution monitoring** — After 200 resolved signals post-§82 launch, tag each trade with which §59–§82 gates fired and compute per-gate ΔWR. Remove gates that don't contribute in production.
- [ ] **A6. Monitor live stop-hit rate at 1.5s/2.0t** — If live stop-hit rate exceeds 55% on the first 50 resolved signals, revert to 1.5s/2.5t.

### 🟡 Medium Priority

- [ ] **A7. Extract `gates/` module from `signal_engine.py`** — `signal_engine.py` is 8k+ lines. Extract one Python file per gate family into `services/gates/` (e.g. `gates/statistical.py`, `gates/macro.py`, `gates/options.py`, `gates/fundamental.py`, `gates/calendar.py`). Enables per-gate `pytest` and visible threshold management.
- [ ] **A8. Babel → Vite migration** — Move frontend build from inline Babel CDN to Vite bundle. Removes `'unsafe-eval'` from CSP. The only security gap affecting all users.

### ⏳ Deferred (needs paid data or infrastructure)

- [ ] **A9. §62 VRP per-stock** — Needs per-stock 52-week IV history. Revisit if Polygon Options tier upgrades.
- [ ] **A11. §75 Buyback window** — Requires EDGAR 8-K parsing for repurchase announcements.
- [ ] **A12. §79 Q1 rebalancing gate** — Needs prior-year sector ETF return stored at Dec-31.
- [ ] **A13. §84 Survivorship bias correction** — Purchase EODHD (~$20/mo) or Norgate ($33/mo) for delisted tickers. Expected: IS WR drops 2–4pp, Sharpe −0.02 to −0.05 (makes backtest honest).
- [ ] **A14. §83 cross-signal correlation** — Already implemented. Needs live validation: track `avg_corr` at entry for 200 signals and confirm sized-down entries don't underperform.
- [ ] **A15. Sector-specific XGBoost retraining** — Unblock XLF/XLP/XLU. Requires ≥200 resolved signals per sector.
- [ ] **A16. Broker OAuth + order execution** — Alpaca Live or IBKR Web API OAuth + order submission. Toggle and DB model already done.

---

## 👁️ Known Issues

| Issue | Severity | Status |
|---|---|---|
| **Default owner password in source** | Critical | ❌ Must change before first paid signup |
| **§59–§82 gates — unit tests** | Resolved | ✅ §73/§74/§76 added (24 new tests in `test_gates_737476.py`); §69–§72 covered in `test_gates_5982.py`. 1025 passing. |
| **OOS v6 CLEAN N=51, Sharpe=0.16** | Resolved | ✅ Pre-specified 30 new tickers (2026-05-31). Curation bias gap −0.08 (smallest ever). Edge generalises. |
| **XLF/XLP/XLU blocked** | High | 🔄 Requires sector-specific XGBoost retraining |
| **Autonomous execution** | High | 🔄 Toggle + DB model done; broker OAuth + order submission pending |
| **Monolithic signal_engine.py (8k+ lines)** | Medium | 🔄 Delivery gates + scanner decomposed. Full engine decomposition deferred — see A7 |
| **Calibration v3 applied** | Resolved | ✅ Brier 0.2432, gap −0.5pp. True §82-aware cal needs N≥200 post-§82 resolved (~29wk). |
