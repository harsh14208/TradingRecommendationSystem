# Signal.Trade — How-To Guide

Everything you need to set up, configure, and use the system day-to-day.

> **Version: v8.8.6+** · Last updated: 2026-06-18

cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000

---

## Table of Contents

1. [Initial Setup](#1-initial-setup)
2. [Starting the System](#2-starting-the-system)
3. [Pages & URLs](#3-pages--urls)
4. [Login & Registration](#4-login--registration)
5. [Understanding the Dashboard](#5-understanding-the-dashboard)
6. [Reading Signal Cards](#6-reading-signal-cards)
7. [The Detail Pane — Charts & Trade Plan](#7-the-detail-pane)
8. [Sending Signals to Telegram](#8-sending-signals-to-telegram)
9. [Linking Telegram (subscriber flow)](#9-linking-telegram)
10. [Paper Trading](#10-paper-trading)
11. [Going Live with Auto-Execution](#11-going-live-with-auto-execution)
12. [Backtesting & Win Rates](#12-backtesting--win-rates)
13. [Outcome Backfill](#13-outcome-backfill)
14. [Track Record (per-ticker)](#14-track-record)
15. [Signal Correlation Matrix](#15-signal-correlation-matrix)
16. [Predictive Confidence Intervals](#16-predictive-confidence-intervals)
17. [Sector Heatmap](#17-sector-heatmap)
18. [Watchlist Management](#18-watchlist-management)
19. [Configuring Filters & Rules](#19-configuring-filters--rules)
20. [Position Sizing Calculator](#20-position-sizing-calculator)
21. [Price Alerts](#21-price-alerts)
22. [Mobile App (/mobile)](#22-mobile-app)
23. [Design Hub & Design Canvas](#23-design-hub--design-canvas)
24. [Account Settings](#24-account-settings)
25. [Subscription & Billing](#25-subscription--billing)
26. [Admin Panel (owner only)](#26-admin-panel)
27. [Keyboard Shortcuts](#27-keyboard-shortcuts)
28. [Data Sources & API Usage](#28-data-sources--api-usage)
29. [Environment Variables Reference](#29-environment-variables-reference)
30. [Deploying to Production](#30-deploying-to-production)
31. [Troubleshooting](#31-troubleshooting)
32. [XGBoost ML Confidence Model](#32-xgboost-ml-confidence-model)
33. [Custom Screener Builder](#33-custom-screener-builder)
34. [PostgreSQL Migration](#34-postgresql-migration)
35. [Redis Cache Setup](#35-redis-cache-setup)
36. [CI/CD & Testing](#36-cicd--testing)
37. [Performance Analytics & Snapshots](#37-performance-analytics--snapshots)

---

## 1. Initial Setup

### Prerequisites
- Python 3.11+ (3.14 works)
- A modern browser (Chrome, Firefox, Safari)

### API Keys Needed

| Service | What it unlocks | Where to get it | Cost |
|---|---|---|---|
| Finnhub | News sentiment, analyst trends | finnhub.io → Dashboard | Free |
| Telegram | Signal delivery, error alerts, weekly digest | @BotFather → /newbot | Free |
| FRED | CPI/NFP/FOMC calendar, Fed Funds rate | fred.stlouisfed.org/docs/api | Free |
| Polygon.io | Reliable OHLCV and market data | polygon.io | Free/Paid |
| Alpaca | Real-time tick prices + paper trading | alpaca.markets → Paper Trading | Free |
| Stripe | Subscription billing (only if charging users) | dashboard.stripe.com | Free account |

### Installation

```bash
cd TradingRecommendationSystem/backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configure `.env`

Copy the template and fill in your values:

```bash
cp ../.env.example backend/.env
```

Minimum viable configuration:

```
FINNHUB_API_KEY=your_key_here
TELEGRAM_BOT_TOKEN=1234567890:AAF...
TELEGRAM_CHAT_ID=123456789
JWT_SECRET=<run: python3 -c "import secrets; print(secrets.token_hex(32))">
OWNER_EMAIL=you@example.com
OWNER_PASSWORD=YourSecurePassword
```

> **JWT_SECRET is required.** Without it, a temporary secret is generated per process and all login sessions are invalidated on every restart.

### Setting Up Telegram (5 minutes)

1. Open Telegram → message `@BotFather` → send `/newbot`
2. Follow prompts → copy the **bot token**
3. Search for your bot → click **Start** → send any message
4. Visit `https://api.telegram.org/bot<TOKEN>/getUpdates` → copy `result[0].message.chat.id`
5. Add both to `.env` as `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`

---

## 2. Starting the System

```bash
cd TradingRecommendationSystem/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

The owner account (`OWNER_EMAIL` / `OWNER_PASSWORD`) is auto-created on first startup with Pro tier access.

You'll see in terminal:
```
[startup] owner account created: you@example.com
[startup] sector heatmap pre-warmed
[scanner] F&G = 42 (Fear) | VIX = 18.87 | Macro score = 6
[scanner] history batch: 25/25 tickers loaded
[scanner] 10:15:03 — scanned 25 tickers, 3 new, 22 refreshed
```

First scan results appear ~30 seconds after startup.

---

## 3. Pages & URLs

| URL | Who sees it | Description |
|-----|-------------|-------------|
| `/` | Everyone | Marketing landing page — hero, features, pricing, live stats |
| `/login` | Everyone | Sign-in page with live signal preview on the left |
| `/signup` | Everyone | Registration: pick plan → create account → Stripe (if paid) |
| `/hub` | Anyone | Design hub — overview of all three surfaces with thumbnail previews |
| `/app` | Logged-in users | Main dashboard — three-pane layout |
| `/mobile` | Logged-in users | Mobile PWA — tab bar navigation |
| `/design` | Anyone | Design canvas — all 8 screens in iOS 26 Liquid Glass frames |
| `/track-record` | Everyone | Public win-rate scorecard, no login required |
| `/tos` | Everyone | Terms of Service |
| `/privacy` | Everyone | Privacy Policy (GDPR + CCPA) |

---

## 4. Login & Registration

### First time

1. Go to `/signup`
2. **Step 1 — Choose plan**: Free (view only), Basic ($19/mo, Telegram + backtest + paper trading), Pro ($49/mo, all features + analytics), Elite ($99/mo, early access + API). Select one, click Continue.
3. **Step 2 — Create account**: Enter name (optional), email, password (min 8 chars). Click "Create account".
4. If you chose a paid plan, you're redirected to **Stripe Checkout** to enter card details.
5. On success you land at `/app`.

### Returning users

Go to `/login` or `/app` (auto-redirects to login if no session).

### Owner account

The owner bypasses all tier gates and gets full access (all tiers) automatically. The password is set in `.env` as `OWNER_PASSWORD`. **Change it on first login**: Account Settings → Security → Change Password.

---

## 5. Understanding the Dashboard (`/app`)

```
┌────────────────────────────────────────────────────────────────────┐
│  Top bar: brand · search · ticker tape · status chips · avatar     │
├──────────┬──────────────────┬──────────────────┬────────────────── ┤
│          │                  │                  │  Delivery log      │
│ Sidebar  │  Signal Feed     │  Detail / Chart  │  ── or ──          │
│  (nav)   │  (left pane)     │  (center pane)   │  Simulated Returns │
│          │                  │                  │  (on Full detail)  │
├──────────┴──────────────────┴──────────────────┴───────────────────┤
│  Status bar: CONNECTED · SOURCES · SIGNALS · TG SENT · MODE        │
│  Disclaimer bar: NOT FINANCIAL ADVICE · ToS · Privacy              │
└────────────────────────────────────────────────────────────────────┘
```

**Sidebar nav groups:**
- **Workspace**: Live signals, History, Backtest
- **Configure**: Sources, Rules & filters, Threshold
- **Account**: Your name + tier badge, Upgrade (if free/basic)

Click any sidebar item to open the corresponding overlay. Click Live signals to return to the three-pane layout.

**Top bar elements:**

| Element | Meaning |
|---|---|
| Ticker tape | Live prices (green = up, red = down) |
| NYSE OPEN / CLOSED | Market status |
| Clock | Current time ET |
| ↺ Refresh | Trigger a manual scan |
| ⚙ Gear | Opens Tweaks panel |
| Avatar | Opens Account Settings |
| ⌘K search | Live filter by ticker or company name; Escape clears; × button resets |

---

## 6. Reading Signal Cards

Each signal card shows:

```
🟢 BUY  NVDA  [swing]  · Price likely to rise — consider buying
"Breakout above 200-DMA + call sweep detected"
                                              82%   09:31  ›
```

**Expand a card** — click it to reveal:
- Current price and day change
- Confidence % with glossary tooltip
- Full headline
- Entry / Stop / Target / R:R stats
- Action buttons: Full detail → | Telegram | Skip

**Signal dot colours:** Green = BUY · Red = SELL · Yellow = HOLD

**Style badges:** `swing` · `position`

> **Note:** `intraday` style requires ≥68% confidence (restored from fully disabled as of v5.8). Historical validation shows 34.8% win rate (PF 0.73x) — quality improvement in progress. Only very high-confidence intraday setups pass the 68% floor (max possible confidence is 72%).

**Suppressed signals** (below your confidence threshold) appear in a grey section below the main feed with a count badge.

---

## 7. The Detail Pane

Click a signal card to expand it, then click **Full detail →** to populate the center pane with full analysis and open the **Simulated Returns** panel on the right.

**Center pane sections:**
1. **Hero row** — ticker, company, action badge, price, day change
2. **Meta row** — confidence %, R:R, sentiment score, sources
3. **Plain-English box** — one-paragraph summary any trader can understand
4. **Probability of Success** — Bayesian P(win) at 1d/3d/7d/14d with percentile bands
5. **SVG chart** — 90-day price history with SMA20 overlay, entry/stop/target lines. Switch between Line / Area / Candles in Tweaks.
6. **Rationale list** — each contributing signal with abbreviated source badge (hover for full name), headline, body, and sentiment tag
7. **Trade plan** — Entry / Stop / Target cards with percentage loss/gain + visual R:R bar
8. **Action row** — Send to Telegram · Skip · Mark reviewed

**Right pane — Simulated Returns** (replaces Delivery Log when Full detail is open):

Adjust the three sliders to model different scenarios:

| Control | Default | What it does |
|---|---|---|
| Starting Capital | $10,000 | Total account size for the simulation |
| Position Size | 5% | Percentage of capital risked per trade |
| Trades to Simulate | 50 | Monte Carlo sample size |

The panel shows:
- **Total Return** — simulated P&L over N trades
- **Final Capital** — ending equity
- **Win Rate** — % of trades profitable (derived from confidence score)
- **Max Drawdown** — largest peak-to-trough loss during simulation
- **Equity curve** — live SVG chart that redraws as you drag sliders
- **Signal inputs** — the win probability, R:R, and per-trade EV used

Click **×** in the Simulated Returns header to restore the Delivery Log.

---

## 8. Sending Signals to Telegram

**Manual send** — click "Send to Telegram" in the action row or `s` keyboard shortcut.

**Auto-send** — set `AUTO_SEND_NOTIFICATIONS=true` in `.env`. Signals are auto-sent when:
- Confidence ≥ `MIN_CONFIDENCE` (default 55%)
- Profit potential ≥ 2%
- Market hours (10:00–15:30 ET)
- No duplicate for same ticker+action in past 24h

Every Telegram message includes:
- Action, ticker, price, confidence, R:R
- Entry / stop / target
- Plain-English summary
- Full legal disclaimer

**Weekly digest** — every Sunday 8am ET, a Telegram summary of the week's signals, win rate, and avg return is sent automatically. On `http://localhost` / `http://127.*` URLs the digest is suppressed by default (both auto and manual sends) to avoid spamming your real Telegram chat while developing. Set `WEEKLY_DIGEST_ALLOW_DEV=true` in `.env` to test digest delivery locally.

---

## 9. Linking Telegram

For **subscribers** to receive signals, they must link their personal Telegram:

1. User goes to `/app` → Account Settings → Telegram Alerts section
2. They see a unique link code (e.g. `A1B2C3D4`)
3. They open your Signal.Trade bot on Telegram and send:
   `/start A1B2C3D4`
4. The bot confirms: "✅ Telegram linked to Signal.Trade!"
5. From the next scan onwards, they receive signals automatically

**To register the bot webhook** (one-time setup after deploying to public HTTPS):
- Account Settings → Admin → "Register TG Webhook"
- Or call: `POST /api/telegram/set-webhook`

---

## 10. Paper Trading

Paper trading simulates real trades through Alpaca's paper account.

**Requires**: `ALPACA_API_KEY` and `ALPACA_API_SECRET` for a **paper** account (not live).

The UI exposes three isolated paper books, each with its own Alpaca paper credentials:

| Book | Env keys | Purpose |
|------|----------|---------|
| Equity | `ALPACA_API_KEY` / `ALPACA_API_SECRET` | Manual/auto equity paper trades and portfolio analytics |
| Options | `ALPACA_OPTIONS_API_KEY` / `ALPACA_OPTIONS_API_SECRET` | Dedicated VRP options sleeve; book sized against `options_buying_power` (capped by equity) so it never exceeds the account's option-buying limit |
| COT / Signal Engine | `ALPACA_SE_API_KEY` / `ALPACA_SE_API_SECRET` (or lowercase `alpaca_se_api_key` / `alpaca_se_api_secret`) | Signal-engine shadow book shown in the COT Engine tab |

All three use Alpaca's paper endpoint (`paper-api.alpaca.markets`). Keep live keys out of these fields.

### Manual paper trade
1. Click "Paper Trade" button in the action row (requires Basic)
2. Enter quantity, choose market/limit
3. Review cost, stop, target — click Execute

### Auto paper trading
- Toggleable in Account Settings
- Runs alongside Telegram sends — every signal that passes auto-send rules also places a paper order
- Notional sizes: $500 / $1k / $2k / $5k per trade (configurable), or a % of account cash via `paper_trade_equity_pct`
- **Cash-secured / no margin**: equity buys are sized against `non_marginable_buying_power` (cash), and SELL signals from the main long-only engine only close existing long positions — naked short selling is disabled for that book. The cross-sectional (XS-h63) sleeve is the one exception: it's a genuine dollar-neutral long/short book, so its SELL entries open real shorts, sized against margin buying power

### Uninvested cash
By default, idle cash in all paper accounts simply sits in the Alpaca paper account (no sweep/interest). The optional residual-cash overlay (`CASH_OVERLAY_ENABLE=true`) can deploy idle cash into `SGOV` / `VOO`, but it is **disabled by default** and currently wired to the live portfolio allocator, not the paper books.

### Portfolio view
Open from sidebar or mobile → Paper tab:
- Total equity, day P&L, buying power
- Open positions with unrealized P&L
- Order history (filled / cancelled / pending) — equity orders come live from Alpaca; option orders come live from Alpaca and are enriched with strategy metadata from `broker_orders`, so resetting the options paper account automatically clears the list
- **Risk dashboard**: Beta vs SPY, Sharpe ratio (account history, excess return over `RISK_FREE_RATE`), Max Drawdown, Exposure %

---

## 11. Going Live with Auto-Execution

Once paper trading proves an edge, you can let the engine place real-money orders through Alpaca or IBKR.

### 11.1 Paper → live graduation criteria

Do **not** connect live keys until all of these are true:

- ≥ 100 resolved paper trades or ≥ 3 months of paper trading
- Clean live win rate > 55% on delivered BUY signals
- Brier score ≤ 0.30 and calibration gap ≤ 10pp
- You have personally tested the kill switch (`POST /api/admin/signals/pause`)

### 11.2 Connect live broker account

1. Create a live account at Alpaca (or fund IBKR).
2. Generate live API keys from the broker dashboard.
3. In Signal.Trade, go to **Account Settings → Broker Connection** (requires Pro).
4. Acknowledge risk: the UI calls `POST /api/me/risk-acknowledge`.
5. Enter live keys and click **Connect**. The system verifies the account status before saving.

### 11.3 Enable auto-execute with conservative settings

Recommended first-live settings:

| Setting | Value | Why |
|---|---|---|
| Auto-execute | On | Only after paper validation |
| Min confidence | 75% | Highest-confidence tier only |
| Notional per trade | $100 | Tiny size while validating live fills |
| Max daily orders | 3 | Limit bad-day damage |
| Max ticker notional | $500 | No single ticker can dominate |

These are stored on the user record and enforced in `services/broker_svc.py`.

### 11.4 What happens when a signal fires

1. Scanner generates a signal.
2. Delivery gates check confidence, MR-count, sector, time-of-day.
3. For users with `auto_execute=True`, `broker_svc.execute_signal_for_user()` runs:
   - Decrypt broker keys.
   - Check portfolio drawdown (< −5% blocks).
   - Check daily/ticker limits.
   - Check slippage/capacity.
   - Submit bracket-stop order.
   - Record `BrokerOrder`.
4. You receive a Telegram alert with the order details.

### 11.5 Monitoring live trades

- **Broker status:** `/api/me/broker/status`
- **Order history:** `/api/me/broker/orders`
- **Live win rate:** `/api/admin/live-wr-stats`
- **Reconciliation:** run `python scripts/reconcile_broker_orders.py` daily

If live win rate drops below 50%, disable auto-execute and return to paper/analysis.

---

## 12. Backtesting & Win Rates

Go to **Backtest** in the sidebar (requires Basic plan).

**Research tab:** *(new in v8.9)*
- Canonical 23-year in-sample backtest (v10.9 canon): N=217, WR=69.1%, Sharpe=0.24, MaxDD −2.31%
- Monthly equity curve from `scripts/backtest_technicals.py`
- Honest disclosure of the IS/live gap and why live results differ
- API: `GET /api/signals/backtest/research`

**Summary tab:**
- Win rate, avg return, avg win/loss
- Sharpe ratio, max drawdown, Calmar ratio, estimated annual return
- Breakdown by: signal direction, source, confidence tier, trade style
- Top 5 / worst 5 signals

> **Performance note:** The backtest summary is pre-computed after every scan cycle and served from cache. For unfiltered requests the response is typically instant (no live GROUP BY query).

**By Horizon tab:**
- Win rate, avg return, Sharpe at 1-day / 3-day / 7-day / 14-day hold periods
- Bar chart comparing hold periods (helps you identify your natural exit timing)

**Calibration tab:**
- Reliability diagram: predicted confidence vs actual win rate per 5pp bucket
- Gap column highlights overconfident (red) and underconfident (green) buckets
- Well-calibrated model has all dots near the diagonal

**OOS (Out-of-Sample) tab:** *(new in v5.3)*
- Walk-forward validation: chronological 60/40 train/test split
- OOS win rate, avg return, annualised Sharpe — the only honest measure of persistent alpha
- Up to 6 rolling 30-day windows showing per-period performance
- API: `GET /api/signals/backtest/oos`

**Simulator tab:** *(new in v8.9)*
- Replay historical sent signals with realistic execution
- Date-range filter, entry policy (market / next-open / limit), and trade cap
- Equity curve, CAGR, Sharpe, max drawdown, cost drag, exit-reason breakdown
- API: `GET /api/signals/backtest/simulate?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&entry_policy=market|limit|next_open&max_signals=200`

> The backtest shows data as soon as any outcome (1d, 3d, 7d, or 14d) is resolved. You don't need to wait 7 days. If no live signals are resolved yet, the Research tab and Simulator still provide full historical evidence.

---

## 13. Outcome Backfill

Signal outcomes are recorded automatically as they age (1d after 1 day, 3d after 3 days, etc.). If you missed some historical outcomes, you can backfill them:

1. Open Backtest → click **"Backfill Outcomes"** button
2. The system fetches actual historical close prices from yfinance for every past signal
3. Fills in any missing 1d/3d/7d/14d outcomes retroactively
4. Stats refresh automatically

This is also available via API: `POST /api/signals/backtest/backfill`

---

## 14. Track Record

The **per-ticker** performance view is in the Archive section of the sidebar.

Shows: win rate, avg return, Sharpe ratio, best trade, worst trade — for every ticker that has at least 3 resolved signals.

There is also a **public track record page** at `/track-record` that shows aggregate stats with no PII. This is designed to share with potential subscribers to demonstrate performance.

---

## 15. Signal Correlation Matrix

Open **Correlation** from the Archive sidebar group (requires Pro).

Shows which signal sources appear together most often and what their combined win rate is when they co-occur.

Reading the matrix:
- **Count** — how often this source pair appeared in the same signal
- **Win rate** — what % of signals with both sources were profitable (shown only when ≥3 resolved signals)
- **High co-occurrence + high win rate** — these source combinations are your highest-conviction setups

---

## 16. Predictive Confidence Intervals

Shown automatically in the detail pane for every active signal.

The system finds historically similar signals (same action, similar confidence, overlapping sources) and computes:
- **P(success)** — probability of a positive outcome based on similar past signals
- **Expected return** — mean return of similar resolved signals
- **Percentile bands** — 10th / 25th / 75th / 90th percentile outcomes at 1d, 3d, 7d, 14d
- **Calibration indicator** — warns when fewer than 5 similar signals were found (limited data)

---

## 17. Sector Heatmap

Click **Sectors** in the sidebar.

- All 11 GICS sectors shown as colour-coded tiles (green = outperforming, red = underperforming)
- Performance is 1-month ETF return
- **Click any sector tile** → lazy-loads all 50–75 stocks in that sector with: 1M return, current signal action, confidence, price
- Filter bar inside the expanded sector to search by ticker
- Pre-warmed at startup — first open is instant

**680 stocks** are mapped across all sectors. Unknown tickers fall back to ETF classification.

---

## 18. Watchlist Management

Open **Watchlist** from the sidebar.

- Default watchlist: **164 tickers** across large-cap, tech, semis, commodities, sector ETFs
- Add any US ticker: type in the search box (1–5 letters, e.g. `AAPL`) → **Add** button
- Remove a ticker: click the ✕ on any row
- Sort: cycle between Added order, A→Z, Z→A using the Sort button
- Changes take effect on the next scan cycle

**Validation (v5.3):** The input field automatically strips non-alphabetic characters and enforces the 1–5 uppercase letter regex. The backend (`POST /api/watchlist`) also validates on the server side — invalid symbols return a 422 with a clear error message.

API access:
```
GET    /api/watchlist              — list all active tickers
POST   /api/watchlist              — add ticker {"ticker": "AAPL"}
DELETE /api/watchlist/{ticker}     — remove ticker
```

---

## 19. Configuring Filters & Rules

Open **Rules & filters** from the sidebar.

**Trading style** — affects which signals appear in the feed:
- `swing` — days to weeks (default for most signals; covers RSI/MACD/options setups)
- `position` — weeks to months (requires strong fundamentals: Piotroski ≥7, FCF yield, institutional QoQ)

> `intraday` style requires ≥68% confidence (v5.8). Below this floor signals are suppressed. Swing style requires ≥70% confidence. Both thresholds are defined in `services/delivery_gates.py`.

**Aggressiveness** (in Tweaks panel):
- Conservative: 75% confidence threshold, min 2.5 R:R, 4 signals/day max
- Balanced (default): 65% threshold, 2.0 R:R, 8 signals/day max
- Aggressive: 55% threshold, 1.5 R:R, 12 signals/day max

**Active days & time window** — signals outside your chosen window are suppressed (not sent to Telegram but still visible in the feed).

---

## 20. Position Sizing Calculator

Shown in the detail pane below the trade plan for any signal with a stop defined.

Enter:
- **Account size** ($)
- **Risk per trade** (% of account you're willing to lose)

The calculator shows:
- Maximum shares to buy
- Total position cost
- Maximum loss ($ and %)
- Maximum gain if target is hit

---

## 21. Price Alerts

Click the **bell icon** on any signal card or in the detail pane action row.

Set a target price and condition (above / below) → the alert fires a Telegram notification when the live tick crosses it.

- Alerts are stored in the database per user, not just localStorage
- Auto-evaluated on every scan cycle (`alert_evaluator.py`)
- Multiple alerts per ticker are supported
- **Validation (v5.3):** Target price must be > 0 and < $1,000,000. The input shows a red border and inline error for invalid values. Backend enforces the same rules via Pydantic.

API:
```
GET    /api/alerts/          — list your active alerts
POST   /api/alerts/          — create {"ticker":"AAPL","target_price":210.0,"condition":"above"}
DELETE /api/alerts/{id}      — delete alert
```

---

## 22. Mobile App

Visit `/mobile` on your phone, or install as a PWA:
- **iPhone/iPad**: Safari → Share → Add to Home Screen
- **Android/Chrome**: Three-dot menu → Install app (or install prompt appears automatically)

### Mobile tab bar

| Tab | Screen |
|-----|--------|
| Signals | Live signal feed with filter pills (All / BUY / ≥70% conf) |
| Watchlist | Ticker list with live prices and signal badges |
| Paper | Paper portfolio — equity, positions, unrealized P&L |
| Record | Track record — win rate, Sharpe, by-ticker bar chart |
| Account | Profile, tier badge, Telegram status, sign out |

**Signal detail** — tap any signal card → full detail screen with trade plan, rationale, "Send to Telegram" button.

The mobile app fetches real API data when authenticated and falls back to mock data when offline.

---

## 23. Design Hub & Design Canvas

### Design Hub (`/hub`)

A single-page overview of all three Signal.Trade surfaces — Dashboard, Mobile App, and Marketing Website — with live thumbnail illustrations and one-click links. Use it as a starting point for navigating the product.

### Design Canvas (`/design`)

Visit `/design` to see all mobile screens laid out in a pan/zoom Figma-style canvas:

- **Pinch to zoom** (trackpad or touch), **two-finger scroll to pan**
- **Click artboard label** to open full-screen focus overlay
- Use **← →** arrows (or keyboard) to navigate between screens within a section
- Use **↑ ↓** arrows to jump between sections
- **Drag the grip icon** (⠿) above an artboard to reorder within its section
- **Double-click** section title or artboard label to rename inline

**Two sections, eight artboards:**

**Core Screens** — Signal Feed · Signal Detail · Paper Portfolio · Account & Settings

**Auxiliary Screens** — Onboarding · Watchlist · Activity / Notifications · Paywall / Upgrade

Every screen is wrapped in an iOS 26 Liquid Glass device frame with Dynamic Island, status bar, and home indicator.

---

## 24. Account Settings

Click your avatar in the top bar or the account nav item in the sidebar.

**Profile** — edit your display name

**Subscription** — shows your current tier (FREE/BASIC/PRO), renewal date, and upgrade/manage billing buttons

**Telegram Alerts** — shows your unique link code. If already linked, shows "Connected" with an unlink button. Generate a new code if the old one expired.

**Security** — change password (current + new + confirm)

**Legal links** — Terms of Service · Privacy Policy · Track Record

**Sign Out** — clears local auth token and redirects to `/login`

---

## 25. Subscription & Billing

### Creating a subscription

1. Go to `/signup` or Account Settings → Upgrade Plan
2. Choose Basic or Pro
3. Redirected to Stripe Checkout (no card stored on our servers)
4. After payment, tier activates instantly via Stripe webhook

### Managing subscription

Account Settings → **Manage Billing** → opens Stripe Customer Portal where you can:
- Update payment method
- Cancel subscription (access continues until period end)
- View invoices

### Failed payment

If payment fails, status changes to `past_due`. You receive an email and Telegram message. Update your card in Stripe Customer Portal within the grace period to avoid downgrade.

### Signal view quotas

Live signals (`/api/signals`) and signal history (`/api/signals/history`) are
capped per user per UTC day. The cap resets at midnight UTC.

| Tier  | Daily signals | Notes                              |
|-------|--------------:|------------------------------------|
| Free  | 5             | Enough to evaluate quality         |
| Basic | 100           | Covers active retail traders       |
| Pro   | Unlimited     | No cap                             |
| Owner | Unlimited     | Bypass                             |

Quota state is returned in response headers on every request:

```
X-Signal-Quota-Limit: 5
X-Signal-Quota-Remaining: 3
X-Signal-Quota-Resets-At: 2026-06-14T00:00:00Z
```

For unlimited users the first two headers are `unlimited`.
`GET /api/billing/status` also returns a `signal_quota` object with
`limit`, `used`, `remaining`, and `resets_at` so the frontend can render
upgrade prompts without parsing headers.

If a free user exhausts their quota, the API returns **402 Payment Required**
with the message *"Daily signal quota exceeded. Upgrade to Basic or Pro for
more signals."*

### Live WebSocket signals

Real-time `new_signal` pushes over `/ws` are a paid-tier benefit. Free users
still receive `price_update`, `market_context`, and price `tick` messages, but
they must use the REST endpoints (above) to view actual signals, where the
daily quota is enforced.

### Stripe setup (for owner)

```bash
# After adding STRIPE_SECRET_KEY to .env:
python3 stripe_setup.py
# Creates Basic + Pro + Elite products, auto-fills STRIPE_PRICE_BASIC, STRIPE_PRICE_PRO, and STRIPE_PRICE_ELITE
```

---

## 26. Admin Panel (Owner Only)

Available in Account Settings → **Admin** section (only visible when logged in as owner).

**Setup health check** — green/red status for all 12 config items:
- JWT_SECRET, OWNER_EMAIL, Telegram bot, Stripe keys, APP_URL, SMTP

**Stats cards** — total users, active subscriptions, MRR (monthly recurring revenue)

**Register Telegram Webhook** — one-click button to register your bot's webhook URL with Telegram. Required for subscriber `/start <code>` linking to work. Only needed once after deploying to a public HTTPS URL.

**User list** — all registered accounts with email, tier, and last-seen date.

**Weekly Digest** — Manual send button + schedule display + delivery channel status (bot configured, owner Telegram linked, email configured). Also accessible via:
```
GET  /api/admin/weekly-digest/status   — schedule + delivery readiness
POST /api/admin/trigger-weekly-digest  — send digest immediately
```

**Delivery SLA** *(new in v5.3)* — p50/p95/p99 signal delivery latency percentiles and 24h breach count (breach = >5 minutes from signal creation to Telegram delivery):
```
GET  /api/admin/delivery-sla
```

Also accessible via API (owner JWT required):
```
GET  /api/admin/setup-status
GET  /api/admin/users
GET  /api/admin/stats
GET  /api/admin/rate-limits            — cache stats, circuit breaker state, screener suggestions
POST /api/admin/users/{id}/tier        — manually override a user's tier
DELETE /api/admin/users/{id}           — delete user account

# Performance snapshots (v5.8)
GET  /api/admin/snapshots              — list last N snapshots (summary: id, tag, WR, Sharpe)
GET  /api/admin/snapshots/{id}         — full metrics JSON for one snapshot
GET  /api/admin/snapshots/diff/{a}/{b} — field-level delta between two snapshots
                                         response includes flagged_metrics[] for significant regressions
```

---

## 27. Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `j` / `↓` | Next signal in feed |
| `k` / `↑` | Previous signal |
| `Enter` | Expand / collapse selected signal |
| `d` | Toggle Full detail / Simulated Returns panel |
| `s` | Send selected signal to Telegram |
| `p` | Open paper trade dialog for selected signal |
| `Esc` | Collapse expanded signal / clear search |
| `⌘K` | Focus search bar |

---

## 28. Data Sources & API Usage

### Finnhub (free tier)

Limited to 60 API calls/minute. A rolling usage counter appears in the sidebar footer. The scanner automatically rate-limits Finnhub calls with jitter to stay under the limit. If you see `429` errors, they are auto-retried with 3× backoff.

### yfinance (no API key)

Used for OHLCV history, options chains, analyst data, earnings calendars. Subject to Yahoo Finance rate limits. The scanner downloads all 25 tickers in a single batch request. `curl_cffi` with Chrome impersonation is used to avoid detection.

### SEC EDGAR (free, rate-limited at 10 req/sec)

Used for:
- **Form 4 insider trading** — 30-day rolling window
- **13F institutional filings** — 15 top hedge funds, cached for 6 hours per fund

### FRED (free with API key)

Used for: CPI, NFP, and FOMC calendar dates (economic calendar shading on charts).

### CBOE (free, no key)

Daily put/call ratio CSV downloaded once per day. Used as a contrarian sentiment signal.

### Alpaca (free paper account)

- **IEX WebSocket** — real-time price ticks for all watchlist tickers
- **REST API** — paper trading: orders, positions, account details, order history

### Polygon.io (primary data source)

Set via `MASSIVE_API_KEY` (same key as dark pool):

| Endpoint | What it fetches | Tier |
|---|---|---|
| `v2/aggs/ticker/{ticker}/range` | OHLCV history | Free |
| `v2/aggs/ticker/{ticker}/prev` | Fast daily quote | Free |
| `v1/indicators/rsi,macd,sma,ema` | Pre-computed technicals | Free |
| `v2/reference/news` | Licensed news feed | Free |
| `v3/reference/dividends` + `splits` | Corporate events | Free |
| `vX/reference/financials` | SEC financial statements | Free |
| `v1/related-companies/{ticker}` | Peer confirmation | Free |
| `v1/marketstatus/now` | NYSE open/closed | Free |
| `v3/snapshot/options/{ticker}` | Full option chain | Premium |
| `v2/last/trade/{ticker}` | Real-time trade tape | Premium |

The system falls back to yfinance when a Polygon endpoint returns 403 or is unavailable.

### Massive API Catalog

Visit **Workspace → Massive API Catalog** in the sidebar to browse all available Polygon endpoints, search by name/description, and test any endpoint live in the built-in console (proxied via `POST /api/massive/proxy`).

---

## 29. Environment Variables Reference

```bash
# ── Market data ───────────────────────────────────────────────────────────────
FINNHUB_API_KEY=           # Free at finnhub.io — news sentiment, analyst trends
MASSIVE_API_KEY=           # Polygon.io + dark pool (Massive WebSocket) — primary data source
FRED_API_KEY=              # Free at fred.stlouisfed.org — CPI, NFP, FOMC calendar
WATCHLIST=AAPL,MSFT,...    # Comma-separated fallback tickers (DB watchlist takes priority)
SCAN_INTERVAL=60           # Seconds between scans

# ── Notifications ─────────────────────────────────────────────────────────────
AUTO_SEND_NOTIFICATIONS=true
MIN_CONFIDENCE=55.0         # Signals below this are suppressed
TELEGRAM_BOT_TOKEN=         # From @BotFather
TELEGRAM_CHAT_ID=           # Your Telegram user ID (fallback single-user delivery)
TELEGRAM_BROADCAST_CHANNEL_ID=   # Optional: post to channel instead of N per-user DMs
                                  # Required once subscribers exceed ~50 (Telegram 30msg/sec limit)

# ── Paper trading ─────────────────────────────────────────────────────────────
ALPACA_API_KEY=             # Equity paper account keys from alpaca.markets
ALPACA_API_SECRET=

# Separate Alpaca paper accounts (optional — create additional paper accounts at alpaca.markets)
ALPACA_OPTIONS_API_KEY=     # Dedicated options VRP sleeve
ALPACA_OPTIONS_API_SECRET=
ALPACA_SE_API_KEY=          # Signal-engine / COT shadow book (lowercase names also accepted)
ALPACA_SE_API_SECRET=

# ── Auth (required) ───────────────────────────────────────────────────────────
JWT_SECRET=                 # python3 -c "import secrets; print(secrets.token_hex(32))"
OWNER_EMAIL=                # Auto-creates owner account with Pro tier on startup
OWNER_PASSWORD=             # CHANGE THIS — default is public in source

# ── Deployment ────────────────────────────────────────────────────────────────
APP_URL=http://localhost:8000    # Set to public HTTPS URL after deploying

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL=postgresql://signal:signal_dev_pw@127.0.0.1:5432/signal_trade
             # Local dev: Homebrew PostgreSQL (see Section 33 to set up).
             # Production (Railway/Fly.io): set to your managed PostgreSQL URL.
             # Leave blank to fall back to SQLite (not recommended for production).

# ── Redis (optional — in-memory fallback when not set) ────────────────────────
REDIS_URL=redis://localhost:6379
          # When set: shared cache for macro/VIX/fear-greed data across workers.
          # Also enables distributed worker bus (Redis Streams instead of asyncio.Queue).
          # Format: redis://host:port or rediss://user:pass@host:6380 (TLS)

# ── Stripe (billing) ──────────────────────────────────────────────────────────
STRIPE_SECRET_KEY=          # sk_live_... or sk_test_...
STRIPE_WEBHOOK_SECRET=      # whsec_... from Stripe webhook dashboard
STRIPE_PRICE_BASIC=         # Auto-filled by: python3 stripe_setup.py
STRIPE_PRICE_PRO=           # Auto-filled by: python3 stripe_setup.py
STRIPE_PRICE_ELITE=         # Auto-filled by: python3 stripe_setup.py

# ── Email / SendGrid (optional) ───────────────────────────────────────────────
# SMTP_HOST=smtp.sendgrid.net
# SMTP_PORT=587
# SMTP_USER=apikey
# SMTP_PASSWORD=SG.your_key
# SMTP_FROM=noreply@yourdomain.com
# SMTP_FROM_NAME=Signal.Trade

# ── Google OAuth (optional — enables "Sign in with Google") ───────────────────
# GOOGLE_CLIENT_ID=
# GOOGLE_CLIENT_SECRET=

# ── Web Push (optional — VAPID browser notifications) ────────────────────────
# VAPID_PRIVATE_KEY=         # Generate: cd backend && python3 -c "from py_vapid import Vapid; ..."
# VAPID_SUBJECT=mailto:admin@yourdomain.com

# ── Frontend analytics sink (optional) ────────────────────────────────────────
ANALYTICS_ENABLED=true      # Set to false to drop first-party CTA/feature-gate events
```

> `.env` changes are picked up every 30 seconds — no restart needed.
> Exception: `JWT_SECRET` and `DATABASE_URL` require a restart.

---

## 30. Deploying to Production

### Pre-launch checklist

| # | Action | Time | Risk if skipped |
|---|--------|------|-----------------|
| 1 | Change `OWNER_PASSWORD` from `ChangeMe123!` | 1 min | 🔴 Account takeover |
| 2 | Deploy to HTTPS | 15 min | 🔴 Stripe/Telegram broken |
| 3 | Set `DATABASE_URL` to managed PostgreSQL | 2 min | 🟠 SQLITE_BUSY under load |
| 4 | Configure Stripe + run `stripe_setup.py` | 20 min | 🟠 No billing |
| 5 | Register Stripe webhook + set `STRIPE_WEBHOOK_SECRET` | 5 min | 🟠 Subscriptions not activated |
| 6 | Register Telegram webhook | 2 min | 🟠 No subscriber delivery |
| 7 | Configure SMTP | 10 min | 🟡 No email verification |
| 8 | Enable Telegram broadcast channel | 5 min | 🟡 Rate-limit at >50 users |

> **Cookie security and CORS are auto-configured.** When `APP_URL` starts with `https://`, the refresh-token cookie is set `Secure=true` and CORS is locked to that origin. No extra config needed.

### Railway (recommended — `railway.toml` pre-configured)

```bash
railway login && railway init && railway up
railway variables set JWT_SECRET=... OWNER_EMAIL=... OWNER_PASSWORD=...
railway variables set TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=...
railway variables set STRIPE_SECRET_KEY=... APP_URL=https://your-app.railway.app
```

**Add PostgreSQL:**
```bash
railway add --plugin postgresql
# Railway auto-sets DATABASE_URL — restart the service to activate
```

Then:
1. Run `python3 stripe_setup.py` locally (with `STRIPE_SECRET_KEY` in `.env`) — auto-fills Price IDs
2. Set up Stripe webhook: endpoint `https://your-app.railway.app/api/billing/webhook`, events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.payment_failed`. Copy the `whsec_...` signing secret to `STRIPE_WEBHOOK_SECRET`.
3. Go to `https://your-app.railway.app/app` → Account Settings → Admin → Register TG Webhook
4. **Change your owner password** in Account Settings → Security

### Fly.io (`fly.toml` pre-configured)

```bash
fly auth login
fly launch --no-deploy
fly secrets set JWT_SECRET=... OWNER_EMAIL=... APP_URL=https://signal-trade.fly.dev # etc.
fly deploy
```

The `fly.toml` mounts `/app/data` as a persistent volume — this directory holds both `trading.db` (SQLite fallback) and `factor_weights.json`. For production, attach a managed Postgres:

```bash
fly postgres create --name signal-trade-db
fly postgres attach signal-trade-db
# Fly auto-sets DATABASE_URL — redeploy to activate
```

The healthcheck polls `/api/health` every 30 s with a 10 s grace period — if it fails 3× the machine is restarted automatically.

### Heroku / Render

`Procfile` is included:
```
web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Docker Compose (self-hosted)

```bash
cp backend/.env.example backend/.env   # fill required vars
docker compose up -d
```

`docker-compose.yml` starts **both** a `postgres:16-alpine` service and the backend. The backend waits for Postgres to pass its healthcheck before starting. All data (DB + factor weights) lives in the named `postgres_data` volume — no manual volume paths needed.

For a backend-only build (bring-your-own Postgres):
```bash
cd backend && docker build -t signal-trade .
docker run -p 8000:8000 --env-file .env signal-trade
```

---

## 31. Troubleshooting

### "No signals showing" / empty feed

- Wait 30–60 seconds for the first scan to complete
- Check terminal for errors
- Ensure `FINNHUB_API_KEY` is set and valid (news + analyst signals need it)
- Lower `MIN_CONFIDENCE` in `.env` or in Tweaks → Aggressiveness → Aggressive

### "Backend offline" in the app

- The server isn't running. Start it: `uvicorn main:app --reload --port 8000`
- Check for port conflict: `lsof -i :8000`
- Check the terminal for Python errors

### Telegram not delivering

- Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are correct
- Test: `curl "https://api.telegram.org/bot<TOKEN>/getMe"` — should return your bot info
- Check `AUTO_SEND_NOTIFICATIONS=true` in `.env`
- Check the Delivery log pane in the dashboard — look for "fail" entries with error messages
- If using subscriber delivery: ensure the bot webhook is registered (Admin panel) and the subscriber has run `/start <code>`

### Subscribers not receiving signals

- The bot webhook must be registered at a public HTTPS URL
- Users must have linked Telegram via `/start <code>` — verify in Admin → Users that `telegram_linked = true`
- Subscribers need **Basic or Pro** subscription status to receive Telegram delivery

### "JWT_SECRET not set" — sessions reset on restart

- Add `JWT_SECRET=<hex string>` to `backend/.env`
- Generate: `python3 -c "import secrets; print(secrets.token_hex(32))"`

### Stripe webhook not firing

- Verify `STRIPE_WEBHOOK_SECRET` (starts with `whsec_`) is set
- Ensure `APP_URL` is your public HTTPS URL (not localhost)
- In Stripe Dashboard → Webhooks — check for failed deliveries

### Sector heatmap stuck on "Loading"

- It pre-warms at startup; if you start the server and immediately open it, wait ~10 seconds
- Check for `[startup] sector heatmap pre-warmed` in terminal — if missing, yfinance may be rate-limited
- Click the sector name again to retry the lazy fetch

### Backtest shows 0 resolved signals

- Outcomes accumulate automatically over time (1d after 1 day, etc.)
- Click **Backfill Outcomes** to retroactively fill from historical yfinance prices
- Signals younger than 1 day cannot be backfilled (no future price data)

### Auth redirect loop

- Clear `localStorage` in browser DevTools → Application → Local Storage → delete `st_auth_token`
- Or open `/login` directly and sign in again

### "passlib / bcrypt" error on Python 3.14

- The system uses `bcrypt` directly (passlib bypassed). If you see this error, ensure `bcrypt` is installed:
  `pip install bcrypt`

### XGBoost model not adjusting confidence

- The model only activates after training. Train it: Account Settings → Admin → `POST /api/ml/train`
- Requires at least 50 resolved signals in the database (outcome_pct IS NOT NULL)
- Check status: `GET /api/ml/status` — shows `oos_accuracy`, `n_train`, `top_features`
- The model retrains automatically every Sunday 11am ET alongside factor mining

### Backtest response is slow

- The backtest summary is pre-computed after each scan cycle and cached for 5 minutes
- If the cache is cold (first request after startup), it runs the live query — takes 1–3 seconds
- After the first scan completes, subsequent requests are instant
- For the OOS endpoint (`/api/signals/backtest/oos`), a 10-minute TTL cache applies

---

## 32. XGBoost ML Confidence Model

The ML model is an XGBoost binary classifier that augments the deterministic signal scores with a data-driven confidence adjustment.

### What it does

- Trained on resolved signals (`outcome_pct IS NOT NULL`) from PostgreSQL
- Extracts a **19-feature** vector (v5.8: `confidence_bin` removed — was a binned duplicate of `confidence` that amplified calibration inversion)
- Features: confidence, sentiment, n_sources, n_rationale, pos/neg rationale, rr_numeric, is_buy, has_options/dark_pool/fundamentals/institutional/macro/earnings source, is_pre_market, is_position_style, stop_pct, target_pct, price_log
- Uses a temporal 70/30 train/test split (oldest 70% = train, newest 30% = OOS validation)
- **Regularization (v5.8):** `reg_alpha=0.1` (L1), `reg_lambda=2.0` (L2), `gamma=0.3`, `max_depth=3`, `learning_rate=0.05`
- Outputs a win probability; adjusts confidence by ±25% (multiplicative, capped at 72% ceiling)
- Runs after Platt/isotonic calibration — the last step before signal assembly

### Requirements

- At least 50 resolved signals in the database
- `xgboost>=2.0.0` and `scikit-learn>=1.4.0` (already in `requirements.txt`)
- The model file is saved to `backend/data/signal_ml_model.json` — not committed to git

### Training manually

```bash
# Via API (owner only):
curl -X POST /api/ml/train -H "Authorization: Bearer <token>"

# Response:
{
  "oos_accuracy": 0.631,
  "oos_auc": 0.704,
  "n_train": 312,
  "n_test": 134,
  "top_features": ["confidence", "has_options_source", "n_sources", ...]
}
```

The model retrains **automatically every Sunday at 11:00am ET** alongside factor mining.

### Checking model status

```bash
GET /api/ml/status
# Returns model metadata or {"trained": false} if no model file exists
```

### Disabling the model

The model is loaded lazily and only applies when the file exists. To disable: delete `backend/data/signal_ml_model.json`. The engine reverts to pure Platt-calibrated confidence with no change to scoring logic.

---

## 33. Custom Screener Builder

The screener builder lets you define named filter presets and run them against the live signal feed — without changing the global confidence threshold.

### Creating a screener

```bash
POST /api/screener
{
  "name": "High-conf dark pool BUYs",
  "rules": [
    {"field": "action",    "op": "eq",  "value": "BUY"},
    {"field": "confidence","op": "gte", "value": 72},
    {"field": "has_source","op": "eq",  "value": "Dark Pool"}
  ]
}
```

### Available fields and operators

| Field | Type | Description |
|-------|------|-------------|
| `confidence` | number | Signal confidence 0–100 |
| `sentiment` | number | Aggregate sentiment −1 to +1 |
| `action` | string | "BUY", "SELL", or "HOLD" |
| `style` | string | "swing" or "position" |
| `rr` | number | Risk:reward ratio (e.g. 2.1) |
| `n_sources` | number | Number of data sources that voted |
| `ticker` | string | Exact ticker symbol |
| `has_source` | string | Source name present in signal (e.g. "Options", "Dark Pool", "13F") |

| Operator | Meaning |
|----------|---------|
| `gt`, `gte`, `lt`, `lte` | Numeric comparisons |
| `eq`, `neq` | Equality / inequality |
| `contains` | String substring (case-insensitive) |
| `in` | Value is in a list |

### Running a screener

```bash
GET /api/screener/{name}/run
# Returns {matched: N, signals: [...]}
```

### Preview without saving

```bash
POST /api/screener/preview
{"name": "test", "rules": [...]}
# Evaluates against live signals but does NOT persist the screener
```

### All endpoints

```
GET    /api/screener               — list all saved screeners
POST   /api/screener               — create or replace a screener (max 20)
DELETE /api/screener/{name}        — delete a screener
GET    /api/screener/{name}/run    — run against live signals
POST   /api/screener/preview       — test without saving
```

All rules are AND-joined. Maximum 20 rules per screener, 20 screeners per account. Screeners are stored in `app_settings["screeners"]` — they survive restarts.

---

## 34. PostgreSQL Migration

PostgreSQL is now the **default database** for both local dev and production. SQLite is the automatic fallback when `DATABASE_URL` is not set.

### Local dev setup (Homebrew)

```bash
# Install and start (one-time)
brew install postgresql@16
brew services start postgresql@16

# Create user and database
psql postgres -c "CREATE USER signal WITH PASSWORD 'signal_dev_pw' SUPERUSER;"
psql postgres -c "CREATE DATABASE signal_trade OWNER signal;"
```

> The `SUPERUSER` grant is only needed locally for the migration script. On managed cloud providers (Railway, Neon, Supabase) the provided credentials already have sufficient privileges.

### Migrate existing SQLite data

If you have existing signals/users in `data/trading.db`, copy them across:

```bash
cd backend
source venv/bin/activate
python scripts/migrate_sqlite_to_postgres.py
```

The script:
- Reads all 10 tables from SQLite
- Type-coerces JSON, boolean, and datetime columns
- Truncates the PG tables then inserts in FK dependency order
- Resets all sequences after import
- Is **idempotent** — safe to re-run

### Activate PostgreSQL

`DATABASE_URL` is read by `database.py` at import time (via `python-dotenv`). For local dev it is already set in `backend/.env`:

```
DATABASE_URL=postgresql://signal:signal_dev_pw@127.0.0.1:5432/signal_trade
```

For Docker Compose the `backend` service overrides this with the internal service hostname (`postgres:5432`). For Railway/Fly.io, set `DATABASE_URL` to your managed provider URL — the app picks it up automatically.

### What changes at runtime

- `SQLITE_BUSY` errors eliminated — PostgreSQL uses proper row-level locking
- Connection pooling: 10 persistent connections, 20 overflow, `pool_pre_ping=True`
- SQLite WAL pragmas and additive `ALTER TABLE` migrations are skipped — Postgres uses `create_all`
- `database.py` loads `.env` at import time so `DATABASE_URL` is always available before the engine is constructed

### SQLite DB path

The SQLite fallback path is `./data/trading.db` (not `./trading.db`). This ensures the file lives inside `/app/data` on Fly.io, which is the persistent volume mount point. On first startup, if `data/trading.db` doesn't exist but `trading.db` does, it is automatically copied over.

### Production (Railway / Fly.io)

```bash
# Railway
railway add --plugin postgresql
# DATABASE_URL is injected automatically — restart to activate

# Fly.io
fly postgres create --name signal-trade-db
fly postgres attach signal-trade-db
# DATABASE_URL is injected automatically — redeploy to activate
```

---

## 35. Redis Cache Setup

Redis provides a shared cache layer for hot data (macro context, fear & greed, sector data) that is fetched from external APIs on every scan cycle. Without Redis, each service maintains its own in-process dict — shared cache across multiple workers requires Redis.

### When to add Redis

- Running multiple scanner workers / replicas
- Noticing redundant API calls to Polygon/Finnhub on the same data within 60 seconds
- Using Redis Streams for the event-driven worker bus (distributed deployment)

### Setup

```bash
# Redis is not required — the system falls back to in-process dicts automatically.
# Add to backend/.env to enable:
REDIS_URL=redis://localhost:6379
# or with TLS:
REDIS_URL=rediss://user:pass@host:6380
```

### What is cached in Redis

| Key | TTL | Source |
|-----|-----|--------|
| `macro:context` | 1 hour | `services/macro.py` |
| `fear_greed:data` | 1 hour | `services/fear_greed.py` |
| `analytics:backtest_summary` | 5 min | `services/scanner.py` post-scan |
| ML model metadata | varies | `services/signal_ml.py` |

### Checking cache health

```bash
GET /api/admin/rate-limits
# Returns cache stats: {"backend": "redis", "memory_keys": 0, "redis_connected": true}
```

### Railway Redis addon

```bash
railway add --plugin redis
# Railway auto-sets REDIS_URL — restart to activate
```

---

## 36. CI/CD & Testing

A GitHub Actions workflow runs on every push/PR to `main`.

### Pipeline

`.github/workflows/ci.yml`:

1. **Syntax check** — `ast.parse()` on all `.py` files (catches broken imports before even running)
2. **Import smoke tests** — `tests/test_imports_smoke.py` — verifies all critical modules import cleanly
3. **Unit tests** — `pytest tests/ -x -q --timeout=30` (E2E tests are skipped by default; run them separately with `pytest tests/e2e --run-e2e -q --timeout=60`)
4. **Signal accuracy gate** — runs `validate_predictions.py`; fails the PR if win rate drops below 52% or Sharpe below 1.0 (skips automatically when fewer than 30 resolved signals exist)
5. **Security audit** — `pip-audit -r requirements.txt` (non-blocking — reports CVEs but doesn't fail the build)

### Running tests locally

```bash
cd backend
source ../.venv311/bin/activate  # Python 3.11 venv required; Python 3.14 conflicts with pytest-asyncio
pytest tests/ -q --timeout=30
# Expected: all backend unit tests pass (E2E skipped by default)
pytest tests/e2e --run-e2e -q --timeout=60
# Expected: E2E golden-path tests pass
```

### Running the accuracy gate manually

```bash
python3 validate_predictions.py
```

### Adding a new test

Tests live in `backend/tests/`. Key test files:
- `test_imports_smoke.py` — import-only smoke tests (fast, no DB)
- `test_delivery_gates.py` — 15 tests for all pre-send gate checks
- `test_quant_metrics.py` — 26 tests for Sharpe, Sortino, VaR, t-stat, etc.
- `test_performance_snapshots.py` — 14 tests for snapshot diff and flagged metrics
- `test_calibration.py` — blend function and apply_calibration tests
- `test_signal_ml.py` — XGBoost feature extraction and confidence adjustment

---

## 37. Performance Analytics & Snapshots

The institutional performance report is generated by `backend/scripts/calc_tbd_metrics.py`.

### Running the report

```bash
cd backend && source venv/bin/activate
python scripts/calc_tbd_metrics.py
```

Output is Markdown — 14 sections covering return summary, risk-adjusted metrics, tail risk, distribution diagnostics, multi-timeframe, monthly, by style/action/exit/confidence/sector/session, trade-path analytics, and return distribution.

### Saving a named snapshot

```bash
python scripts/calc_tbd_metrics.py --snapshot "v5.8-calibration-tightened"
# Writes to performance_snapshots table. Re-running the same tag upserts (delete + insert).
```

The snapshot stores the full metrics dict as JSONB alongside the git SHA at time of writing.

### Comparing snapshots

```bash
# Via API (owner JWT required):
GET /api/admin/snapshots              # list all snapshots
GET /api/admin/snapshots/diff/1/2    # delta between snapshot 1 (before) and 2 (after)
```

The diff response includes a `flagged_metrics[]` array listing every metric that changed beyond its significance threshold (e.g. win_rate ≥2pp, sharpe ≥0.3, brier ≥0.02, phantom_wins ≥5).

### Auto-snapshots

The Sunday weekly digest automatically saves a `weekly-YYYY-MM-DD` snapshot after sending. This provides a no-effort weekly baseline without manual intervention.

### Key metrics explained

| Metric | What it means | Caveat |
|---|---|---|
| **Win Rate (7d mark)** | % trades with outcome_pct > 0 at 7-day horizon | Includes phantom wins |
| **Stop-Enforced WR** | WR if all stop hits are forced losses | The realistic live-portfolio number |
| **Sharpe** | mu/sigma × sqrt(252) | Per-signal quality metric, not portfolio Sharpe |
| **Sortino** | mu/sigma_d × sqrt(252) | sigma_d = RMS of negative returns from 0%, divisor = n |
| **Capture Ratio** | avg_return / avg_stop_distance | 0.41 means you capture 41% of what you risked |
| **Phantom Wins** | hit_stop=True AND outcome_pct > 0 | Stop hit intraday but position recovered by 7d mark |

### Security audit

```bash
pip-audit -r requirements.txt
```

Known false positives are excluded with `--ignore-vuln PYSEC-2022-42969`. All other CVEs should be investigated and dependencies updated.

## Enabling Options Paper/Live Execution

Options VRP signals are **signal-only by default** (`options_mode='signal'`).  To enable execution:

1. Acknowledge the options-specific risk disclosure:
   ```bash
   curl -H "Authorization: Bearer $JWT" \
        -X POST https://signal.trade/api/me/options/risk-acknowledge
   ```

2. Switch to paper mode to simulate fills:
   ```bash
   curl -H "Authorization: Bearer $JWT" \
        -H "Content-Type: application/json" \
        -X PUT https://signal.trade/api/me/options/settings \
        -d '{"options_mode":"paper"}'
   ```

3. For live mode you must also:
   - Complete the generic trading-risk acknowledgement (`POST /api/me/risk-acknowledge`).
   - Connect an Alpaca account with options approval level ≥ 3.
   - Then `PUT /api/me/options/settings {"options_mode":"live"}`.

Paper fills are priced at the natural side of the spread (buy at ask, sell at bid) and marked to market nightly against Polygon option snapshots.  All option orders are filtered for liquidity (volume, open interest, bid/ask spread) before submission.
