# Signal.Trade Comprehensive Technical Audit — Execution Plan

## Objective
Perform an exhaustive, end-to-end technical code review of the Signal.Trade real-time trading recommendation system across five architectural pillars.

## Codebase Overview
- **Backend**: FastAPI (Python 3.11+), ~90 services, ~25 routers, SQLAlchemy async, PostgreSQL/SQLite
- **Frontend**: React (JSX, no TypeScript), single-file components, WebSocket, localStorage caching
- **Key Files** (by pillar):

### Pillar 1 — Core Mathematical Logic & Signal Engine
- `backend/services/signal_engine.py` (5,871 lines) — main signal generation
- `backend/services/technicals.py` (885 lines) — RSI, MACD, Bollinger, ATR, ADX, Stochastic, CCI, ROC, candlesticks, entry/stop/target calculations
- `backend/services/options_engine.py` (479 lines) — VRP, option legs, DTE
- `backend/services/signal_scoring.py` (556 lines) — EMA cross, MACD, OBV/ADX, oscillator scoring
- `backend/services/bayesian_smoothing.py` (27 lines) — Bayesian win-rate smoothing
- `backend/services/scanner.py` (2,414 lines) — orchestration pipeline
- `backend/services/engines/helpers.py` — R:R, levels, scoring helpers
- `backend/services/engines/assembler.py` — signal assembly

### Pillar 2 — Frontend State & Component Robustness
- `frontend/src/app.jsx` (2,102 lines) — main app state, WebSocket, auth, localStorage, signal cache
- `frontend/src/cin.app.jsx` (676 lines) — cinematic app shell, signal mapping, delivery log
- `frontend/src/app.signal.jsx` (311 lines) — SignalRow, TelegramPane, delivery UI
- `frontend/src/app.views.jsx` — views and routing
- `frontend/src/cin.market.jsx` — market context, ticker tape
- `frontend/src/cin.dashboard.jsx` — dashboard, stats
- `frontend/src/cin.ui.jsx` — UI primitives, icons
- `frontend/src/app.ui.jsx` — UI helpers, tooltip, modal

### Pillar 3 — Data Pipelines, Filtering & Flow Control
- `backend/routers/delivery_router.py` (31 lines) — delivery endpoint
- `backend/routers/websocket_router.py` (150 lines) — WS connection manager, broadcast
- `backend/services/delivery_gates.py` (651 lines) — pre-send eligibility gates
- `backend/services/delivery_manager.py` — delivery orchestration
- `backend/services/scanner.py` (2,414 lines) — scanning pipeline, filtering
- `backend/services/signal_workers.py` — worker bus, signal processing
- `backend/services/worker_bus.py` — event-driven worker bus
- `backend/services/market_calendar.py` — market hours, holidays
- `backend/routers/signals.py` (2,156 lines) — signal REST API

### Pillar 4 — Integration & Brokerage Sandbox Boundaries
- `backend/routers/paper_router.py` (228 lines) — paper trading orders, positions, risk
- `backend/routers/broker.py` (459 lines) — broker connect, auto-execute, credential encryption
- `backend/services/broker_svc.py` — broker service, credential encryption/decryption
- `backend/services/alpaca_rest.py` — Alpaca REST API wrapper
- `backend/services/alpaca_ws.py` — Alpaca WebSocket
- `backend/services/options_paper.py` — option paper trading
- `backend/services/ibkr_rest.py` — IBKR REST wrapper
- `backend/models.py` (50,202 lines) — BrokerOrder, User, Signal models

### Pillar 5 — Error Handling, Logging & Exceptions
- `backend/main.py` (2,331 lines) — FastAPI app, middleware, exception handlers, startup/shutdown
- `backend/config.py` (328 lines) — settings, secrets, validation
- `backend/database.py` (89 lines) — DB session, connection pool
- `backend/services/auth_svc.py` — auth, JWT, token validation
- `backend/routers/*.py` — all router error handling patterns
- `backend/services/*.py` — service-level error handling
- Sentry integration in main.py

## Execution Strategy
Launch 5 parallel sub-agents (one per pillar). Each sub-agent:
1. Reads the assigned files thoroughly
2. Searches for specific anti-patterns within the assigned scope
3. Produces a structured audit report with:
   - Severity (Critical / High / Medium / Low)
   - Exact file path, function, line number
   - Root cause
   - Real-world impact
   - Production-ready refactored code fix

## Integration
After all 5 sub-agents return, merge findings into a single comprehensive audit document.
