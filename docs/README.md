# Signal.Trade

**Quantitative mean-reversion trading signals — 70+ independent indicators, 23-year backtested MR strategy (IS Sharpe 0.37 with L7+L8 sizing), multi-user Telegram delivery, full subscription stack, and institutional performance analytics.**

> **v10.8+v8.2** · 1871 tests passing (ex-e2e) · PostgreSQL primary · TSYS-1→13 complete · QENG roadmap complete · IS N=155 trades/23yr (Sh=0.25 with L7 score-band sizing + MR-count-2, survivorship-corrected + §63 ADF gate), OOS Sharpe=0.16 · Forward Sharpe est. 0.13–0.20 · cross-sectional L/S net +0.347 (h=21, SHADOW)
> Not financial advice. For informational and educational purposes only.

---

## The Goal: From Research to Live Automated Trading

Signal.Trade is built as a complete pipeline that starts with research signals and ends with
**broker-executed trades**. The north-star is unattended, risk-controlled live trading:

1. **Research & backtest** — validate mean-reversion edge on 23 years of data.
2. **Paper trade** — run the engine against Alpaca/IBKR paper accounts until live win rate is stable.
3. **Shadow/live validation** — compare broker fills to signal assumptions and verify decay monitors.
4. **Live auto-execution** — enable broker auto-execute with strict per-trade and daily risk limits.

> **Current status:** Live delivery is active; broker auto-execution is implemented but should remain on
> **paper until the live win rate is consistently above 55%**. See [Signal Validation](SIGNAL_VALIDATION.md)
> and [Runbook](RUNBOOK.md) §7 for the go-live checklist.

---

## What it is

Signal.Trade is a personal quant desk that:

- **Scans ~107 IS-validated tickers** continuously (09:30–16:00 ET) using 70+ independent signals across 15 categories
- **Scores each signal** into a calibrated confidence rating (40–55%) — ceiling post-cal v4 (Brier 0.2641)
- **Classifies trading style** (intraday / swing / position) from the actual rationale composition — not a heuristic flag
- **Delivers high-confidence BUY/SELL signals** via Telegram with entry, stop, target, R:R, and plain-English explanation
- **Applies structural market invariants** — VIX hard floor, risk-free rate yield dampener, VWAP liquidity filter, earnings blackout, sector peer confirmation, and correlation-based portfolio limits
- **Auto-expires stale signals** — intraday signals die at market close, swing in 10 days, position in 30
- **Mines factor weights weekly** — brute-forces all source combos by out-of-sample Sharpe; re-weights the engine automatically
- **Tracks calibration** — plots "what we said" vs "how often we were right" in a reliability diagram
- **Supports multi-user Telegram fan-out** with per-user confidence thresholds
- **Runs full subscription billing** via Stripe (Free / Basic $29 / Pro $79)

---

## Quick Start

```bash
# 1. Clone and install
cd TradingRecommendationSystem/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Start PostgreSQL (local dev)
brew install postgresql@16 && brew services start postgresql@16
psql postgres -c "CREATE USER signal WITH PASSWORD 'signal_dev_pw' SUPERUSER;"
psql postgres -c "CREATE DATABASE signal_trade OWNER signal;"

# 3. (Optional) Install Playwright for the Finviz news fallback scraper
playwright install chromium

# 4. Configure (minimum viable setup)
cp ../.env.example .env
# Edit .env — set FINNHUB_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
#              JWT_SECRET, OWNER_EMAIL, OWNER_PASSWORD
# DATABASE_URL is pre-filled for local Homebrew Postgres

# 5. Start
uvicorn main:app --reload --port 8000

# 5. Open
open http://localhost:8000        # marketing landing page
open http://localhost:8000/app    # dashboard (login required)
open http://localhost:8000/hub    # design hub (all surfaces)
open http://localhost:8000/mobile # mobile PWA
open http://localhost:8000/design # iOS 26 design canvas
```

> **Owner account** is auto-created from `OWNER_EMAIL` / `OWNER_PASSWORD` on first startup.
> If SMTP is not configured, new users are auto-verified — no blocked signups in dev.

---

## Live Trading Readiness

Before connecting real money, complete every item:

| Gate | Requirement | Evidence |
|---|---|---|
| **Paper track record** | ≥100 resolved signals or ≥3 months of paper trading | `BrokerOrder` table with `account_type='paper'` |
| **Live win rate** | > 55% on clean delivered BUY signals | `/api/admin/live-wr-stats` |
| **Calibration** | Brier score ≤ 0.30 and confidence gap ≤ 10pp | Backtest → Calibration tab |
| **Drawdown tolerance** | Max expected DD < 10% of account | Simulated Returns panel, position sizing ≤ 5% |
| **Risk limits set** | `max_daily_orders`, `max_ticker_notional`, `auto_execute_qty_dollars` | User record / admin panel |
| **Kill switch tested** | `POST /api/admin/signals/pause` works from your phone | Runbook §5.2 |
| **Broker connection verified** | Alpaca/IBKR status returns `connected: true` | `/api/me/broker/status` |
| **Risk acknowledged** | `POST /api/me/risk-acknowledge` recorded | DB `risk_acknowledged_at` |

**Recommended first live settings:**
- `auto_execute_qty_dollars = 100`
- `min_conf = 75`
- `max_daily_orders = 3`
- `max_ticker_notional = 500`
- Keep ≥ 90% of account in cash initially.

See [HOWTO.md](HOWTO.md) §10+ for broker connection steps and [RUNBOOK.md](RUNBOOK.md) §7 for operational procedures.

---

## Pages

| URL | Description |
|-----|-------------|
| `/` | Marketing landing — 11-page React SPA (hero, pricing, track record, docs, auth) |
| `/hub` | Design hub — overview of all three surfaces with thumbnails |
| `/app` | Main dashboard — signal feed, charts, backtest, paper trading |
| `/mobile` | Mobile PWA — Feed, Watchlist, Portfolio, Account, Notifications, Paywall |
| `/design` | Design canvas — 8 iOS 26 Liquid Glass screens on a pan/zoom canvas |
| `/login` | Sign-in (Google OAuth, email/password) |
| `/signup` | Registration with plan picker → Stripe Checkout |
| `/track-record` | Public win-rate scorecard (no auth required) |
| `/tos` | Terms of Service |
| `/privacy` | Privacy Policy (GDPR + CCPA) |

---

## Signal Engine — 50+ Blocks

### Core Indicators (Technical)

| Category | Indicators |
|----------|-----------|
| **Oscillators** (capped ±28) | RSI(14), Stochastic %K/%D, Williams %R, CCI(20), MFI(14) |
| **Trend / Momentum** | MACD histogram + zero-line cross, EMA 8/21, ROC(10), ADX+DI |
| **Mean Reversion** | Z-score (2σ, 2.5σ), Bollinger touch + squeeze + %B |
| **Moving Averages** | 200-DMA gate, 50/200 golden/death cross, SMA20 streak |
| **VWAP** | 20-day rolling VWAP; below → liquidity headwind penalty; above → confirmation bonus |
| **Price Structure** | 52-week proximity, pivot S1/R1, candlestick patterns (hammer, engulfing, shooting star, doji), HH/HL |
| **Volume** | OBV trend, RVOL, ADR compression, short squeeze (>20% float AND >5 DTC), CMF stealth accumulation |
| **Regime Detection** | Supertrend(7,3), Hurst Exponent (H>0.6=trend, H<0.4=mean-revert), Keltner Channels, Fractal Dimension Index |
| **Multi-timeframe** | 1H RSI/MACD/EMA20; all aligned=×1.08, contradicts=×0.82; weekly SMA20 |

### External Data Sources

| Source | What it checks |
|--------|---------------|
| **Options Flow** | Multi-expiry sweeps (3 expiries), OTM spike, IV term structure, IV Rank, 25-delta skew, Gamma Exposure |
| **13F Institutional** | 15 top funds (Berkshire, Viking, Tiger…); new/increased/decreased positions; **QoQ trend**: 2+ consecutive quarters rising = ×1.5 score boost, falling = early-exit warning |
| **News** | Finnhub (age-decayed) + Seeking Alpha RSS + Reuters via Google News + Finviz table; merged and deduplicated; Playwright chromium fallback for Finviz |
| **Analyst** | Consensus buy/hold/sell counts, price target upside, recommendation revision trends |
| **Insider (Form 4)** | SEC EDGAR cluster buys/sells, 30-day window |
| **Earnings** | 4-tier proximity suppression; **hard blackout ≤2d** (forces HOLD regardless of technicals); surprise history |
| **Cointegration / Pairs** | 14 pre-defined pairs (NVDA/AMD, MSFT/GOOGL, JPM/BAC…); OLS spread, z-score ≥2σ, 60-day rolling Pearson ≥0.70 |
| **Relative Strength** | 1M vs SPY, 1M vs sector ETF (11 GICS); sector RS trap filter |
| **Market Sentiment** | CNN Fear & Greed, CBOE P/C (contrarian + directional), Breadth (%>SMA50/200), NAAIM, CFTC COT |
| **Social** | StockTwits bull%, Reddit WSB velocity (7d/1d), Google Trends |
| **Macro** | VIX regime, VIX term structure, 10Y yield, yield curve, SPX 50-DMA, HYG, Fed Funds, CPI, DXY (sector-conditional), Copper/Gold |
| **Fundamentals** | Piotroski F-Score, FCF yield, revenue growth, ROE trend, dividend yield gap, buyback yield |
| **Congressional** | Quiverquant 90-day purchase/sale counts |

### Structural Market Invariants

These run as post-processing gates on every signal, regardless of technical score:

| Invariant | Logic |
|-----------|-------|
| **Risk-Free Rate Dampener** | Projected return (entry→target) must clear 10Y Treasury + sector risk premium (+3.5pp high-beta, +2.0pp others). Below risk-free → −14pp confidence |
| **VIX Gates** | VIX < 15 → MR entries suspended (too calm for fear-driven bounces). VIX > 20 required for MR entry (§9b). VIX > 25 → marginal signals blocked. VIX > 30 → extreme filter |
| **VWAP Binary Filter** | Price >2% below 20-day VWAP on BUY → liquidity headwind penalty (1pt/%, capped −12). Exemption for RSI < 35 |
| **Earnings Hard Blackout** | ≤2d to earnings → score zeroed → forced HOLD regardless of technical strength |
| **Sector Peer Confirmation** | BUY with <2 of 3 sector peers also bullish → −6pp (1 peer) or −12pp (0 peers) confidence haircut |
| **Correlation Portfolio Limits** | Sector exposure >30% → confidence haircut up to 25%; >50% → BUY forced to HOLD |

### Meta-Analysis

- **Orthogonalization caps**: MA ±22, trend ±18, volume ±16, oscillator ±28
- **Orthogonality bonus**: +pts per independent confirming source (configurable via Engine Bias panel)
- **Cluster boost**: ≥6 source categories agree → up to 12% boost — **auto-halved when ticker historical win rate <50%**
- **Per-ticker win-rate gating**: NVDA at 43% win rate → cluster boost is halved automatically
- **Factor mining calibration**: Weekly OOS-Sharpe ranking of source combos feeds ±3pt adjustments
- **Regime-conditional weighting**: Bear market → BUY haircut; bull → SELL haircut
- **VIX-dampened adaptive weights**: Historical win rate nudges confidence, dampened 40-80% when VIX>20

### Confidence Calibration

The engine uses a calibrated confidence scale. Post-calibration v4 (2026-06-01, Brier=0.2641): **all live signals are <55% confidence** (min_confidence=40%). The `⚠ CALIB` badge fires when confidence exceeds empirical win rate by >20pp. Post-signal calibration uses isotonic regression (preferred) or Platt bin-blend. IS backtest win rate: 70.7%. Live win rate (phantom-win corrected): 42.5%.

```
confidence ≈ sigmoid(score) → isotonic-calibrated → capped empirically
```

---

## Style Classification

Style is derived from **what actually fired in the rationale**, not a heuristic flag:

| Style | Triggers |
|-------|---------|
| **Intraday** | RSI oversold/overbought, Bollinger Band touch, RSI divergence, Stochastic cross in extremes, Williams %R extreme |
| **Position** | Piotroski F-Score ≥7, Strong FCF Yield, Active Buyback, Institutional conviction (13F score >5) |
| **Swing** | Everything else (MACD crossovers, Supertrend flips, EMA crosses, volume surges) |

---

## Watchlist (154 Tickers)

| Theme | Count | Key names |
|-------|-------|-----------|
| AI Infra / Semis | 21 | NVDA, AMD, AVGO, SMCI, ALTR, AMKR, COHR, LATT, POWI, PSTG, KEYS |
| Industrial Rotation | 14 | GE, CAT, HON, ETN, PWR, TT, URI, AME, RTX, DE |
| Commodities / Real Assets | 17 | GLD, GDX, FCX, SCCO, AEM, NEM, XOM, CVX, SLB |
| Software / Next-Gen | 10 | PLTR, CRM, NOW, SNOW, MDB, DDOG, NET, PANW |
| Mega-cap Core (S&P 100) | 78 | AAPL, MSFT, AMZN, GOOGL, META, TSLA, JPM, LLY… |
| Sector & Broad ETFs | 14 | SPY, QQQ, IWM, XLK, XLF, XLE, XLI, XLV, XLC… |

Seeded automatically on fresh deployment via `_ensure_default_watchlist()`.

---

## Subscription Tiers

| Tier | Price | Features |
|------|-------|---------|
| **Free** | $0 | View signals in dashboard, market context |
| **Basic** | $29/mo | + Telegram delivery, backtest analytics, custom watchlist, signal history |
| **Pro** | $79/mo | + Paper trading, correlation matrix, predictive intervals, sector heatmap, calibration dashboard, simulated backtest |

Run `python3 stripe_setup.py` to create Stripe products and auto-fill `.env`.

---

## Architecture

```
TradingRecommendationSystem/
├── backend/
│   ├── main.py                   FastAPI app, lifespan, background jobs
│   │                             (periodic scan, weekly digest, weekly factor mining,
│   │                              nightly signal cleanup)
│   ├── models.py                 SQLAlchemy models (Signal, User, RefreshToken,
│   │                             SignalDelivery, WatchlistItem, AppSettings…)
│   ├── config.py                 Settings, tier definitions, feature gates.
│   │                             All secrets use pydantic.SecretStr; no hardcoded
│   │                             JWT fallback. JWT_SECRET is required in production.
│   ├── database.py               PostgreSQL (asyncpg, pool_size=10) or SQLite WAL fallback;
│   │                             loads .env at import time so DATABASE_URL is always available.
│   │                             Does NOT auto-commit; callers own transaction boundaries.
│   ├── data/
│   │   └── factor_weights.json   Weekly-mined OOS-Sharpe source rankings
│   ├── routers/
│   │   ├── auth.py               JWT, refresh cookies, GDPR deletion
│   │   ├── billing.py            Stripe checkout, webhook, portal, live status
│   │   ├── signals.py            Signal CRUD, backtest, calibration, factor-mining
│   │   ├── accuracy.py           Win rate per source / per ticker
│   │   ├── market.py             F&G, macro, calendar
│   │   ├── quotes.py             OHLCV, sector heatmap, sector detail
│   │   ├── paper_router.py       Alpaca paper trading. All endpoints require auth;
│   │                             POST /orders requires Pro tier (or owner).
│   │   ├── watchlist_router.py   Watchlist CRUD
│   │   ├── admin.py              Owner-only: users, MRR, setup status
│   │   ├── oauth.py              Google OAuth2 with PKCE
│   │   └── websocket_router.py   Real-time /ws push; requires valid access token
│   └── services/
│       ├── signal_engine.py      50+ block scoring engine; style from rationale;
│       │                         structural invariants; sector peer confirmation
│       ├── scanner.py            Scan loop, per-ticker win rates, weight overrides,
│       │                         factor weights, portfolio exposure limits
│       ├── factor_miner.py       Weekly OOS-Sharpe brute-force factor ranking
│       ├── cointegration.py      Pairs trading: OLS spread, z-score, Pearson gating
│       ├── news_scraper.py       Seeking Alpha RSS + Reuters + Finviz (Playwright)
│       ├── institutional.py      13F SEC EDGAR XBRL (3-quarter QoQ delta)
│       ├── technicals.py         28 indicators incl. 20-day rolling VWAP
│       ├── options.py            Multi-expiry sweeps, IV, Greeks
│       ├── market_data.py        yfinance batch fetch + caching
│       ├── sector.py             Sector ETF relative strength (154-ticker map)
│       ├── auth_svc.py           JWT, bcrypt, tier gating
│       ├── broker_svc.py         Credential encryption (scrypt KDF v2 + per-credential salt),
│       │                         drawdown circuit breaker, auto-execution
│       ├── redis_cache.py        Redis with in-memory fallback; asyncio.Lock for
│       │                         in-memory lock fallback (TSYS-13c)
│       ├── email_svc.py          Transactional SMTP
│       └── …
├── app.jsx                       Dashboard React SPA (~4000 lines)
│                                 Signal feed, backtest, calibration tab,
│                                 sortable tables, sector drill-down, rules editor,
│                                 paper trading, engine bias controls
├── site.jsx                      Marketing website — 11-page React SPA
├── mobile.jsx                    Mobile PWA — 8 screens
├── styles.css                    Dashboard design-system CSS
├── landing.html / app.html       Entry points
├── login.html / signup.html      Auth pages (Google + email)
├── Dockerfile / docker-compose.yml
├── railway.toml / fly.toml       Deployment configs
├── .env.example                  All variables documented
├── stripe_setup.py               One-time Stripe product creation
└── PROGRESS.md                   Full feature log + remaining TODOs
```

> **New in this refactor:** all API success responses are moving to a unified
> envelope helper, `ApiResponse[T]`, so clients can rely on a consistent
> `{success, data, error, meta}` shape. See `backend/routers/` usage for examples.

---

## Environment Variables

See `.env.example` for the full reference. Minimum to run locally:

```bash
FINNHUB_API_KEY=...          # Free tier: 60 req/min
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...         # Your personal chat ID (owner fallback)
JWT_SECRET=...               # python3 -c "import secrets; print(secrets.token_hex(32))"
OWNER_EMAIL=you@email.com
OWNER_PASSWORD=YourPassword!

# Database (local Homebrew Postgres — pre-filled in .env.example)
DATABASE_URL=postgresql://signal:signal_dev_pw@127.0.0.1:5432/signal_trade
# Production: set to Railway/Fly.io/Neon/Supabase managed URL

# Optional (app works without these)
ALPACA_API_KEY=...           # Paper trading
ALPACA_API_SECRET=...
FRED_API_KEY=...             # Macro indicators (yield curve, CPI)
SMTP_HOST=...                # Transactional email (users auto-verified without it)
STRIPE_SECRET_KEY=...        # Billing (subscription tiers work without it in dev)
STRIPE_WEBHOOK_SECRET=...    # whsec_... from Stripe dashboard (required for paid subs)
GOOGLE_CLIENT_ID=...         # OAuth
```

---

## Deploy

### Railway (recommended — `railway.toml` pre-configured, ~$5/mo)

```bash
railway login && railway init && railway up
railway add --plugin postgresql          # DATABASE_URL auto-injected
railway variables set JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
railway variables set OWNER_EMAIL=you@example.com OWNER_PASSWORD=StrongPass!
railway variables set FINNHUB_API_KEY=... TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=...
railway variables set APP_URL=https://your-app.up.railway.app
```

After deploy:
1. Run `python3 stripe_setup.py` locally → auto-fills Stripe Price IDs in `.env`
2. In Stripe dashboard: add webhook endpoint `https://your-app.up.railway.app/api/billing/webhook`, listen for `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed` → copy `whsec_...` to `STRIPE_WEBHOOK_SECRET`
3. Register Telegram webhook via Admin → Setup Status
4. Verify all green in Admin → Setup Status

> **Security is auto-configured.** Cookie `Secure` flag and CORS origin lock are derived from `APP_URL` — no extra config needed when deploying to HTTPS.

### Docker Compose (self-hosted)

```bash
cp backend/.env.example backend/.env   # fill required vars
docker compose up -d
```

The `docker-compose.yml` starts a `postgres:16-alpine` service alongside the backend. All data (PostgreSQL + factor weights) lives in a named Docker volume — no manual bind-mount paths needed. The backend waits for Postgres to be healthy before starting.

---

## Key API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/signals` | Active signals (50+ fields) |
| `GET` | `/api/signals/backtest` | Win rate, Sharpe, max drawdown |
| `GET` | `/api/signals/backtest/calibration` | Reliability diagram data |
| `GET` | `/api/signals/factor-mining` | Weekly-mined OOS-Sharpe rankings |
| `POST` | `/api/signals/factor-mining/run` | Trigger immediate factor mining run |
| `GET` | `/api/signals/history` | Filterable by ticker/action/outcome/confidence/date |
| `GET` | `/api/market/sectors` | Sector ETF 1-month heatmap |
| `GET` | `/api/market/sectors/detail` | Per-sector stock list with signal + 1M return |
| `DELETE` | `/api/auth/me` | GDPR erasure (anonymise PII + cancel Stripe) |
| `GET` | `/api/paper/risk` | Portfolio Beta, Sharpe, MaxDD, sector exposure |
| `WS` | `/ws` | Real-time signal + price tick stream |

Full endpoint reference: see `PROGRESS.md → API All Endpoints`.

---

## Legal

⚠️ **Signal.Trade is not financial advice.** All signals are algorithmic outputs for informational and educational purposes only. Signal.Trade is not a registered investment adviser, broker-dealer, or financial planner. Past performance does not guarantee future results. All trading involves substantial risk of loss.

See [Terms of Service](/tos) and [Privacy Policy](/privacy).
