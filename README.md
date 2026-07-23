| ![CI](https://github.com/harsh14208/TradingRecommendationSystem/actions/workflows/ci.yml/badge.svg) | ~2700 tests | Python 3.11 · FastAPI · PostgreSQL | React frontend |
|---|---|---|---|

# Signal.Trade

A quantitative mean-reversion trading system: a 23-year backtested signal engine, a FastAPI backend that scans a live watchlist and delivers scored BUY/SELL signals over Telegram, and an optional broker-execution layer (Alpaca/IBKR paper or live).

> ⚠️ **Not financial advice.** All signals are algorithmic output for informational and educational purposes only. This is a personal research project, not a registered investment adviser or broker-dealer. Past performance does not guarantee future results — see [Honest performance](#honest-performance) below before trusting any headline number.

---

## What this is

- A **signal engine** (`backend/services/signal_engine.py` + `services/engines/`) that scores ~170 tickers against 50+ independent indicator families — technicals, options flow, 13F institutional positioning, insider activity, fundamentals, macro regime, sentiment, and cross-sectional/pairs signals — and turns that into a calibrated confidence score.
- A **research harness** (`backend/scripts/backtest_technicals.py`, `cross_sectional_alpha_model.py`, and 100+ documented experiments in [`docs/`](docs/)) used to validate or kill every gate before it goes live. The research log is kept — including the dead ends — because that's the only way to know what's actually been tested.
- A **delivery + execution pipeline** (`services/scanner.py`, `services/delivery_gates.py`, `services/broker_svc.py`) that runs a continuous scan loop, applies risk/structural gates, fans signals out over Telegram, and can optionally auto-execute through Alpaca or IBKR paper/live accounts.
- A **FastAPI backend + React frontend** with auth, Stripe billing, a dashboard, mobile PWA, and public track-record page — this project doubles as a small SaaS, not just a research script.

## Honest performance

The per-trade edge is real by the metrics this project tracks (~55% win rate, positive Sharpe on the core mean-reversion cohort, survives walk-forward and bootstrap validation) — see [`docs/Stats.md`](docs/Stats.md) for the full research log.

But **Sharpe and win rate are not the metrics that decide whether this beats just buying an index fund.** Measured on concurrent-portfolio CAGR against SPY buy-and-hold over the same 22-year window (SPY ≈ 10.9%/yr dividend-adjusted), this system's backtested CAGR is **+1.1–1.4%/yr** — it does not currently beat the market. The gap is a capital-utilization problem, not a signal-quality problem: low trade frequency means the bulk of capital sits idle. That finding, why it happened, and what's being done about it (an idle-capital overlay, revisiting entry-gate tuning that traded volume for win rate) is tracked honestly in [`docs/TODO.md`](docs/TODO.md) and [`docs/LEARNINGS.md`](docs/LEARNINGS.md) rather than hidden behind a Sharpe number. If you're evaluating this repo, read that before the marketing copy below.

## Architecture

```
backend/
  main.py              FastAPI app, router mounts, lifespan, scheduled jobs
  database.py          SQLAlchemy async engine (PostgreSQL primary, SQLite for tests)
  config.py             Pydantic settings (.env)
  routers/              HTTP endpoints (signals, quotes, auth, billing, broker, paper trading…)
  services/
    signal_engine.py    Orchestration — generate_signal() + scan_all()
    engines/            Scoring assembly, risk gates, calibration
    signal_workers.py   Async per-source workers (news, fundamentals, options, institutional…)
    scanner.py           Continuous market scan loop
    delivery_gates.py    Structural/risk gates that decide what actually gets sent
    broker_svc.py        Alpaca/IBKR order execution, HRP portfolio allocation, cash overlay
    market_data.py        OHLCV cache (Redis → in-memory fallback)
    macro.py              VIX, yield curve, macro regime detection
  scripts/               Backtests, factor mining, screeners, research experiments
  tests/                 ~2700 tests (pytest)
frontend/
  src/                   React app (dashboard, marketing site, mobile PWA)
  pages/, public/        Served HTML/static assets
```

Full architecture, layer boundaries, and transaction policy: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Signal engine — condensed

70+ indicators across technicals (RSI/MACD/Bollinger/ADX/Hurst/Supertrend…), options flow (GEX, IV rank, skew), 13F institutional flow, insider Form 4 activity, fundamentals (Piotroski, FCF yield), macro (VIX regime, yield curve, HMM regime detection), sentiment (Fear & Greed, NAAIM, social), and sector/pairs cointegration — combined into a confidence score, then passed through structural gates (VIX floor, earnings blackout, sector concentration limits, cohort-level expected-value gating) before delivery. Full indicator-by-indicator breakdown: [`docs/README.md`](docs/README.md#signal-engine--50-blocks).

## Quick start

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# PostgreSQL (local dev)
brew install postgresql@16 && brew services start postgresql@16
psql postgres -c "CREATE USER signal WITH PASSWORD 'signal_dev_pw' SUPERUSER;"
psql postgres -c "CREATE DATABASE signal_trade OWNER signal;"

cp .env.example .env
# set FINNHUB_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, JWT_SECRET, OWNER_EMAIL, OWNER_PASSWORD

uvicorn main:app --reload --port 8000
```

```
open http://localhost:8000        # marketing landing
open http://localhost:8000/app    # dashboard (login required)
open http://localhost:8000/mobile # mobile PWA
```

The owner account is auto-created from `OWNER_EMAIL`/`OWNER_PASSWORD` on first startup. Full environment variable reference: [`docs/HOWTO.md`](docs/HOWTO.md) §29.

## Testing

```bash
cd backend && pytest tests/ -x -q --timeout=30
ruff check backend/ --config ruff.toml
ruff format backend/ --config ruff.toml --check
```

~2700 tests. CI runs syntax/import smoke checks, the full suite, an accuracy regression gate, `pip-audit`, and `ruff` on every push — see [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Before connecting real money

Broker auto-execution is implemented but should stay on **paper** until live results justify otherwise — and per [Honest performance](#honest-performance), that bar hasn't been cleared yet on a risk-adjusted-vs-benchmark basis. Go-live checklist: [`docs/RUNBOOK.md`](docs/RUNBOOK.md) §7.

## Docs

| Doc | What's in it |
|---|---|
| [`docs/Stats.md`](docs/Stats.md) | Full backtest research log — every experiment, including the ones that failed |
| [`docs/TODO.md`](docs/TODO.md) | Open research items and known issues |
| [`docs/LEARNINGS.md`](docs/LEARNINGS.md) | Post-mortems — what broke in production and why |
| [`docs/SIGNAL_VALIDATION.md`](docs/SIGNAL_VALIDATION.md) | Live gate validation results |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System design, layer boundaries, transaction policy |
| [`docs/RUNBOOK.md`](docs/RUNBOOK.md) | Operational procedures, deployment, go-live checklist |
| [`docs/HOWTO.md`](docs/HOWTO.md) | Setup, environment variables, broker connection steps |

## Product layer

The backend also runs a small subscription product (Free/Basic/Pro/Elite tiers via Stripe, multi-user Telegram fan-out, dashboard, mobile PWA) — see [`docs/README.md`](docs/README.md#subscription-tiers) for details. This is secondary to the research; the code is included as-is rather than stripped out, since the execution/billing/multi-tenant plumbing is part of what makes the signal engine a complete system rather than a notebook.

## License

No license file is currently included — all rights reserved by default. Open an issue if you'd like to discuss usage terms.

## Legal

Signal.Trade is not financial advice. All signals are algorithmic outputs for informational and educational purposes only. Signal.Trade is not a registered investment adviser, broker-dealer, or financial planner. Past performance does not guarantee future results. All trading involves substantial risk of loss.
