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
