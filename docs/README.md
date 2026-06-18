# Signal.Trade

**Quantitative mean-reversion trading signals — 70+ independent indicators, 23-year backtested MR strategy (IS Sharpe 0.24 with L7 conviction sizing), multi-user Telegram delivery, full subscription stack, and institutional performance analytics.**

> **v10.8+v8.8.6** · 2550 tests passing (ex-e2e) · PostgreSQL primary · TSYS-1→13 complete · QENG roadmap complete · public HTTPS live at `https://signaltrade.org` · IS N=217 trades/23yr (Sh=0.24 with L7 conviction sizing + MR-count-2, survivorship-corrected + §63 ADF gate), OOS Sharpe=0.16 · Forward Sharpe est. 0.13–0.20 · cross-sectional L/S net +0.576 (h=63, SHADOW) +0.347 (h=21)
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

Before connecting real money, complete the go-live checklist in [RUNBOOK.md](RUNBOOK.md) §7.

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

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full system architecture, layer boundaries, transaction policy, error handling, rate limiting, migration standards, and tier & entitlement model.

---

## Environment Variables

See [HOWTO.md](HOWTO.md) §29 for the full environment variables reference and `.env` setup.

---

---

## Deploy

See [RUNBOOK.md](RUNBOOK.md) §1 for first-time deployment, and [HOWTO.md](HOWTO.md) §30 for production deployment steps.

---

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
