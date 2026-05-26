# Signal.Trade — TODO

## 🔴 Pre-Launch Checklist

### Critical — must complete before anyone pays

- [ ] **1. Change owner password** — `backend/.env`: set `OWNER_PASSWORD=<16+ chars, mixed case, symbols>`. Default `ChangeMe123!` is committed to source. Risk: instant account takeover.
- [ ] **2. Deploy to public HTTPS URL** — Run `railway up` or `fly deploy`. Set `APP_URL=https://your-app.up.railway.app`. Risk: Stripe webhooks 404, OAuth callbacks broken, HTTPS-only cookies not sent.
- [x] **3. Migrate to PostgreSQL** — Local Homebrew PostgreSQL 16 running. 7,015+ signals, 8 users migrated. SQLite removed as runtime dependency.
- [ ] **4. Configure Stripe billing** — `STRIPE_SECRET_KEY` and price IDs set. Still needed: register webhook in Stripe Dashboard, copy `whsec_...` to `STRIPE_WEBHOOK_SECRET`. Risk: checkout completes but tier never activates.
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
- [ ] **13. Add Redis** — `railway add --plugin redis`. Risk: redundant API calls under concurrent load.
- [ ] **14. Upgrade SendGrid** — Essentials (~$20/mo) before daily signups + resets exceed 100 emails/day.

---

## 🎯 Strategic TODOs — Gen 2 Roadmap

### Pillar 0b — Entry Quality Research (§17, 2026-05-25)

> **Context:** Online research cross-validation identified 4 new backtest-testable gate ideas.
> Academic sources: Quantpedia ATR P70, Alpha Architect return-jump filter, Pagonidis IBS paper,
> Jegadeesh-Titman reversal timing (Review of Financial Studies Dec 2025), VIX slope research.
> All implemented in backtest + live engine. §17 runner ready at `scripts/run_section17.py`.

**Implemented 2026-05-25 (live engine + backtest framework):**
- [x] **ATR%rank ceiling ≤ 70 gate** — trending-panic entries (ATR > P70) blocked. Quantpedia: RSI MR signals in very-high-ATR regimes produce weaker bounces (stock still in breakdown, not dip). Gate added to `signal_engine.py` + `backtest_technicals.py` Gate 17b.
- [x] **Single-day return jump filter (< −6%)** — large single-day drops blocked as fundamental repricing. Alpha Architect: filtering return jumps tripled cumulative returns. Added to signal engine + backtest Gate 17c.
- [x] **VIX 3-day slope gate** — rising VIX (slope > +3 pts over 3 days, VIX > 16) blocks MR entry. Academic finding: MR bounces reliable only after VIX peaks and falls. `vix_3d_slope` added to `macro.py`; gate added to `signal_engine.py`.
- [x] **Entry delay T+2 (backtest only)** — test filling at T+2 open instead of T+1 to skip continuation morning. Available via `entry_delay_override=True` in `simulate_ticker()`.
- [x] **§17 research function** — `run_gate_research_v17()` in `signal_alpha_decomposition.py` sweeps all 4 gates vs §15f baseline. Now extended with §17e (IBS streak) and §17f (full stack).
- [x] **`run_section17.py` runner** — 25-30 min, strong 42-ticker universe only. Fixed `_r()` atr_min conflict; re-running at PID 98699.
- [x] **IBS + multi-day SMA20 confluence gate** — Pagonidis 2013: IBS<0.15 as sole MR trigger now requires ≥5 consecutive days below SMA20. Gate added to `signal_engine.py` + `backtest_technicals.py` Gate 17e (via `ibs_sma20_streak_override`). §17e sweep added to `run_gate_research_v17()` with N=3/5/7 streak variants.
- [x] **_SECTOR_MR_CONFIG confirmed-negative sectors blocked** — §16a data: Healthcare (Sharpe −0.17, WR 29.4%), Industrials (Sharpe −0.48, WR 28.6%), Real Estate (Sharpe −15) all set to `buy_thresh: 999` (blocks all MR entries). Energy calibrated to `hold_days: 5` (§16a WR 70%). Rationale message updated for blocked sectors.

**Pending (after §16 + §17 complete):**
- [ ] **Run §17 and read results** — Currently running at PID 98699 (`/tmp/decomp_§17.log`). Will produce §17a/b/c/e/f results on ATR ceiling, jump filter, entry delay, IBS streak.
- [ ] **Options flow confirmation gate** — Unusual Whales / FlowAlgo API (~$50-99/mo). Concurrent large call sweeps on oversold stocks = institutional accumulation confirmation. Estimated WR uplift to 85%+. See Pillar 0 for full spec.
- [ ] **Energy sub-sector split** — §16a showed Energy Sharpe 0.52, WR 70%. EOG in bad-ticker list. Isolate EOG; re-test XOM/CVX/COP/SLB as 4-ticker energy subgroup after §16 completes.
- [ ] **Update _SECTOR_MR_CONFIG for XLB/XLU/XLC/XLE** — after §16 full results, fill in Materials, Utilities, Telecom, and finalize Energy with sub-sector split data.

### Pillar 0 — Per-Trade Sharpe → 1.0 (Research Roadmap, 2026-05-24)

> **Context:** Alpha decomp v12 + §12 gate research found the OHLCV ceiling at per-trade Sharpe ~0.50.
> Annualized Sharpe = 1.00 first achieved via MR=0.1 + ATR%rank≥20 (N=137, §12e).
> Free items (ATR%rank default, adaptive exit, fundamental gate, revision gate) implemented 2026-05-24.
> Paid/structural items below push per-trade Sharpe from 0.38 toward 0.60-0.80.

**Free items (implemented 2026-05-24):**
- [x] **ATR%rank≥20 default in MR-only backtest** — matches live engine gate; ann. Sharpe 0.92→1.00
- [x] **Adaptive exit in backtest** — exits when RSI>55 or MACD+ or price>VWAP while profitable; captures bounce peak, reduces σ
- [x] **Fundamental value-trap gate (live engine)** — blocks BUY when revenue −20% YoY AND FCF yield <−5%; free yfinance data
- [x] **Near-earnings revision soft-gate (live engine)** — −4pp confidence haircut for 8-14d pre-earnings signals without positive analyst revision

**Paid / structural items:**

- [ ] **FREE: GEX + options flow as hard MR gate** — `services/options.py` already fetches `gex`, `pc_ratio`, `unusual_vol_ratio`, `otm_call_vol` per-ticker from yfinance (no paid API). Wire into `_assemble_signal()` MR gate chain: when MR BUY fires, add soft confidence bonus (+5pp) if `gex > 0 AND pc_ratio < 0.75` (dealer support + bullish flow), and apply −5pp haircut if `gex < 0 AND pc_ratio > 1.5 AND unusual_vol_ratio < 0.5` (no confirmation + puts dominating). Hard gate: if `pc_ratio > 2.0` (extreme put dominance), block regardless. Requires adding `opt_flow: dict` param to `_assemble_signal()`. **Next free implementation milestone.**

- [ ] **FREE: EPS revision hard gate (strengthen from soft)** — Current soft gate: −4pp confidence haircut for 8-14d pre-earnings without positive analyst revision. Upgrade: hard-block MR BUY in the 8-14d window when BOTH `revision_pts ≤ 0` AND options flow is neutral (no unusual call activity). Do NOT hard-block when either revision OR options confirms — §11c data shows these trades outperform when alt-data backs them. Gate: `if not has_pos_revision and not has_unusual_calls: action = "HOLD"`.

- [x] **Curated 150 ticker screener** — Script built at `scripts/screen_sp500_mr_candidates.py`. Screens S&P 500 via Wikipedia (sector, beta≥0.7, mktcap≥$10B), runs §17f backtest per candidate, outputs PASS/FAIL table + copy-paste list for `_STRONG` universe. Quality bar: WR≥55%, per-trade Sharpe≥0.35, N≥5. Fast mode: `--fast` (2006–2016, ~30min). Full run: ~90min. **Run after §16+§17 complete to avoid CPU contention.**

- [ ] **Options flow confirmation gate** — Subscribe to Unusual Whales API (~$50/mo) or Market Chameleon. Filter MR signals to those with rising call volume or falling put/call ratio (capitulation peak → confirmed MR setup). Live §11c data shows near-earnings signals outperform; options flow is the likely driver. Expected ΔSharpe: +0.15–0.25 per-trade. Gate: require `call_vol > 1.5× avg_call_vol OR pcr_slope < 0` at entry. **Highest-leverage single improvement available.**

- [ ] **Covered call overlay on live trades** — For every BUY signal with style=swing, sell a 1×ATR OTM covered call expiring 10-15 days out. Requires Level 2 options at broker. Premium collected (~1-2% of position) added to all outcomes: losses are floored (premium offsets part), wins are capped at target (already the exit). Math: E[r] +0.85pp, σ −0.5pp → per-trade Sharpe +0.15–0.20. Implementation: add `covered_call_premium_pct` field to signal output; display to user with call strike and expiry. **Requires broker options API or manual workflow.**

- [ ] **GEX (Gamma Exposure) support levels** — SpotGamma API (~$99/mo) provides per-ticker dealer GEX levels. When a stock's MR entry is at or below a major GEX support (positive GEX floor), dealer hedging mechanically creates a bounce. Filter: only enter when `price ≤ gex_support_level × 1.01`. Highest-conviction subset of MR setups. Expected ΔSharpe: +0.10 per-trade on gated subset.

- [ ] **Market-neutral beta hedge** — At entry, short 0.9× position value in SPY (beta-weighted). Removes market beta contribution to variance. Note: R²=0.010 means beta explains only 1% of per-trade variance; expected σ reduction is ~10%, not the 40-60% typical for high-beta strategies. More useful during confirmed bear regimes (SPY downtrend) where beta contribution to losses is real. Requires margin account.

- [ ] **Earnings surprise momentum filter** — EPS revision momentum (Finnhub free tier partially covers this; Refinitiv I/B/E/S for full coverage). Filter: only trade companies where analyst EPS estimates have been revised UP ≥2 times in the past 30 days. Hypothesis: institutional accumulation of oversold stock where analysts know beat is coming = strongest MR setup. Estimated WR uplift: +8–12pp on filtered subset. Free partial implementation: `revision_pts > 2` gate using existing Finnhub analyst_recs data (already in pipeline).

- [ ] **Run backtest with adaptive exit enabled** — New `adaptive` exit reason added to `simulate_ticker()`. Run `python scripts/backtest_technicals.py` and measure: (a) what % of exits are now `adaptive`, (b) ΔSharpe vs baseline, (c) ΔAvg return. Update §16 in Stats.md with results. **Run this before any other paid item — validates the free gain.**

- [ ] **Run backtest with ATR%rank≥20 default** — The default is now 20 in MR-only mode. The §12e result (N=137, Sharpe=0.38, Ann=1.00) was from the alpha-decomp 74-ticker universe. Run primary 30-ticker backtest and measure impact. Expected: N drops ~17%, per-trade Sharpe +0.06. Update §16 in Stats.md.

### Pillar 1 — Alpha Generation & Predictive Edge

- [x] **ML scoring model (XGBoost)** — 19-feature vector (confidence_bin removed); regularized (`reg_alpha=0.1`, `reg_lambda=2.0`, `gamma=0.3`). Weekly retrain Sunday 11am ET.
- [x] **Institutional quant analytics** — Sharpe, Sortino, Calmar, Omega, VaR/CVaR, t-stat, reliability diagram, phantom wins, stop-enforced WR, capture ratio. `scripts/calc_tbd_metrics.py`.
- [x] **Performance snapshot system** — `performance_snapshots` table; `--snapshot <tag>` CLI flag; diff API at `/api/admin/snapshots/diff/{a}/{b}`.
- [ ] **Monitor phantom win fix propagation** — run `validate_predictions.py` weekly and compare stop-enforced WR vs reported WR. Target: gap < 5pp within 4 weeks as new signals resolve at stop level.
- [ ] **Sector sub-model retraining** — XLF, XLP, XLU currently blocked (PF < 0.40x). Train sector-specific XGBoost classifiers to unblock these sectors.
- [ ] **Swing recalibration** — currently floored at 70%. Re-examine after next 200 swing-style resolved trades. Target: restore to 63% or lower if calibration improves.
- [ ] **LSTM for regime-conditioned confidence** — shallow LSTM on rolling 30-day windows (VIX, SPY ret, yield curve, breadth) to predict regime transitions 3–5 days ahead.
- [ ] **Feature importance audit** — inspect SHAP values after next XGBoost retrain; remove/invert negative-EV blocks.
- [x] **Walk-forward OOS validation** — `GET /api/signals/backtest/oos` added.

### Pillar 2 — Data Architecture & Reliability

- [x] **Move hot-path market data off yfinance** — Polygon/Massive batch helpers called first; yfinance is fallback only.
- [x] **SQLite removed** — PostgreSQL is the only runtime DB. SQLite retained for test suite only.
- [x] **Redis cache + lock layer** — `services/redis_cache.py`. Backed by Redis when `REDIS_URL` set.
- [x] **Data quality monitoring** — Telegram alert on ≥5 consecutive null fetches per ticker.
- [x] **Fear & Greed API fixed** — CNN HTTP 418 bot detection resolved with full browser headers. F&G live at 62.9 (Greed).
- [ ] **Ditch Playwright/Finviz scraping** — Replace fallback with Benzinga Pro or Polygon news.
- [ ] **Commercial data feed evaluation** — Polygon Advanced ($199/mo) or Benzinga Pro ($49/mo).

### Pillar 3 — UI/UX

- [x] **Custom screener builder (backend)** — 8 filter fields, 8 operators. Frontend UI pending.
- [x] **DOM feed pagination hardening** — suppressed rows paginated 20 at a time.
- [ ] **Chart drawing tools** — annotation layer above LightweightCharts (trend lines, rectangles). Most-requested feature.
- [ ] **Alert customisation UI** — per-ticker alert rules: "notify me when NVDA BUY confidence > 72%".
- [ ] **Mobile-responsive main app** — breakpoint at 768px, single-column view.

### Pillar 4 — Execution & Delivery Mechanics

- [x] **Delivery gates extracted to `services/delivery_gates.py`** — independently testable; reusable for broker execution path.
- [x] **Signal delivery SLA monitoring** — `scan_cycle_started_at` used for SLA (was using `created_at`, causing false 424-min alerts).
- [ ] **Telegram broadcast channel** — enable `TELEGRAM_BROADCAST_CHANNEL_ID` before marketing push. Required at >50 subscribers.
- [ ] **OAuth broker execution (live trading)** — OAuth flow for Alpaca Live or IBKR Web API. Auto-execute high-confidence signals.
- [ ] **Autonomous execution mode** — per-user toggle to auto-trade signals above X% confidence.
- [ ] **Webhook outbound improvements** — two-way confirmation: POST fill price to `/api/webhooks/execution-confirm`.

### Pillar 5 — Codebase Maintainability & Scalability

- [x] **Migrate to PostgreSQL** — complete. SQLite removed as runtime dependency.
- [x] **Delivery gates decoupled** — `services/delivery_gates.py` extracted from scanner.
- [x] **signal_engine.py decomposition** — `generate_signal()` split into fetch, score, assemble.
- [x] **CI/CD with accuracy regression gate** — syntax check, smoke tests, pytest, accuracy gate, pip-audit.
- [x] **Dependency audit and hardening** — pinned versions; pip-audit in CI.
- [ ] **Monolithic `run_scan` decoupling** — refactor `services/scanner.py` to decouple data fetching, scoring, delivery, and telemetry into discrete services.

---

## 👁️ Known Issues

| Issue | Severity | Status / Next Action |
|---|---|---|
| **Phantom wins (42.2% vs 58.8% WR)** | Critical | ✅ Fix deployed 2026-05-17. Monitor weekly until gap < 5pp. |
| **XLF/XLP/XLU blocked** | High | 🔄 Requires sector-specific retraining |
| **Intraday WR 34.8%, PF 0.73x** | High | 🔄 At ≥68% conf floor; improve signal quality |
| **Confidence gap +11pp overconfident** | High | 🔄 Calibration tightened; monitor next training run |
| **Default owner password in source** | Critical | ❌ Must change before first paid signup |
| **Monolithic `run_scan`** | Medium | 🔄 Delivery gates done; full decomposition pending |
| **Chart drawing tools missing** | High | ❌ Not implemented |
| **Autonomous execution** | Critical | ❌ Not started |
| **Dividend ex-date trap** | Medium | ❌ No blackout around ex-date |
| **Post-earnings IV crush** | Medium | ❌ No IV Rank flagging |

---

## ✅ Recently Completed (v5.8)

- [x] Phantom win fix — stop_monitor locks outcome_pct at exit level; validate_predictions skips calendar fill for closed positions
- [x] ATR stops widened for position style (3.0–3.5× from 2.0–2.5×)
- [x] Sector gate — XLF/XLP/XLU blocked from delivery (PF < 0.40x)
- [x] Delivery gates extracted to `services/delivery_gates.py`
- [x] XGBoost regularization — 19 features, reg_alpha, reg_lambda, gamma
- [x] Calibration tightened — blend 0.97, N_FULL 15
- [x] Performance snapshot system — DB table, CLI flag, admin API, weekly auto-snapshot, diff endpoint
- [x] Institutional quant metrics — Sharpe (sqrt(252), single application), Sortino (semi-dev from 0%, divisor=n), phantom wins, stop-enforced WR, capture ratio, t-stat
- [x] Fear & Greed CNN bot detection fixed — full browser headers
- [x] SLA false positive fix — latency measured from scan_cycle_started_at
- [x] SQLite removed as runtime dependency
- [x] 662 tests passing, 0 failed
