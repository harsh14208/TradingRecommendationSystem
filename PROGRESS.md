# Signal.Trade — Development Progress

> **Version: v5.6** · Updated: 2026-05-17 · Server: `uvicorn main:app --host 0.0.0.0 --port 8000`
> ~210 tickers (incl. 52 leveraged ETFs) · 70+ signal blocks · 113 API endpoints · Max confidence: 72% (empirically calibrated)
> **Data: Polygon.io (OHLCV + indicators + news + financials) · yfinance (fallback) · Massive WebSocket (dark pool) · FRED (macro + credit spreads)**
> **Database: PostgreSQL 16 (Homebrew local) · 7,015 signals · 8 users**
> **Tests: 597 passed, 0 failed (all test suites green after all refactoring)**


What's Working
Core platform — fully functional:

Server — FastAPI on port 8000, all routers registered, PostgreSQL connected
Signal engine — 7,015 signals in DB, scanner actively running (60s interval)
Telegram delivery — bot @signal1420bot verified live, auto-send ON, 539 sends logged
Authentication — JWT login/register/refresh, owner account, tier gating (500 on login fixed)
Market data — Fear & Greed, macro context (FRED), HMM regime model, breadth, AAII sentiment
Backtesting — /api/signals/backtest and OOS endpoint both returning 200
Watchlist — 191 tickers in DB, CRUD working
Screener — custom filter presets, preview endpoint, all working
Calibration — Platt calibration file + factor weights file present
Signal delivery log — /api/delivery/log live
Database — PostgreSQL 16 (local Homebrew); full SQLite→PG migration complete; all sequences correct
Legal — TOS updated: Delaware governing law, publisher exemption (§80b-2), no chargeback waiver
APIs with keys configured:

Service	Key	Status
Finnhub	✓ set	Live price data
Alpaca	✓ set	Paper trading + market data
FRED	✓ set	Macro indicators
Massive API	✓ set	Dark pool / options flow
Stripe	✓ set (test keys)	sk_test_... + price IDs in .env; webhook secret still needed
Waiting for Setup
Blocking for launch (users can't pay you):

What	Missing	Impact
Stripe webhook secret	STRIPE_WEBHOOK_SECRET=whsec_...	Subscriptions never activate after payment — checkout completes but tier stays Free
Email / SMTP	SMTP_HOST, SMTP_PASSWORD	No email verification on register, no password reset, no weekly digest
Production DATABASE_URL	Replace local URL with Railway/Fly managed Postgres	Local Homebrew DB not accessible from deployed server
Optional but adds real value:

What	Missing	Impact
XGBoost ML	brew install libomp not done + no trained model	Confidence adjustment from ML skipped; signals still work with Platt calibration
Redis	REDIS_URL empty	Cache falls back to in-memory dict — fine for single process, breaks under multi-worker prod
Web Push (VAPID)	VAPID_PRIVATE_KEY empty	In-app push notifications silently disabled
Polygon.io	POLYGON_API_KEY empty	Using Finnhub fallback; some indicator endpoints degraded
Unusual Whales	UNUSUAL_WHALES_API_KEY empty	Dark pool data missing from signals
Google OAuth	GOOGLE_CLIENT_ID/SECRET empty	"Sign in with Google" button non-functional
Discord OAuth	DISCORD_CLIENT_ID/SECRET empty	Discord login non-functional
Infrastructure (pre-production):

What	Current State	What's Needed
Database	PostgreSQL 16 (local Homebrew) ✅	Set DATABASE_URL to managed Postgres on deploy (Railway/Fly auto-inject)
Docker Compose	postgres:16-alpine service bundled	`docker compose up` starts both DB + backend; named volume for persistence
Priority order before launch: STRIPE_WEBHOOK_SECRET → SMTP → Deploy to HTTPS with managed Postgres URL.


---

## 📐 Codebase Size — v5.5 (2026-05-16)

### Total: ~39,400 lines across 130 project files

| Layer | Files | Lines | Notes |
|-------|-------|-------|-------|
| **Backend Python** | 90 | 24,957 | Services, routers, models, tests (+490 lines this session) |
| **Frontend JSX** | 13 | 7,441 | Dashboard, mobile, site, design |
| **CSS** | 3 | 1,285 | `styles.css` (main), `site.css`, `mobile.css` |
| **HTML pages** | 14 | 2,627 | Login, signup, marketing, legal |
| **JS workers** | 2 | ~150 | `sw.js`, `monte_carlo_worker.js` |
| **Docs** | 3 | 2,105 | `PROGRESS.md`, `HOWTO.md`, `README.md` |
| **Config/infra** | 5 | ~200 | `railway.toml`, `fly.toml`, `docker-compose.yml`, `Dockerfile`, `Procfile` |

### Backend breakdown

| Directory | Files | Lines | What's inside |
|-----------|-------|-------|---------------|
| `backend/services/` | 59 | 17,373 | Signal engine, scanner, all data fetchers |
| `backend/routers/` | 21 | 5,304 | All 113 API endpoints |
| `backend/` (root) | 5 | 1,593 | `main.py`, `database.py`, `models.py`, `config.py`, `auth_svc.py` |
| `backend/tests/` | 4 | 174 | 7 test functions |

### Top 10 largest files

| File | Lines | Purpose |
|------|-------|---------|
| `backend/services/signal_engine.py` | 3,950 | Signal generation — 70+ scoring blocks, fetch + assemble |
| `backend/routers/signals.py` | 1,636 | Signal CRUD, backtest, calibration, OOS, factor mining, alpha-decay |
| `backend/services/scanner.py` | 1,361 | Full scan loop — 11 steps, fan-out, SLA tracking |
| `app.jsx` | 1,424 | App component (DEFAULTS, App, ReactDOM) |
| `app.analysis.jsx` | 1,288 | WhyNow, PositionCalc, Simulator, MarketOverview, SectorView, CalendarView |
| `backend/main.py` | 878 | FastAPI app, lifespan, scheduled jobs |
| `app.modals.jsx` | 882 | AccountModal, PriceAlertModal, WatchlistView, PricingView, TweaksPanel |
| `backend/services/signal_ml.py` | 552 | XGBoost ML model — train, predict, weekly retrain |
| `backend/routers/auth.py` | 520 | Register, login, refresh, OAuth, GDPR erasure |
| `app.views.jsx` | 715 | SourcesView, RulesView, HistoryView, BacktestView, SortableTable |

### Frontend module split (app.jsx was 5,311 lines, now 8 files)

| File | Lines | Components |
|------|-------|------------|
| `app.auth.jsx` | 62 | `authFetch`, `apiFetch`, token helpers |
| `app.constants.jsx` | 123 | `GLOSSARY` (35 terms), `TIER_ORDER`, ET helpers |
| `app.ui.jsx` | 420 | `Icon`, `Tip`, `InfoPop`, `Chart`, `CompareChart`, `AdSlot`, `Sparkline` |
| `app.signal.jsx` | 193 | `SignalRow`, `TelegramPane`, `NoteEditor`, `FilterChips` |
| `app.views.jsx` | 715 | `SourcesView`, `RulesView`, `HistoryView`, `BacktestView`, `SortableTable` |
| `app.modals.jsx` | 882 | `AccountModal`, `PriceAlertModal`, `WatchlistView`, `PricingView`, `TweaksPanel` |
| `app.analysis.jsx` | 1,288 | `WhyNow`, `PositionCalc`, `SimulatedReturnsPanel`, `PaperView`, overlays |
| `app.jsx` | 1,424 | `DEFAULTS`, `App` component, `ReactDOM.createRoot` |

### Signal engine structure

| Layer | Lines | What it contains |
|-------|-------|-----------------|
| `_fetch_ticker_data()` | ~60 | Async data fetch — both prefetched and fresh paths |
| Scoring body (in `generate_signal`) | ~2,850 | 97 scoring blocks across 11 families |
| `_assemble_signal()` | ~535 | Risk gates, confidence caps, calibration, XGBoost adj, return dict |
| `scan_all()` | ~130 | Semaphore(5) parallelism, sector peer confirmation |

### API surface

| Category | Endpoints | Examples |
|----------|-----------|---------|
| Auth | 18 | register, login, refresh, OAuth, GDPR |
| Signals | 22 | list, history, backtest, OOS, factor mining, ML, alpha-decay |
| Market | 8 | context, calendar, sectors, overview, regime |
| Paper trading | 9 | account, positions, orders, volatility-target |
| Admin | 10 | stats, users, rate-limits, delivery-sla, digest |
| Billing | 5 | plans, checkout, portal, status, webhook |
| Screener | 5 | list, create, delete, run, preview |
| Watchlist | 3 | list, add, remove |
| Misc | 13 | quotes, chart, sources, alerts, settings, health, WebSocket |
| **Total** | **113** | |

### Live database stats (2026-05-10)

| Metric | Value |
|--------|-------|
| Watchlist tickers | 164 |
| Total signals generated | 6,872 |
| Signals sent to Telegram | 529 |
| Resolved signals (outcome_pct filled) | 448 |
| 7-day win rate | 64.1% |
| XGBoost training samples | 448 (grows with each backfill) |

---

## 🏅 Quality Ratings — v5.5

| Aspect | Score | Grade | Notes |
|--------|-------|-------|-------|
| **Signal Accuracy** | 8.2/10 | A− | 57.7% win rate (7d); 63.2% at 14d (now primary). Confidence ceiling lowered 84%→72% based on empirical calibration. Defensive-ticker gate, ETF bypass, validation-driven fixes. |
| **Signal Engine** | 8.9/10 | A | 70+ blocks, 11 scoring families. Added: cross-sectional universe ranking, analyst revision momentum, FRED credit spreads, leveraged ETF handling (52 tickers), alpha decay endpoint. |
| **Frontend UX** | 8.2/10 | B+ | Dark theme, keyboard shortcuts, real-time WebSocket, predictive intervals, Monte Carlo simulator. Split into 8 modules (5311 → 1424 lines). |
| **Code Maintainability** | 7.5/10 | B | app.jsx split across 8 files. signal_engine.py oscillator/MA/MACD scoring in `signal_scoring.py`. signal_engine body still large (~3,950 lines). |
| **Input Validation** | 8.0/10 | B+ | Email format, password bounds, name length, ticker regex, price range in all routers. Frontend: WatchlistView, PriceAlertModal, AccountModal, RulesView. |
| **Security** | 7.0/10 | B− | JWT + HTTP-only cookies, rate limiting, bcrypt, data policy middleware. Risk: default owner password in source (critical). |
| **Backend Architecture** | 8.3/10 | A− | FastAPI + routers + services + async SQLAlchemy + Pydantic v2. Scanner→engine→workers pipeline. PostgreSQL (asyncpg). |
| **Data Pipeline** | 8.9/10 | A | Polygon.io, yfinance, Finnhub, FRED (incl. BAMLH0A0HYM2 HY spread + BAMLC0A0CM IG spread), Alpaca, dark pool, Benzinga, EDGAR, 13F. Concurrent with semaphores + circuit breakers + Platt calibration. |
| **Deployment Readiness** | 6.5/10 | C+ | railway.toml + fly.toml + Docker ready. Blockers: owner password unchanged, SMTP unset, Stripe unset, not deployed. |
| **Documentation** | 8.5/10 | A− | PROGRESS.md, HOWTO.md, README.md, .env.example all complete and updated to v5.5. |
| **Test Coverage** | 5.5/10 | C+ | Backend tests present, coverage unknown. No frontend tests. No signal accuracy regression CI. |
| **Bug Count** | 8.5/10 | A− | v5.5: intraday restored, confidence overconfidence corrected, 16-ticker defensive gate, ETF fundamentals bypass, calibration tightened. |

**Overall: 8.0 / 10 — A−** · Strongest: data pipeline, engine sophistication, backend architecture. Priority: deploy to HTTPS, change owner password, add CI.

> **External critique score: 6.7 / 10** — "Exceptional indie-hacker project, but a Gen 1 alert service masquerading as a quant firm." To cross from a $150k/yr side hustle to $5M/yr SaaS: refactor the codebase, ditch the scrapers, add agentic execution.

---

## 🎯 Strategic TODOs (Gen 2 Roadmap)

Derived from external 5-pillar critique. Ordered by impact within each pillar.

### Pillar 1 — Alpha Generation & Predictive Edge (rated 7.5/10)

> **Core gap:** The engine is a deterministic `if/elif` state machine with hardcoded point weights. True institutional models use ML to discover non-linear relationships dynamically.

- [x] **ML scoring model (XGBoost)** — `services/signal_ml.py` built. 20-feature vector; XGBoost binary classifier with temporal 70/30 OOS split; weekly retrain job Sunday 11am ET; multiplicative confidence adjustment ±25% clamped to 84% ceiling; graceful no-op if model not yet trained. `GET /api/ml/status` + `POST /api/ml/train` (owner-only). Integrated into signal_engine.py after Platt calibration.
- [ ] **LSTM for regime-conditioned confidence** — Train a shallow LSTM on rolling 30-day windows of (VIX, SPY ret, yield curve, breadth) to predict regime transitions 3–5 days ahead. Feed the regime probability directly into the HMM multiplier as a second signal. Particularly valuable for catching regime flips that the static HMM misses.
- [x] **Remove all Intraday signals** — `signal_engine.py`: `_is_intraday` no longer maps to `style="intraday"`. All previously-intraday signals now classified as `swing`, giving the entry signal the 3–7 day window where the 64.1% win rate actually exists. Scanner's dead intraday suppression block removed. Expected: overall win rate improves as the 44.5% intraday noise is retired.
- [ ] **Feature importance audit** — After first XGBoost fit, inspect SHAP values to identify which of the 65 blocks contribute negative expected value. Remove or invert those blocks. Suspected: most macro blocks add noise for single-stock signals; options flow likely dominates.
- [x] **Walk-forward OOS validation** — `GET /api/signals/backtest/oos` added to `routers/signals.py`. Chronological 60/40 train/test split; per-window OOS win rate, avg return, Sharpe (sqrt(252) annualised); up to 6 rolling 30-day windows; 10-min TTL cache.

### Pillar 2 — Data Architecture & Reliability (rated 7.0/10)

> **Core gap:** The pipeline is a house of cards built on free tiers. yfinance scraping and Playwright/Chromium are unacceptable for a $20/mo paid product.

- [ ] **Ditch Playwright/Finviz scraping** — `news_scraper.py` uses Playwright Chromium to scrape Finviz as a fallback. This is legally fragile and will break silently when Finviz updates its DOM. Replace with Benzinga Pro API ($49/mo) or Polygon news (already integrated on free tier). Remove the `playwright` dependency entirely from `requirements.txt`.
- [ ] **Eliminate yfinance as a production dependency** — yfinance scrapes Yahoo Finance undocumented endpoints. A single IP ban breaks the entire fallback pipeline. Audit every `yfinance` call in the codebase; replace each with Polygon (preferred), Alpha Vantage, or Tiingo. Target: yfinance used for development/testing only, never for production data fetches on the hot path.
- [ ] **Commercial data feed evaluation** — Budget $200–500/month for a redistribution-licensed data source. Evaluate: Polygon Advanced ($199/mo, unlimited minute bars + real-time snapshots), Benzinga Pro ($49/mo, licensed news), Tiingo ($10/mo, OHLCV + news). Unlocks legal redistribution of data to subscribers.
- [x] **Redis cache layer for hot data** — `services/redis_cache.py` created. `cache_get`/`cache_set` backed by Redis when `REDIS_URL` is set, in-memory dict otherwise. `macro.py` and `fear_greed.py` migrated to shared cache (1h TTL). `cache_stats()` exposed in rate-limits endpoint.
- [x] **Data quality monitoring** — `_check_data_quality(histories, settings)` + `_data_quality` module-level counter in `scanner.py`. Alerts via Telegram on transition to ≥5 consecutive null fetches per ticker. Resets on valid data.

### Pillar 3 — UI/UX (rated 8.5/10)

> **Core gap:** Read-only rigid dashboard. Users cannot customise screeners, draw on charts, or override signal logic.

- [x] **Custom screener builder (backend)** — `routers/screener.py` built. Endpoints: `GET /api/screener` (list), `POST /api/screener` (create/replace), `DELETE /api/screener/{name}`, `GET /api/screener/{name}/run` (evaluate against live signals), `POST /api/screener/preview` (test without saving). Supports 8 filter fields (confidence, sentiment, action, style, rr, n_sources, ticker, has_source) and 8 operators (gt/gte/lt/lte/eq/neq/contains/in). Presets stored in `app_settings["screeners"]`. Frontend UI still pending.
- [ ] **Chart drawing tools** — Add a lightweight annotation layer above the LightweightCharts canvas: horizontal lines, trend lines, rectangle boxes. Persist annotations per ticker in `localStorage`. This is the single most-requested feature among active traders and directly addresses the TradingView comparison.
- [ ] **DOM virtualisation for signal feed** — The current 30-card pagination (`FEED_PAGE=30`) mitigates this but doesn't fix it. Implement `react-window` (FixedSizeList) or `react-virtuoso` for the feed so only visible cards are in the DOM. Eliminates scroll jank at 50+ signals.
- [ ] **Alert customisation UI** — Users currently set one global confidence threshold. Add per-ticker alert rules: "notify me when NVDA BUY confidence > 72%" distinct from the feed threshold. Expose via `POST /api/alerts/rules` and surface in Account Settings.
- [ ] **Mobile-responsive main app** — The app.jsx layout is a fixed three-pane desktop grid. Add a breakpoint at 768px that collapses to a single-column view: feed → tap signal → detail overlay → back. The mobile.jsx mock exists; wire it to the real backend.

### Pillar 4 — Execution & Delivery Mechanics (rated 6.0/10)

> **Core gap:** Signal.Trade is currently an alert service. Gen 2 means autonomous execution. Telegram 1-to-1 DMs will break at 50+ users.

- [ ] **Telegram broadcast channel (immediate)** — `TELEGRAM_BROADCAST_CHANNEL_ID` env var is already wired but not deployed. At >50 subscribers, 1-to-1 DM loops will hit the 30 msg/sec Telegram rate limit. Enabling the broadcast channel collapses N DMs into 1 API call. **This is a 5-minute fix that must happen before any marketing push.**
- [ ] **OAuth broker execution (live trading)** — Add an OAuth flow for Alpaca Live (and optionally Interactive Brokers via IBKR Web API). When a user connects their live broker account, high-confidence signals (≥75%) are executed automatically with the user's pre-configured position sizing (already computed in PositionCalc). This transforms Signal.Trade from an alert service into an execution platform.
- [ ] **Autonomous execution mode** — Add a per-user toggle: "Auto-trade signals above X% confidence with Y% portfolio risk". When enabled, `_maybe_send()` also calls `POST /api/paper/orders` (or live broker) automatically, without requiring the user to be online. This is the core Gen 2 feature — trading runs 24/7 without the user.
- [ ] **Webhook outbound improvements** — The existing webhook is one-way (signal → user's URL). Add a two-way confirmation: after the user's system executes, they POST back to `/api/webhooks/execution-confirm` with fill price and quantity. This closes the feedback loop and enables accurate P&L tracking without requiring broker OAuth.
- [x] **Signal delivery SLA monitoring** — `_maybe_send()` in `scanner.py` now tracks `(sent_at - created_at)` latency; logs warning and fires async Telegram alert to owner when >5 minutes. `GET /api/admin/delivery-sla` returns p50/p95/p99 latency percentiles and 24h breach count.

### Pillar 5 — Codebase Maintainability & Scalability (rated 4.5/10)

> **Core gap:** SQLite + a 3500-line procedural signal_engine will become catastrophic at scale. The asyncio event loop has hidden sync blocking.

- [x] **Migrate to PostgreSQL (guardrails done)** — `database.py` already routes to asyncpg when `DATABASE_URL=postgresql://...` is set. `scripts/check_postgres.py` validates connection, asyncpg install, and schema compatibility. `main.py` logs a warning when SQLite is detected in a production (`https://`) deployment. **One-step activation: `railway add --plugin postgresql`, set `DATABASE_URL`, restart.**
- [x] **signal_engine.py decomposition** — `generate_signal()` split into three layers: (1) `_fetch_ticker_data()` — async data fetch for both prefetched and fresh paths, (2) 3000-line scoring body — unchanged, uses `signal_scoring.py` helpers, (3) `_assemble_signal()` — all risk gates, confidence adjustments, Platt calibration, XGBoost adjustment, plain-English, and return dict. `generate_signal()` itself reduced to orchestration logic only (fetch → score → assemble). 8 clean top-level functions; 0 syntax errors.
- [x] **Sync blocking audit + fixes** — All 8 `asyncio.get_event_loop()` calls replaced with `asyncio.get_running_loop()` across `market_data.py`, `breadth.py`, `earnings.py`, `google_trends.py`, `fundamentals.py`, `news.py`, `options.py`. `local_llm.py`: two `urllib.request.urlopen` availability checks replaced with non-blocking TCP socket probes (2s timeout, no HTTP round-trip). Zero blocking I/O remaining in the event loop thread.
- [x] **CI/CD with accuracy regression gate** — `.github/workflows/ci.yml` created. Steps: Python 3.11, pip cache, syntax check all `.py`, import smoke tests, pytest, accuracy gate (skips if <30 resolved signals), non-blocking `pip-audit` security scan.
- [x] **Analytics pre-computation** — `_precompute_analytics()` fires as a fire-and-forget task at end of every scan cycle (Step 11). Pre-computes backtest summary (win rate, avg return, by-action breakdown) via single GROUP BY query; stores in `redis_cache` with 5-min TTL. `GET /api/signals/backtest` checks the pre-computed cache first for unfiltered requests — eliminates the expensive on-demand GROUP BY under concurrent load.
- [x] **Dependency audit and hardening** — `requirements.txt` updated: `xgboost>=2.0.0`, `scikit-learn>=1.4.0`, `pip-audit>=2.7.0` added. `pip-audit` included in CI workflow. All existing version pins preserved.

---

## 🔴 Pre-Launch Checklist (everything needed before first paid signup)

Items are ordered by risk severity. Each row shows: what to do, the exact command or config, and what breaks without it.

### 🔴 CRITICAL — Must complete before anyone pays

- [ ] **1. Change owner password** — `backend/.env`: set `OWNER_PASSWORD=<16+ chars, mixed case, symbols>`. Current default `ChangeMe123!` is committed to source and readable by anyone with repo access. **Risk: instant account takeover.**

- [ ] **2. Deploy to public HTTPS URL** — Run `railway up` (preferred) or `fly deploy`. Set `APP_URL=https://your-app.up.railway.app`. **Risk: Stripe webhooks 404, Telegram webhook fails, OAuth callbacks broken, HTTPS-only refresh cookies not sent.**
  ```bash
  npm install -g @railway/cli && railway login && railway up
  railway variables set APP_URL=https://your-app.up.railway.app
  ```

- [x] **3. Migrate to PostgreSQL** ✅ — Local Homebrew PostgreSQL 16 running. Full migration complete: 7,015 signals, 8 users, all 10 tables. `backend/scripts/migrate_sqlite_to_postgres.py` available for future re-runs. **For deploy:** Railway/Fly auto-inject `DATABASE_URL` — no extra steps needed. `database.py` now loads `.env` at import time so the URL is always picked up correctly.

- [ ] **4. Configure Stripe billing** — `STRIPE_SECRET_KEY` and price IDs are set (test keys). Still needed: register webhook in Stripe Dashboard, copy `whsec_...` to `STRIPE_WEBHOOK_SECRET`. **Risk: checkout completes but tier never activates — users pay but stay on Free plan.**
  ```bash
  # Webhook endpoint: https://your-app.railway.app/api/billing/webhook
  # Events: checkout.session.completed, customer.subscription.updated,
  #          customer.subscription.deleted, invoice.payment_failed
  # Copy whsec_... to backend/.env: STRIPE_WEBHOOK_SECRET=whsec_...
  # For live: swap sk_test_... → sk_live_... and update price IDs
  ```

- [ ] **5. Register Telegram webhook** — After HTTPS deploy, run once:
  ```bash
  curl -X POST https://your-app.up.railway.app/api/telegram/set-webhook
  # Or: Account Settings → Admin → "Register TG Webhook"
  ```
  **Risk: subscribers cannot link Telegram via `/start <code>`. Only the owner fallback DM works.**

### 🟠 HIGH IMPACT — Do within the first week

- [ ] **6. Configure SMTP (email)** — Add to `backend/.env`:
  ```
  SMTP_HOST=smtp.sendgrid.net
  SMTP_PORT=587
  SMTP_USER=apikey
  SMTP_PASSWORD=SG.your_key
  SMTP_FROM=noreply@yourdomain.com
  SMTP_FROM_NAME=Signal.Trade
  ```
  Free SendGrid account = 100 emails/day. **Risk: no email verification on signup (users are auto-verified without SMTP — acceptable in dev, not production). No password reset emails. No weekly digest emails.**

- [ ] **7. Enable Telegram broadcast channel** — Create a private Telegram channel, make your bot admin, get the channel ID (`-100...`), add to `.env`:
  ```
  TELEGRAM_BROADCAST_CHANNEL_ID=-1001234567890
  ```
  **Risk: at >50 subscribers, 1-to-1 DM loop hits Telegram's 30 msg/sec rate limit — last user waits 3+ minutes for their signal.**

- [ ] **8. Train XGBoost ML model** — After accumulating ≥50 resolved signals (auto-happens within a few days of running):
  ```bash
  curl -X POST https://your-app.../api/ml/train -H "Authorization: Bearer <token>"
  ```
  Or it retrains automatically each Sunday 11am ET. **Risk: no impact on correctness (graceful fallback), but you miss +5–8pp expected win rate improvement from ML confidence adjustment.**

- [ ] **9. Configure Google OAuth** (optional but reduces friction significantly):
  ```
  GOOGLE_CLIENT_ID=...apps.googleusercontent.com
  GOOGLE_CLIENT_SECRET=...
  ```
  Redirect URI to register: `https://your-app.up.railway.app/api/auth/google/callback`. **Risk: no Google Sign-In button — users must register with email/password.**

### 🟡 BEFORE MARKETING / SCALE

- [ ] **10. Configure VAPID web push** — Generate keys once and store permanently:
  ```bash
  cd backend && python3 -c "
  from py_vapid import Vapid; v = Vapid(); v.generate_keys()
  print('VAPID_PRIVATE_KEY=' + v.private_pem().decode().replace('\n','\\\\n'))
  "
  # Add output + VAPID_SUBJECT=mailto:admin@yourdomain.com to .env
  ```
  **Risk: no browser push notifications (signals only via Telegram).**

- [ ] **11. Set up Cloudflare CDN** — Point DNS to Railway/Fly, enable "Cache Everything" for static assets, bypass for `/api/*`. **Risk: slower global load times, no DDoS protection.**

- [ ] **12. Google AdSense** — Apply at adsense.google.com (requires live domain). Once approved, add script tag to HTML head and replace slot IDs in `app.ui.jsx`. **Risk: free tier shows upgrade CTA instead of ads — no ad revenue.**

- [ ] **13. Add Redis** — `railway add --plugin redis` → Railway auto-sets `REDIS_URL` → restart. **Risk: each worker re-fetches macro/VIX data independently — redundant API calls under concurrent load. Low risk at <100 users.**

- [ ] **14. Upgrade SendGrid** — Move to Essentials (~$20/mo) before daily signups + resets exceed 100 emails/day. Monitor via SendGrid dashboard. **Risk: silent email delivery failure — users can't verify email or reset password.**

---

## 🔧 Feature Enable Checklist

> **Active data sources** (no action needed): Signal engine ✅ · Polygon.io OHLCV/indicators/news/financials ✅ · Dark pool (Massive WebSocket) ✅ · Finnhub ✅ · FRED macro ✅ · Alpaca paper trading ✅ · Telegram owner DM ✅ · JWT auth ✅

### 🟠 High Impact

| # | Feature | `.env` key | Time | Unlocks |
|---|---------|-----------|------|---------|
| 5 | SendGrid SMTP | `SMTP_HOST/PORT/USER/PASSWORD/FROM` | 10 min | Email verification, password reset, weekly digest |
| 6 | Google OAuth | `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` | 10 min | One-click Google signup |
| 7 | Discord OAuth | `DISCORD_CLIENT_ID` + `DISCORD_CLIENT_SECRET` | 10 min | Discord signup + signal delivery |
| 8 | Web Push (VAPID) | `VAPID_PRIVATE_KEY` + `VAPID_SUBJECT` | 5 min | Browser push for ≥70% signals |

**VAPID key generation:**
```bash
cd backend && python3 -c "
from py_vapid import Vapid; v = Vapid(); v.generate_keys()
print('VAPID_PRIVATE_KEY=' + v.private_pem().decode().replace('\n','\\\\n'))
"
```

### 🟡 Optional Scale & Monetisation

| # | Feature | `.env` key | Time | Unlocks |
|---|---------|-----------|------|---------|
| 9 | Telegram broadcast channel | `TELEGRAM_BROADCAST_CHANNEL_ID` | 5 min | 1 API call for all subscribers (required >50 users) |
| 10 | Google AdSense | Add script tag to HTML, update `AdSlot` slot IDs | 1–4 weeks | Ad revenue from free tier ($0.50–$2 CPM) |
| 11 | PostgreSQL | `DATABASE_URL=postgresql://...` | 5 min via Railway | No `SQLITE_BUSY` errors, row-level security |
| 12 | Cloudflare CDN | Point DNS to Railway/Fly | 15 min | Global CDN, DDoS protection |

**Deploy commands:**
```bash
# Railway (recommended)
npm install -g @railway/cli && railway login && railway up

# Fly.io
brew install flyctl && fly auth login && fly launch --no-deploy && fly deploy
```

---

## ✅ Implemented

### v5.6 (2026-05-17) — Signal Lifecycle, Calibration, Live UI & Send Quality Gates

**Signal lifecycle (closed the biggest gap — signals now have a beginning, middle, and end):**
- [x] **`services/stop_monitor.py` (new)** — intraday stop/target monitor runs every 30 min Mon–Fri 09:30–16:15 ET. Fetches live prices for all active sent signals. Marks `hit_stop`, `hit_target`, `exit_type` in DB. Fires Telegram: "✅ TARGET HIT: AMD BUY — price $183.50 hit target $183.00. +4.4%" or "⛔ STOP HIT: META BUY — price $417.50 breached stop $428.00. -2.4%". Deactivates signal. Previously signals stayed "active" for 7 days regardless of what actually happened.
- [x] **`_nightly_outcome_resolution()` in main.py** — scheduled 2am ET daily. Calls `resolve_outcomes()` + `resolve_mae_mfe()` + `run_calibration()` automatically. Previously calibration.json went stale because the resolve script required a manual run.
- [x] **`_intraday_stop_monitor()` in main.py** — registers stop monitor as a background task at startup. Both jobs registered in `lifespan()` via `asyncio.create_task`.

**Calibration upgrade:**
- [x] **Isotonic regression** — fitted alongside Platt calibration in `calibration.py` when scikit-learn is available. Non-parametric: learns the actual shape of score→probability relationship. Stored as `_isotonic` in calibration.json. `apply_calibration()` uses isotonic interpolation when ≥30 training samples, falls back to Platt bin-blend.

**Send quality gates (scanner.py `_maybe_send`):**
- [x] **Pre-earnings hard blackout** — no BUY/SELL sent within 2 days of earnings (`daysToEarnings ≤ 2`). Prevents IV crush, gap-through-stop, and analyst pre-positioning distortions.
- [x] **Sector concentration limit** — max 2 BUY signals per SPDR sector ETF per rolling 24h. Prevents sending NVDA + AMD + SOXL + MU as "4 signals" when they're one correlated market view.
- [x] **Ticker-adaptive confidence floor** — tickers with historical win rate <45% require ≥68% confidence to send; high-win-rate (≥75%) tickers use a relaxed 52% floor. Reads from `adaptive_weights.ticker_win_rates` cached per scan cycle.

**Signal card UX (app.signal.jsx):**
- [x] **Entry/Stop/Target chips in collapsed card** — traders see levels (E $175.40 · S $171.00 · T $183.00) without expanding. Green for target, red for stop. Was previously hidden behind a click.
- [x] **Mini confidence sparkline** — 5-point trend inline in every collapsed card. Derived from same-ticker-same-action signals already in memory (zero extra API calls). Rising = green, falling = red.

**Detail pane (app.jsx):**
- [x] **Live WebSocket price in hero** — `livePrice` derived from `tickerTape` state updated by WS tick handler. Shows current price vs entry and calculates "X% above stop". Falls back to static scan-time price gracefully.
- [x] **Chart on Why tab** — LightweightCharts OHLCV chart with entry/stop/target lines moved to top of Why tab. First thing visible after selecting a signal, before rationale cards.

**HistoryView (app.views.jsx):**
- [x] **Exit type as primary outcome** — TARGET (green) / STOP (red) / TIME (amber) badge is now column 6, before the raw return. A signal that hit stop at -8% and recovered to +1% by day 7 correctly shows as STOP red, not a +1% win.

**Test suite (all tests green after refactoring):**
- [x] **`_assemble_signal` parameter fix** — `_is_lev_etf` added as explicit keyword parameter (was accidentally accessed as closure variable from `generate_signal`'s scope, causing NameError when tests called `_assemble_signal` directly).
- [x] **Test updates** — `TestBlend` updated to `_MAX_BLEND=0.90, _N_FULL=20`; `TestBestOutcome` updated to expect `outcome_14d` first; `TestMaybeSend` mocks updated for new daily-cap + source-independence query order; `_sig()` helper given non-technical source so independence gate passes.
- [x] **597 passed, 0 failed** — all test suites green.

### v5.5 (2026-05-16) — Validation-Driven Fixes, Quant Features & Leveraged ETF Tracker

**Signal validation & calibration (from n=529 resolved signal audit):**
- [x] **14-day primary outcome** — `validate_predictions._best_outcome()` now prefers `outcome_14d` over `outcome_pct` (7d). 14d shows 63.2% win rate / +4.90% avg return vs 57.7% / +2.32% at 7d. Horizon labels in WORST/BEST signal tables updated accordingly.
- [x] **Confidence ceiling 84%→72%** — Empirical validation showed 75-84% bands win at only 48-50%. Ceiling lowered at all 6 cap/clamp sites in `signal_engine.py` plus `calibration.py`. No signal will ever display confidence above 72%.
- [x] **Platt calibration tightened** — `_MAX_BLEND` raised 0.80→0.90; `_N_FULL` lowered 30→20 (faster convergence); calibration now uses `outcome_14d` when available (falls back to 7d). Clamp updated to [35, 72].
- [x] **Intraday style restored** — May 10 retirement reverted. `_is_intraday` correctly routes to `style="intraday"` again. Three-way intraday/swing/position routing re-enabled.
- [x] **Defensive-ticker BUY gate** — 16 tickers with validated 0% BUY win rate (BAC, KO, PEP, T, NEE, PG, USB, PNC, C, TGT, AIG, WM, MCO, TT, DE, TJX) now gate to HOLD with a Risk Gate rationale card. Catches higher-ATR names that slip past the existing ATR<0.8% gate.

**Quant / hedge-fund features (free-data only, all zero new API costs):**
- [x] **FRED HY/IG credit spreads** — `macro.py` now fetches `BAMLH0A0HYM2` (ICE BofA US HY OAS spread) and `BAMLC0A0CM` (IG OAS spread) alongside existing FEDFUNDS/CPI. Scored at 3 stress thresholds: HY >600bps (−10), >450bps (−5), <300bps (+4); IG >200bps (−4). More direct than the HYG ETF price proxy.
- [x] **Analyst estimate revision momentum** — `news._fetch_analyst_recs()` already calls Finnhub `recommendation_trends` returning 4 months of data but only used `raw[0]`. Now also reads `raw[1]` (prior month) and computes `revision_pts = bull_delta − bear_delta` (±8 cap). Zero extra API calls. New scoring block in `signal_engine` fires when |rev_pts| ≥ 2 — one of the most documented equity alpha factors (SUE effect / earnings revision momentum).
- [x] **Cross-sectional universe ranking** — Added to `scan_all()` tail after all per-ticker signals and sector/supply-chain passes complete. Ranks every directional signal by confidence within the scan cycle (requires ≥10 signals). Top decile +3pp, top quartile +1.5pp; bottom quartile −1.5pp, bottom decile −3pp. Each adjusted signal gets a "Cross-Sectional" rationale card showing its universe rank percentile. Converts the engine from absolute scoring to relative scoring.
- [x] **Beta in signal dict** — `info["beta"]` was already fetched from yfinance but unused. Added `"beta": info.get("beta")` to the signal return dict. PositionCalc can now use it for SPY-beta-adjusted sizing.
- [x] **Alpha decay by source — `GET /api/signals/alpha-decay`** — New endpoint in `routers/signals.py`. Queries all resolved signals, unpacks each signal's `sources` JSON array, and computes win rate + avg return at 1d/3d/7d/14d per source (min 3 signals, configurable). 5-min cache. Reveals which scoring families have real edge at which horizons and at what holding period — e.g. "RSI Oversold" might peak at 3d but decay by 14d; "Piotroski F-Score 8" might be flat across all horizons. Informs optimal hold time per signal family.

**Leveraged & inverse-leveraged ETF tracker:**
- [x] **52 leveraged ETFs added to watchlist** — 3× bull (SOXL, TECL, FAS, TNA, LABU, UPRO, SPXL, WEBL, FNGU, NAIL, DPST, YINN, DRN, TMF, HIBL, MIDU, GUSH, NUGT, JNUG), 3× bear (SQQQ, SPXS, SPXU, SOXS, TECS, FAZ, TZA, LABD, FNGD, YANG, DRV, TMV, HIBS, SRTY, DRIP, DUST, JDST), and popular 2× pairs (SSO/SDS, QLD/QID, UCO/SCO, ROM/REW, UWM/TWM). Watchlist seed now covers ~210 tickers.
- [x] **`_LEVERAGED_ETFS` frozenset** — Module-level constant (52 tickers) in `signal_engine.py`. Used as the single source of truth for ETF detection.
- [x] **Fundamentals/earnings/insider bypass** — Immediately after `_fetched` is unpacked, `_is_lev_etf` flag zeros out `fundamentals`, `earnings_cal`, `earnings_surp`, `insider`, `analyst_recs`, `congress` for leveraged ETF tickers. All downstream blocks already guard on `if fundamentals:` etc. — no wasted API calls, clean silent bypass.
- [x] **Style cap at swing** — Leveraged ETFs that score as "position" are forced back to "swing". Daily-rebalancing products lose 2–8% NAV per round-trip to volatility decay; position-style hold times make target prices meaningless.
- [x] **Disclosure rationale card** — Every leveraged ETF signal gets a "Risk Gate" card showing multiplier (2× or 3×), direction (Bull/Bear), decay risk, fundamentals bypass, and ≤5-day / ⅓ position size recommendation.
- [x] **Company names** — All 52 ETFs have display names with `(3×)` / `(−3×)` / `(2×)` suffix in `market_data.py`. Suffix is visible in the signal feed header.
- [x] **Sector mappings** — All 52 ETFs mapped to their underlying's sector ETF in `sector.py` (e.g. SOXL/SOXS → XLK, FAS/FAZ → XLF, GUSH/DRIP → XLE, NUGT/DUST → XLB, DRN/DRV → XLRE, TMF/TMV → XLU, YINN/YANG → XLC).

### v5.4 (2026-05-10) — Production Hardening, PostgreSQL Migration & Legal

**Production security:**
- [x] **Cookie `Secure` flag** — Refresh-token cookie now auto-sets `Secure=true` when `APP_URL` starts with `https://`. Was hardcoded `False` — refresh tokens would have been sent over plain HTTP in production.
- [x] **CORS locked** — `allow_origins` changed from `["*"]` to the configured `APP_URL` domain for any non-localhost deployment. Stays open for local dev automatically.
- [x] **Non-root Docker user** — `Dockerfile` now creates `appuser` (UID 1000) and runs the container as that user. Was running as root.
- [x] **SQLite path → `./data/`** — Default SQLite DB moved from `./trading.db` to `./data/trading.db` so it lives inside the Fly.io persistent volume (`/app/data`). Previous path was outside the mount and wiped on every deploy. Auto-migrates existing `trading.db` on first start.
- [x] **fly.toml hardened** — `[mounts]` → `[[mounts]]` array syntax; HTTP healthcheck added (polls `/api/health` every 30s, 10s grace, 3 retries before restart).
- [x] **Expired reset-token GC** — Forgot-password endpoint now purges expired entries from the in-memory `_reset_tokens` dict on every write.
- [x] **`docker-compose.yml` updated** — Postgres 16-alpine service added with named volume, healthcheck, and `depends_on`. Backend overrides `DATABASE_URL` to use the compose service hostname.

**PostgreSQL migration (complete):**
- [x] **Local PostgreSQL 16** — Installed via Homebrew, `signal_trade` database and `signal` user created.
- [x] **`database.py` early `.env` load** — Added `load_dotenv()` at import time so `DATABASE_URL` is read before SQLAlchemy constructs the engine. Was silently falling back to SQLite on every server start even with `DATABASE_URL` in `.env`.
- [x] **`backend/scripts/migrate_sqlite_to_postgres.py`** — One-shot idempotent migration: reads all 10 tables from SQLite, type-coerces JSON/bool/datetime columns, truncates PG tables, inserts in FK dependency order, resets all sequences. 7,015 signals + 8 users migrated.
- [x] **Sequence fix** — All PostgreSQL `id` sequences advanced past max existing value after migration. Unset sequences caused 500 on login (`duplicate key value violates unique constraint "refresh_tokens_pkey"`).
- [x] **`backend/.env`** — `DATABASE_URL=postgresql://signal:signal_dev_pw@127.0.0.1:5432/signal_trade` set for local dev.
- [x] **`backend/.env.example`** — Added `DATABASE_URL`, `JWT_SECRET`, `APP_URL`, `STRIPE_WEBHOOK_SECRET`, `SMTP_*`, `GOOGLE_CLIENT_*`, `DISCORD_CLIENT_*` sections (were missing).

**Legal updates (TOS):**
- [x] **Removed hardcoded algorithm version** — `v5.2` reference removed from Section 2; replaced with "proprietary automated algorithmic system". Version numbers in TOS create liability as code evolves.
- [x] **Removed unenforceable chargeback waiver** — Section 6 previously contained "you irrevocably waive any right to dispute charges with your payment provider" — unenforceable in most jurisdictions and violates Stripe ToS. Removed.
- [x] **Governing law specified** — Section 13 now names Delaware, United States + AAA Consumer Arbitration Rules. Was vague ("jurisdiction in which the operator is based").
- [x] **Publisher exemption added** — Section 14 now cites the Investment Advisers Act §80b-2(a)(11)(D) bona fide publisher exemption, CFTC/CTA non-registration notice, and explicit no-personalized-advice statement. This is the core legal shield for a signal publishing service.

**Bug fix:**
- [x] **CALIB badge overlap** — `⚠ CALIB` badge in hero-meta was overlapping the ConfidenceTrend chart at narrow panel widths. Fixed by adding `flexShrink:0` to the confidence span (app.jsx) and `flex-shrink: 0` to `.ct-wrap` (styles.css).

**Docs:**
- [x] **README.md, HOWTO.md, PROGRESS.md** — All updated to reflect PostgreSQL as default, new migration workflow, Stripe webhook setup, security auto-config note, Fly.io healthcheck, Docker Compose postgres service.
- [x] **HOWTO.md §33** — Complete rewrite of PostgreSQL Migration section.

### v5.3 (2026-05-10) — Modularisation, Validations & Bug Fixes

- [x] **app.jsx modularised** — 5311-line monolith split into 8 files: `app.auth.jsx`, `app.constants.jsx`, `app.ui.jsx`, `app.signal.jsx`, `app.views.jsx`, `app.modals.jsx`, `app.analysis.jsx`, `app.jsx` (1424 lines). Loaded sequentially via Babel script tags.
- [x] **signal_scoring.py** — Pure scoring helpers extracted from signal_engine.py: `score_oscillators`, `score_macd`, `score_ema_cross`, `score_obv_adx`, `score_moving_averages`.
- [x] **Backend input validation** — `routers/auth.py`: email format regex, password 8–128 chars, name ≤60 chars. `routers/watchlist_router.py`: ticker `^[A-Z]{1,5}$`. `routers/price_alerts.py`: proper Pydantic model with price range 0–$1M, condition enum.
- [x] **Frontend input validation** — WatchlistView: ticker regex + non-alpha stripping. PriceAlertModal: range 0–$1M + red border on invalid. AccountModal: name length + conf range 0–100 + inline errors. RulesView: time HH:MM format + start<end check.
- [x] **Bug: AdSlot hooks-in-conditional** — `React.useEffect` moved outside the `if (hasAdSense)` block; condition moved inside effect body.
- [x] **Bug: DemoTour hooks-in-conditional** — `useEffect` moved before `if (!open) return null` early return.
- [x] **Bug: AccountModal saveName** — Added try/catch, empty/length validation, error state display. No longer crashes silently on API failure.
- [x] **Bug: registerWebhook alert()** — Replaced browser `alert()` with `webhookMsg` state variable rendered inline.
- [x] **Configure Ads for Free Plan** — `AdSlot` component renders Google AdSense `<ins>` tags for free-tier users; tasteful upgrade CTA fallback. Slim banner above feed + full unit every 5 cards.
- [x] **Data Redistribution Compliance** — Chart endpoints require Basic subscription (`_require_basic()` guard, HTTP 402). `X-Data-Policy` header on all `/api/` responses via `DataComplianceMiddleware`. `config.py` `TIER_FEATURES` includes `"chart"` in Basic+.
- [x] **Terms of Service** — "No Refunds for Trading Losses" clause added to `tos.html` Section 6.
- [x] **Telegram Rate Limit Prep** — `TELEGRAM_BROADCAST_CHANNEL_ID` env var; when set, `_maybe_send()` posts once to channel instead of N per-user DMs.

### v5.2 (2026-05-09) — Polygon.io Free-Tier Optimisations

- [x] **Polygon OHLCV bug fix** — `polygon_client.py` was reading `POLYGON_API_KEY` (empty) instead of `MASSIVE_API_KEY`. Fixed `_get_api_key()` to check both.
- [x] **Pre-computed Indicators** — `services/polygon_indicators.py`. RSI(14), MACD, SMA(20/50/200/EMA200) from `v1/indicators/*`. RSI blended 60% Polygon / 40% pandas. 30-min cache.
- [x] **Related Companies Peer Scoring** — `services/polygon_related.py`. `v1/related-companies/{ticker}`. BUY with ≥2 peers also bullish → +2pp; 0 peers → −5pp. 24h cache.
- [x] **Fast Quotes** — `get_quotes_batch()` tries Polygon `v2/aggs/ticker/{ticker}/prev` first (80ms stagger), falls back to yfinance. 154-ticker quote refresh ~12s vs previous 15s+ timeout.
- [x] **Authoritative Market Status** — `v1/marketstatus/now` from Polygon; writes `market_open`, `after_hours`, `early_hours` into macro context. NYSE OPEN/CLOSED chip now accurate.
- [x] **Polygon News as Primary Source** — `services/benzinga_news.py` rewritten to use `v2/reference/news`. Keyword sentiment scoring with age decay.
- [x] **Polygon Financial Ratios** — `services/massive_ratios.py` rewritten: `vX/reference/financials` for FCF yield, gross/net margin, D/E, current ratio, revenue QoQ. 6h cache.
- [x] **Corporate Events** — `services/corporate_events.py` rewritten: dividends, splits, M&A/guidance via Polygon free tier. Scored in signal engine.
- [x] **Weekly OHLCV Trend Strength** — 26-week bars; SMA13 above/below for 8/10 weeks = ±4pts.
- [x] **EMA(200) Dynamic Trend Gate** — Double-bullish (above EMA200+SMA200) = +3pts; double-bearish = −3pts.
- [x] **3-Year Revenue Acceleration** — "Earnings Torpedo" block from annual financials.
- [x] **Accurate Dividend Yield** — TTM from last 4 quarterly payments; Aristocrat/King bonuses.
- [x] **Macro News Sentiment** — SPY+QQQ Polygon news; caps BUY confidence at 65% when sentiment < −0.3 AND VIX > 20.
- [x] **Market Holiday Pre-Signal Warning** — `services/market_calendar.py`; `v1/marketstatus/upcoming`; −5pp haircut near 3-day weekends.
- [x] **VIX from Polygon** — `I:VXN`/`^VIX` via Polygon first; yfinance fallback.

### v5.1 (2026-05-09)

- [x] **Macro Regime HMM** — `services/macro_regime.py`. Pure-numpy 2-state Gaussian HMM (Baum-Welch, 25 iterations) on VIX, SPY 20d return, yield curve, realised vol. Probability-weighted scoring multipliers. `GET /api/market/regime`. HMM chip in topbar + sidebar.
- [x] **Supply Chain Alt Data** — `services/supply_chain.py`. Baltic Dry Index (Stooq), Brent Crude (yfinance), Cass Freight (FRED). Sector impact map; ±8pts in signal engine.
- [x] **Dark Pool Block Trade Reconstruction** — Rolling 30-min print buffer, Lee-Ready tick rule, groups FINRA TRF prints. `GET /api/market/dark-pool/reconstructed`.

### v5.0 (2026-05-09)

- [x] **Polygon.io as Primary OHLCV** — `get_history()` tries `polygon_client.py` first; yfinance fallback. Eliminates Yahoo 429 errors.
- [x] **Push Notifications** — `pywebpush` + VAPID; `_maybe_send()` fires web push for ≥70% confidence signals.
- [x] **Multi-Ticker Comparison Chart** — "Compare vs SPY/QQQ/IWM/GLD" button row; `CompareChart` LightweightCharts overlay on normalised % return.
- [x] **Cross-Asset Volatility Targeting** — `services/volatility_targeting.py`; inverse-vol weights with correlation penalty; 15% annualised target. `GET /api/paper/volatility-target`. Panel in PaperView.

### v4.9 (2026-05-08)

- [x] **Massive API Advanced Signals** — FTDs & Reg SHO, Options GEX, Retail vs Institutional Flow Divergence, Level 2 Order Book Imbalance, Real-Time Buyback Executions in `signal_engine.py`.

### v4.8 (2026-05-07)

- [x] **Elliott Wave & Gann Analysis** — Phase identification and 1×1 angle tracking in `services/technicals.py`.
- [x] **Dark Pool Scaffold** — `services/dark_pool.py` + Massive WebSocket for off-exchange block trades.
- [x] **Massive API Integration** — WebSocket into dark pool; REST into Market Overview dashboard.

### v4.7 (2026-05-06)

- [x] **Volatility-Scaled Bayesian Smoothing** — `services/bayesian_smoothing.py`; adjusts Laplace smoothing based on VIX.
- [x] **Monte Carlo Web Worker** — `monte_carlo_worker.js`; 500-path simulation off main thread.
- [x] **Discord Bot Delivery** — `services/discord_bot.py`; webhooks alongside Telegram.
- [x] **Price Alert System** — `routers/price_alerts.py` with full Pydantic validation.
- [x] **Referral Programme** — Phase 2 billing; Stripe credits on conversion.

### v4.6 (2026-05-05)

- [x] **Backend test/coverage harness** — project-local venv, runnable coverage suite.
- [x] **Signal De-confliction Gate** — Dynamic confidence penalties (8% per warning, 20% max) for conflicting signals. "Risk Gate" rationale cards.
- [x] **Visual Risk-Reward Chart Zones** — Red (stop) / green (target) shaded areas on price chart.
- [x] **Keyboard Navigation** — `p` (paper trade), `s` (skip) hotkeys.
- [x] **Execution Slippage Logic** — `check_slippage()` in Alpaca integration; rejects if price slipped >$0.05 within 100ms.
- [x] **SQLite Concurrency** — WAL mode, `synchronous=NORMAL`, 64MB cache, 256MB mmap, 5000ms busy timeout.
- [x] **Local LLM Offloading** — `services/local_llm.py`; Ollama/LM Studio; async `aiohttp` client.
- [x] **Pre-warmed Vector Store** — `services/vector_store.py`; Qdrant/Milvus/Memory; 28-indicator regime DNA + similar setup win rate lookup.

### v4.4–v4.5 (2026-05-04)

- [x] **`_force_hold` flag** — Earnings/sector blackouts enforced at final assembly; survives all post-zero scoring blocks.
- [x] **Extended-Hours Signal Block** — 1-min bars with `prepost=True`; gap + volume-surge signals for institutional pre-open positioning.
- [x] **Interactive OHLCV Chart** — LightweightCharts v4 candlestick/line/area; 200-DMA, Entry/Stop/Target lines, volume histogram.
- [x] **Confidence Heat Bar** — Coloured fill bar in feed rows and detail pane (green ≥75%, blue 62–75%, amber 50–62%, red <50%).
- [x] **Position Size Calculator** — Inline in detail pane; portfolio + risk% inputs; shows Shares, Max loss, Max gain, Notional. PAPER TRADE button executes against paper API.
- [x] **Extended GLOSSARY** — 20+ indicator definitions (MACD, RSI divergence, OBV, CMF, ADX, FDI, Hurst, VWAP, Supertrend, Stochastic, Williams %R, CCI, MFI, Keltner, Donchian, Ichimoku, Z-Score, Pivots, Orthogonal Alpha, Signal Cluster, Platt Calibration, Factor Mining, Sector RS, 13F, Stat Arb).
- [x] **Rationale Card Tooltips** — Hover over indicator names → glossary definition; 38-entry prefix map.
- [x] **Threshold Inline Control** — ±5 stepper in sidebar.
- [x] **Economic Calendar Enriched** — PCE, PPI, Retail Sales, GDP via FRED; release time, impact badge, expandable context.
- [x] **Load Time & Cache** — Signals initialized from `localStorage`. `/api/market/context` has 5-min in-memory cache.
- [x] **`LightweightCharts` reference unified** — `window.LightweightCharts` guard + `LC` alias prevents `ReferenceError` if CDN fails.

### v4.3 (2026-05-03)

- [x] **Platt Scaling Calibration** — `services/calibration.py`. Bins historical pairs into 5pp buckets, blends toward empirical win rate. Last step before 84% ceiling.
- [x] **Sector Downtrend BUY Gate** — `sector_1m_ret < −5%` AND `score < 40` → gate BUY to HOLD.
- [x] **Loss-Aware Duplicate Cooldown** — 1 loss → 48h cooldown; 3+ losses → 72h cooldown.
- [x] **Style Classification Overhaul** — Position requires Piotroski 7/8/9, strong FCF, buyback, or institutional QoQ trend. Default → swing.
- [x] **Low-Volatility BUY Gate** — `atr_pct < 0.8%` requires score ≥35 AND macro_score ≥0 for BUY.
- [x] **Post-Earnings Cooldown** — Days 0–2 → hard HOLD; days 3–4 → ×0.80 score suppression.
- [x] **Signal Confidence Decay** — Nightly decay 3pp/day for signals older than 3 days, capped −15pp.

### v4.2 (2026-05-02)

- [x] **Agreement Bonus Decontamination** — Excludes meta-sources (Risk Gate, Orthogonalization, Signal Cluster) from agreement count.
- [x] **Consecutive Loss Streak Suppression** — Streak ≥2 → −5pp per loss, capped −20pp.
- [x] **Recency-Weighted Win Rates** — Exponential decay (halflife 60 days) replaces flat all-time rates.
- [x] **Bear + High-VIX BUY Gate** — Post-multiplier score <35 → HOLD when SPY below 50-DMA AND VIX >25.
- [x] **Macro Contradiction Cap** — BUY ≥70% conf with bearish macro → cap at 65%. Symmetric for SELL.

### v4.1 (2026-05-01)

- [x] **Per-Ticker Win Rates** — `_compute_adaptive_weights()` returns `ticker_win_rates` (min 3 resolved signals).
- [x] **Cluster Boost De-Rating** — When ticker win rate <50%, cluster boost halved, orthogonality bonus halved.
- [x] **Weight Overrides in Settings** — `weight_overrides` JSON persists manual bias (cluster_boost, orthogonality_pts, orthogonality_max) across factor mining runs.
- [x] **Factor Mining Wired** — Engine reads `market_ctx["factor_weights"]`, applies ±3pt (capped ±5) per source combo rank.
- [x] **Engine Bias Panel in TweaksPanel** — Three number inputs with blue override border, ↺ reset buttons.

### v4.0 (2026-04-30) — Core System

- [x] **Auth & Users** — JWT HS256, bcrypt, refresh token rotation, OAuth (Google + Discord), email verification, password reset, GDPR erasure, rate limiting.
- [x] **Subscription & Billing** — Stripe Checkout + Portal + Webhooks, Free/Basic/Pro tiers, feature gates, coupon codes, transactional emails.
- [x] **Signal Engine** — 50+ scoring blocks; oscillators, trend/momentum, mean reversion, MAs, volume, regime, multi-timeframe, options, institutional 13F, news/analyst, earnings, relative strength, macro, fundamentals, meta-scoring.
- [x] **Scanner** — Batch history, time-of-day filter, smart deduplication, multi-user fan-out, WebSocket broadcast, paper auto-trade, weekly digest, factor mining, nightly cleanup.
- [x] **Cointegration / Pairs Trading** — `services/cointegration.py`; 14 pre-defined pairs; 2σ spread; Stat Arb source.
- [x] **Institutional QoQ Delta** — 3 quarters; consecutive trend ×1.5 scoring.
- [x] **Correlation-Based Portfolio Limits** — Soft 30% / hard 50% sector concentration limits.
- [x] **Event-Driven Microservices** — `services/worker_bus.py` with asyncio.Queue + Redis Streams backend; `CircuitBreaker`; 5 isolated scoring workers in `services/signal_workers.py`.
- [x] **Webhook Outbound** — HMAC-signed POST to user-defined webhook URL on successful Telegram send.
- [x] **Rate-Limit Dashboard** — `GET /api/admin/rate-limits`; yfinance CB state, cache stats, screener suggestions.
- [x] **SQLite → PostgreSQL Migration Path** — `database.py` detects `postgresql://` prefix; no schema changes needed.
- [x] **yFinance Global Circuit Breaker** — Trips `_yf_backoff_until` 15min on 429.
- [x] **Playwright News Scraper** — `services/news_scraper.py`; Seeking Alpha + Reuters + Finviz; Playwright chromium fallback.
- [x] **Docker + Deploy** — `docker-compose.yml`, `Dockerfile`, `railway.toml`, `fly.toml`, `Procfile`, `/api/health`.
- [x] **Frontend** — Three-pane layout, style strip, FilterChips, j/k navigation, signal cluster chip, ConfidenceTrend, WhyNow, SimilarSignals, OutcomeStrip, BacktestView with Calibration tab, SortableTable, Watchlist sort, PaperView, AccountModal, HotkeyHelp, DemoTour, PredictiveIntervals, NoteEditor, SimulatedReturnsPanel.
- [x] **RAG & Semantic Memory** — Vector store fed with historical regime embeddings; similar setup win rate lookup.
- [x] **Automated Reflection** — LLM reads loss outcomes, saves reflection to vector DB.
- [x] **Generative UI / NL Search** — Natural language query parser: action, confidence, style, source, rationale, sector intent from free-text.
- [x] **DOM Virtualisation** — Feed paginated 30 cards initially; "Show more" loads 20 at a time; filter resets page.
- [x] **Async Non-Blocking LLM** — `aiohttp`-based `agenerate()` in `local_llm.py`.
- [x] **Differential Scan** — Skips `generate_signal()` for tickers with <0.5% price change + vol <1.3× + active signal <2h.
- [x] **Indicator Cache Warming** — `_warm_indicator_cache()` on startup; pre-fetches Polygon indicators at safe free-tier rate.
- [x] **Polygon OHLCV Shared Cache** — `_ohlcv_cache` keyed by `(ticker, period, interval)`, 15-min TTL.
- [x] **Heavy Analytics Caching** — `/backtest` + `/correlation` cached 5min in-memory.
- [x] **Out-of-Process Web Scraping** — `_playwright_finviz_sync()` in `asyncio.to_thread()`; Chromium no longer blocks event loop.
- [x] **WebSocket Reconnection Resilience** — `_watchdog()` coroutine restarts WS on 15s stall; dark pool thread restarted on 60s stall.
- [x] **Signal History Export** — `GET /api/signals/history/export?format=xlsx`; styled openpyxl workbook.
- [x] **Automated Factor Mining** — `services/factor_miner.py`; brute-forces source combos; ranks by OOS Sharpe (70/30 split); Sunday 10am ET job.
- [x] **PCA Risk Model** — `services/pca_risk.py`; latent factor decomposition; haircut on overexposed factor clusters.
- [x] **NLP on Earnings Transcripts** — Local LLM tones MD&A + Risk Factors sections.
- [x] **10-K/10-Q Delta Analysis** — Tracks textual changes in SEC filings quarter-over-quarter.
- [x] **Supply Chain Graph Propagation** — Supplier/customer lead-lag scoring via supply_chain.py.
- [x] **Advanced Dealer Positioning (Vanna & Charm)** — Structural hedging flow prediction for OPEX.
- [x] **Parallel Signal Generation** — `scan_all()` with `asyncio.Semaphore(5)`; ~5× speedup.

---

## 🏆 System Validation — v5.3 (2026-05-10)

### Technical Validation
- **53 Python files** — 0 syntax errors (project files; venv excluded)
- **13/13 critical modules** import cleanly (signal_engine, scanner, signal_scoring, all routers, main)
- **7/7 API smoke tests** passed (health, auth guards, market context, calendar, chart, delivery log, signals)

### Signal Accuracy — 14-Day Evaluation (2026-04-25 → 2026-05-09)

#### All-horizons: **B — 78/100**
| Metric | Value |
|--------|-------|
| Win rate | **56.4%** |
| Profit factor | **2.41×** |
| Annualised Sharpe | **1.88** |
| Expectancy / trade | **+1.32%** |
| Calibration gap | **+6.2pp** |

#### 7-day resolved only: **A+ — 95/100**
| Metric | Value | Benchmark |
|--------|-------|-----------|
| Win rate (7d) | **64.1%** | >55% = good edge |
| Avg win / Avg loss | **+5.12% / −2.40%** | |
| Profit factor | **2.85×** | >1.5 = excellent |
| Annualised Sharpe | **2.45** | >2.0 = institutional |
| Expectancy / trade | **+2.42%** | |
| Kelly fraction | **41%** (use ¼ Kelly → ~10%) | |
| 14-day win rate | **82.4%** (n=34) | |
| High-conf ≥70% | **71.2%** | |

#### By horizon:
| Horizon | N | Win rate | Avg return |
|---------|---|----------|------------|
| 1-day | 210 | 44.5% | +0.55% |
| 3-day | 195 | 59.3% | +1.15% |
| **7-day** | **142** | **64.1%** | **+2.42%** |
| 14-day | 34 | 82.4% | +8.10% |

#### Best tickers: AMD 100% (+14.2%), GOOGL 100% (+9.1%), AMZN 100% (+4.5%), MU 100% (+8.3%)
#### Worst tickers: PLTR 15% (−2.1%), META 35% (−1.8%), NVDA 41% (+0.5%)

---

## 👁️ Known Blind Spots

| # | Issue | Severity | Fix |
|---|-------|----------|-----|
| 1 | **Intraday noise** — 30.4% win rate on 1d holds (validation n=529) | Medium | ✅ Intraday style restored with volatility-decay awareness; style cap swing for leveraged ETFs |
| 2 | **Low-vol / defensive stocks** — 0% BUY win rate (BAC, KO, PEP, T, NEE, PG, USB, PNC, C, TGT, AIG, WM, MCO, TT, DE, TJX) | High | ✅ Fixed — named defensive-ticker BUY gate converts to HOLD for 16 validated zero-win-rate tickers |
| 3 | **Confidence overconfidence** — 75-84% bands won at only 48-50% | High | ✅ Fixed — ceiling lowered 84%→72% at all cap sites; Platt calibration tuned (_MAX_BLEND 0.8→0.9, _N_FULL 30→20); now uses 14d outcomes |
| 4 | **Leveraged ETF fundamentals misfiring** — Piotroski/FCF/earnings scoring on SOXL/TQQQ/etc. | High | ✅ Fixed — _LEVERAGED_ETFS frozenset (52 tickers); full fundamentals/earnings/insider bypass; swing-only style |
| 5 | **Dividend ex-date trap** — mechanical drop triggers false breakouts | Medium | Ensure dividend-adjusted OHLCV; 1-day blackout around ex-date for high-yield stocks |
| 6 | **Correlated tech exposure** — NVDA/AMD/TSM treated as independent | Medium | ✅ PCA haircut + cross-sectional ranking now penalises crowded sector signals |
| 7 | **Post-earnings IV crush** — options premium destroyed even on correct direction | Medium | Flag `IV Rank > 80%` swing trades as "Premium Selling" instead of directional |
| 8 | **LLM sync blocking** (if Ollama enabled) | Medium | ✅ Fixed — `aiohttp`-based async client |
| 9 | **PostgreSQL migration** — `SQLITE_BUSY` under multi-user load | Medium | ✅ Fixed — PostgreSQL 16 (asyncpg) + Redis analytics caching |
| 10 | **yFinance rate-limit fragility** | Low | ✅ Fixed — global circuit breaker trips 15min on 429 |

---

## ⬆️ Polygon Premium Upgrade Path

The following services are built and gracefully return `{}` on the free tier. Upgrading unlocks them with **zero code changes**:

| Service | File | Plan |
|---------|------|------|
| Full option chain GEX + 25Δ skew | `massive_options.py` | Starter ($29/mo) |
| Real-time snapshot (live price) | `massive_options.py` | Starter |
| ETF fund flow data | `etf_flows.py` | Developer ($79/mo) |
| ETF constituent weights | `etf_constituents.py` | Developer |
| Bulls Bears Say analyst thesis | `massive_analyst.py` | Developer |
| Corporate Guidance (EPS raise/cut) | `massive_analyst.py` | Developer |
| Wall Street Horizon corporate events | `corporate_events.py` | Developer |
| 8-K material event text | `eightk_events.py` | Developer |
| Real-time trade tape (dark pool) | `dark_pool.py` | Developer |

---

## 📚 Architecture Reference

### Database Schema (SQLite · WAL mode)

| Table | Key columns |
|-------|-------------|
| `signals` | ticker, action, confidence, `confidence_warning`, price, entry/stop/target, rr, headline, sentiment, style, sources (JSON), rationale (JSON), `plain_english` (JSON), `session`, `days_to_earnings`, `next_earnings_date`, `sector_etf`, `rs_vs_sector`, reviewed, notes, is_active, is_sent, is_skipped, `expires_at`, outcome_pct/1d/3d/14d |
| `users` | email, password_hash, full_name, is_owner, subscription_tier/status/period_end, stripe_customer/subscription_id, telegram_chat_id/link_code, oauth_provider/sub, `email_verified`, min_confidence_override, referred_by, referral_rewarded |
| `refresh_tokens` | user_id, token_hash (SHA-256), expires_at, revoked |
| `signal_deliveries` | signal_id, user_id, sent_at, telegram_msg_id |
| `watchlist` | ticker, company, is_active, added_at |
| `sources` | id, name, abbr, description, is_on, requests_24h, latency_ms, feed |
| `app_settings` | id=1, data (JSON) — user tweaks + weight_overrides |
| `send_log` | time, status, message, created_at |

**SQLite pragmas:** `journal_mode=WAL`, `synchronous=NORMAL`, `cache_size=−64000` (64MB), `mmap_size=256MB`, `busy_timeout=5000ms`

**Indexes on `signals`:** ticker, is_active, confidence, created_at, is_sent, action, style, outcome_pct, `(is_active, confidence DESC)`, `(is_sent, outcome_pct)`

### API Endpoints (75+)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | — | Create account |
| POST | `/api/auth/login` | — | JWT + refresh cookie |
| GET | `/api/auth/verify-email?token=` | — | Verify email |
| POST | `/api/auth/refresh-cookie` | cookie | Rotate refresh token |
| POST | `/api/auth/logout` | ✓ | Revoke all tokens |
| GET/PATCH | `/api/auth/me` | ✓ | Profile |
| DELETE | `/api/auth/me` | ✓ | GDPR erasure |
| POST | `/api/auth/change-password` | ✓ | Change password |
| POST | `/api/auth/forgot-password` | — | Password reset |
| POST | `/api/auth/reset-password` | — | Complete reset |
| POST | `/api/auth/telegram-link-code` | ✓ | Generate Telegram code |
| DELETE | `/api/auth/telegram-unlink` | ✓ | Unlink Telegram |
| PATCH | `/api/auth/signal-prefs` | ✓ | Per-user confidence threshold |
| GET | `/api/auth/referral` | ✓ | Referral link + stats |
| GET | `/api/auth/google` | — | Google OAuth |
| GET | `/api/auth/discord` | — | Discord OAuth |
| GET | `/api/auth/oauth-exchange?code=` | — | OTC → access token |
| GET | `/api/billing/plans` | — | Plan definitions |
| POST | `/api/billing/checkout/{tier}` | ✓ | Stripe Checkout |
| POST | `/api/billing/portal` | ✓ | Stripe billing portal |
| GET | `/api/billing/status` | ✓ | Tier + card on file |
| POST | `/api/billing/webhook` | — | Stripe events |
| GET | `/api/admin/setup-status` | owner | Config health |
| GET | `/api/admin/users` | owner | All users |
| GET | `/api/admin/stats` | owner | MRR, ARR, delivery stats |
| POST | `/api/admin/users/{id}/tier` | owner | Override tier |
| DELETE | `/api/admin/users/{id}` | owner | Delete user |
| GET | `/api/admin/rate-limits` | owner | Cache + CB stats |
| POST | `/api/admin/trigger-weekly-digest` | owner | Send digest now |
| GET | `/api/admin/weekly-digest/status` | owner | Digest schedule + delivery status |
| POST | `/api/telegram/webhook` | — | Bot `/start <code>` handler |
| POST | `/api/telegram/set-webhook` | — | Register webhook URL |
| GET | `/api/public/track-record` | — | Aggregate stats |
| GET | `/api/signals` | ✓ | Active signals |
| GET | `/api/signals/history` | ✓ | Past signals (filterable) |
| GET | `/api/signals/backtest` | basic | Win rate + Sharpe |
| GET | `/api/signals/backtest/horizons` | basic | Win rate at 1d/3d/7d/14d |
| GET | `/api/signals/backtest/calibration` | ✓ | Reliability diagram |
| POST | `/api/signals/backtest/backfill` | ✓ | Fill outcomes |
| GET | `/api/signals/track-record` | basic | Per-ticker Sharpe |
| GET | `/api/signals/correlation` | pro | Source co-occurrence |
| GET | `/api/signals/factor-mining` | ✓ | Factor mining results |
| POST | `/api/signals/factor-mining/run` | ✓ | Trigger factor mining |
| GET | `/api/signals/alpha-decay` | ✓ | Win rate + avg return by source at 1d/3d/7d/14d |
| GET | `/api/signals/predictive` | ✓ | Bayesian P(success) + CI |
| GET | `/api/signals/{ticker}/confidence-history` | ✓ | Last 30 confidence scores |
| GET | `/api/signals/{ticker}/spark` | ✓ | OHLCV sparkline |
| PATCH | `/api/signals/{id}/notes` | ✓ | Save note |
| POST | `/api/signals/{id}/send` | basic | Manual Telegram send |
| POST | `/api/signals/{id}/skip` | ✓ | Skip signal |
| POST | `/api/signals/{id}/review` | ✓ | Mark reviewed |
| POST | `/api/signals/scan` | ✓ | Trigger manual scan |
| GET | `/api/accuracy/sources` | ✓ | Win rate per source |
| GET | `/api/accuracy/tickers` | ✓ | Win rate per ticker |
| GET/POST | `/api/watchlist` | basic | List / add ticker |
| DELETE | `/api/watchlist/{ticker}` | basic | Remove ticker |
| GET | `/api/quotes` | ✓ | Live prices |
| GET | `/api/chart/{ticker}` | basic | OHLCV chart data |
| GET | `/api/chart/{ticker}/relative` | basic | Normalised % vs benchmark |
| GET/PATCH | `/api/sources` | ✓ | Source list / toggle |
| GET | `/api/market/context` | ✓ | F&G + macro + P/C + breadth + NAAIM + COT |
| GET | `/api/market/calendar` | ✓ | FOMC, CPI, NFP dates |
| GET | `/api/market/sectors` | ✓ | Sector ETF heatmap |
| GET | `/api/market/sectors/detail` | ✓ | Per-sector stock list |
| GET | `/api/market/overview` | ✓ | SPX, NDX, VIX, DXY, breadth |
| GET | `/api/market/regime` | ✓ | HMM regime state |
| GET/POST | `/api/paper/account` | pro | Alpaca paper account |
| GET | `/api/paper/positions` | pro | Open positions |
| GET | `/api/paper/orders` | pro | Order history |
| POST | `/api/paper/orders` | pro | Place order |
| DELETE | `/api/paper/positions/{symbol}` | pro | Close position |
| DELETE | `/api/paper/orders/{id}` | pro | Cancel order |
| GET | `/api/paper/risk` | pro | Beta, Sharpe, MaxDD, Exposure |
| GET | `/api/paper/volatility-target` | pro | Inverse-vol weights |
| GET/PUT | `/api/settings` | ✓ | Load / persist tweaks |
| GET/POST | `/api/alerts/` | ✓ | Price alerts |
| DELETE | `/api/alerts/{id}` | ✓ | Delete alert |
| GET | `/api/health` | — | DB ping |
| WS | `/ws` | ✓ | Real-time signals + price ticks |

### Watchlist (~210 tickers)

| Theme | Tickers |
|-------|---------|
| AI Infra / Semis | NVDA, AMD, AVGO, QCOM, MU, SMCI, ARM, MRVL, AMAT, KLAC, LRCX, ADI, CDNS, SNPS |
| Industrial Rotation | GE, CAT, HON, RTX, DE, UNP, EMR, ITW, APH, ETN, PWR, TT, URI, AME |
| Commodities / Real Assets | GLD, GDX, SLV, XOM, CVX, SLB, EOG, FCX, SCCO, AEM, NEM |
| Software / Next-Gen | PLTR, CRM, NOW, SNOW, PANW, ORCL, IBM, MDB, DDOG, NET |
| Mega-cap Core (S&P 100) | AAPL, MSFT, AMZN, GOOGL, META, TSLA, BRK-B, JPM, LLY, V, UNH, MA, COST, HD, PG, JNJ, WMT, BAC, ABBV, KO, ACN, MRK, CVX, TMO, WFC, ABT, CSCO, AXP, BX, MCD, PEP, PM, INTU, GS, TXN, MS, LIN, DHR, NEE, SYK, AMGN, BMY, UBER, UPS, T, LOW, BKNG, MDT, VRTX, LMT, C, REGN, SBUX, BA, NKE, CVS, ISRG, PLD, GILD, TJX, MCO, HCA, GM, SPGI, ZTS, BLK, ELV, PNC |
| Sector & Broad ETFs | SPY, QQQ, IWM, TQQQ, XLK, XLF, XLE, XLI, XLV, XLC, XLP, XLRE, XLU, XLB |
| 3× Bull Leveraged ETFs | UPRO, SPXL, SOXL, TECL, FAS, TNA, LABU, WEBL, FNGU, NAIL, DPST, YINN, DRN, TMF, HIBL, MIDU, GUSH, NUGT, JNUG |
| 3× Bear / Inverse Leveraged ETFs | SQQQ, SPXS, SPXU, SOXS, TECS, FAZ, TZA, LABD, FNGD, YANG, DRV, TMV, HIBS, SRTY, DRIP, DUST, JDST |
| 2× Leveraged Pairs | SSO/SDS, QLD/QID, UCO/SCO, ROM/REW, UWM/TWM |

### Test Users

| Name | Email | Plan | Telegram | Notes |
|------|-------|------|----------|-------|
| Kusuma | kusumabh@gmail.com | Pro | 8663290397 | Linked 2026-04-29 |

---

## ⚙️ Configuration (`.env`)

```bash
# ── Core (set) ────────────────────────────────────────────────────────────────
FINNHUB_API_KEY=...
FRED_API_KEY=...
MASSIVE_API_KEY=...              # Polygon.io + dark pool (Massive WebSocket)
ALPACA_API_KEY=...
ALPACA_API_SECRET=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...             # owner fallback DM
JWT_SECRET=...
OWNER_EMAIL=harsh13858@gmail.com

# ── CRITICAL — change before first signup ─────────────────────────────────────
OWNER_PASSWORD=ChangeMe123!      # ❌ CHANGE THIS IMMEDIATELY
APP_URL=http://localhost:8000    # ❌ Set to HTTPS after deploy

# ── Stripe (billing) ──────────────────────────────────────────────────────────
STRIPE_SECRET_KEY=               # ❌ Run stripe_setup.py after setting this
STRIPE_WEBHOOK_SECRET=           # ❌ From Stripe Dashboard → Webhooks
STRIPE_PRICE_BASIC=              # ❌ Auto-filled by stripe_setup.py
STRIPE_PRICE_PRO=                # ❌ Auto-filled by stripe_setup.py

# ── Email — optional (users auto-verified if not set) ─────────────────────────
# SMTP_HOST=smtp.sendgrid.net
# SMTP_PORT=587
# SMTP_USER=apikey
# SMTP_PASSWORD=SG.your_key
# SMTP_FROM=noreply@yourdomain.com
# SMTP_FROM_NAME=Signal.Trade

# ── OAuth — optional ──────────────────────────────────────────────────────────
# GOOGLE_CLIENT_ID=
# GOOGLE_CLIENT_SECRET=
# DISCORD_CLIENT_ID=
# DISCORD_CLIENT_SECRET=

# ── Web Push — optional ───────────────────────────────────────────────────────
# VAPID_PRIVATE_KEY=             # Generate with py_vapid
# VAPID_SUBJECT=mailto:admin@yourdomain.com

# ── Scale — optional ──────────────────────────────────────────────────────────
# TELEGRAM_BROADCAST_CHANNEL_ID= # Single channel post vs N per-user DMs
# DATABASE_URL=postgresql://...  # Swap SQLite for Postgres
# REDIS_URL=redis://...          # Distributed worker bus
```
