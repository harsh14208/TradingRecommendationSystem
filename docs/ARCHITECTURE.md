# Signal.Trade — Architecture Guide

> This architecture is designed to support the full lifecycle from research signals to
> **live broker execution**. Every layer is built so that a validated signal can flow
> automatically into an Alpaca or IBKR order with risk checks, audit logging, and a
> human-operated kill switch.

## System Overview

```text
┌─────────────────────────────────────────────────────────────────────┐
│                              Clients                                 │
│  React SPA (dashboard)  │  Marketing site  │  Mobile PWA  │  Admin  │
└─────────────────────────┴──────────────────┴──────────────┴─────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FastAPI Application                              │
│  Auth / Billing / Signals / Paper / Admin / WebSocket / OAuth        │
│  ─ slowapi rate limiting  ─ SecurityHeadersMiddleware (CSP/HSTS)     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            ▼                     ▼                     ▼
┌───────────────┐      ┌────────────────────┐   ┌───────────────┐
│    Services   │      │  SQLAlchemy async  │   │  Redis/cache  │
│  (business)   │◄────►│  PostgreSQL/SQLite │   │  (optional)   │
└───────────────┘      └────────────────────┘   └───────────────┘
```

## Live Execution Flow

When a user enables broker auto-execution, the signal path is:

```text
Scanner (15-min market-hours loop)
  └── Signal generated → delivery gates (confidence, MR-count, sector, time-of-day)
        └── _maybe_auto_execute_for_signal()
              ├── Fetch users with auto_execute=True + valid broker keys
              ├── Per-user runtime risk limits (daily orders, per-ticker notional)
              ├── Portfolio drawdown circuit-breaker (< −5% equity blocks)
              ├── TCA / capacity check (expected slippage)
              ├── Submit bracket-stop order via Alpaca/IBKR REST
              └── Record BrokerOrder + audit log
```

Key components:

| Component | File | Responsibility |
|-----------|------|----------------|
| Scanner orchestration | `services/scanner.py` | Triggers auto-execute after signal delivery |
| Broker abstraction | `services/broker_svc.py` | Credential encryption, risk limits, order placement, reconciliation |
| Broker REST clients | `services/alpaca_rest.py`, `services/ibkr_rest.py` | Low-level order APIs |
| Portfolio allocator | `services/portfolio_allocator.py` | HRP-based target weights; optional residual-cash overlay into SGOV/VOO |
| Cross-sleeve allocator | `services/alpha_sleeves.py` | Risk-parity / Sharpe-proportional capital split across MR, cross-sectional L/S, etc. |
| Daily PnL mark | `models.py` → `PnlDaily` | Equity, cash, gross/net exposure, drawdown tracking |
| Cross-sectional alpha | `services/cross_sectional_shadow.py` | Persisted h=21/h=63 XGBoost models; live bottom-decile sizing |
| TCA / capacity | `services/tca_service.py` | Slippage estimation and fill-quality feedback |
| User settings | `models.py` | `auto_execute`, `auto_execute_qty_dollars`, `max_daily_orders`, etc. |
| API surface | `routers/broker.py` | Connect credentials, toggle auto-execute, view status |
| Kill switch | `routers/admin.py` | Global pause/resume of all signal delivery and broker execution |

## Layer Boundaries

- **Routers** (`backend/routers/`) validate HTTP shape, call services, and
  return responses. They do not commit transactions.
- **Services** (`backend/services/`) contain business logic and are the only
  layer that commits database transactions.
- **Models / Database** (`backend/models.py`, `backend/database.py`) define the
  schema and provide sessions. `get_db()` yields only.

## Transaction Policy

> **"Services commit, routers don't; `get_db()` yields only."**

- `database.py` does not auto-commit. `get_db()` yields an `AsyncSession` and
  rolls back on unhandled exceptions.
- Routers pass the session into services; services call `await db.commit()`
  when a unit of work is complete.
- This prevents half-committed HTTP requests and makes retry/idempotency logic
  easier to reason about.

## Error Handling Policy

- Bare `except: pass` is forbidden.
- The minimum acceptable handler is:
  ```python
  log.warning("...", exc_info=True)
  ```
- All exceptions in services and routers must be logged; user-facing messages
  must not leak internal exception text or stack traces.
- Webhooks must return `200` for duplicate/replay events and log handler
  results.

## Idempotency Policy

- Stripe mutations always include an `idempotency_key` derived from
  `user_id` + action + timestamp.
- Webhook events are deduplicated by `event_id` and stored in `stripe_events`.
- Critical non-Stripe operations (checkout, portal, referral credits) also use
  idempotency keys or database unique constraints.

## Rate Limiting Standards

- A global `slowapi` limiter is mounted on the FastAPI app.
- Use per-route decorators (`@_limiter.limit("N/minute")`) for all auth,
  billing, checkout, admin-mutating, and externally-triggered endpoints.
- Prefer IP-based keys (`get_remote_address`) unless user-based limits are
  explicitly required.

## Migration Standards

- All schema changes must be dialect-aware (PostgreSQL vs SQLite).
- New indexes on PostgreSQL must use `CONCURRENTLY` to avoid table locks in
  production.
- `database.py` `init_db()` only contains safe additive migrations for empty
  or CI databases; production migrations go through Alembic.
- Never drop columns or tables inside `init_db()`.

## Tier & Entitlement Model

Three subscription tiers are defined in `backend/config.py`: `free`, `basic`,
and `pro`.  `services/auth_svc.require_tier()` enforces feature-level gates,
and owners bypass all tier checks.

### Signal view quotas

Signal consumption is capped per user per UTC day via
`services/signal_quota_svc`:

| Tier  | Daily signal views | Enforcement                         |
|-------|-------------------:|-------------------------------------|
| free  | 5                  | `GET /api/signals`, `/api/signals/history` |
| basic | 100                | Same endpoints                      |
| pro   | unlimited          | No cap                              |
| owner | unlimited          | Bypass                              |

The quota is tracked in the `user_signal_quotas` table (one row per user,
window reset at UTC midnight).  Routers call `apply_signal_quota()` before
fetching rows and `record_signal_views()` after serialization, then commit the
session.  Quota state is returned in `X-Signal-Quota-*` headers and inside the
`signal_quota` field of `GET /api/billing/status`.

Paid users whose `subscription_status` is not `active` are downgraded to the
free quota until billing is resolved.

### WebSocket eligibility

`routers/websocket_router.py` accepts connections from any authenticated user
but tags each connection with `eligible_for_signals`. Only owners and active
Basic/Pro users receive `new_signal` broadcasts; free and inactive paid users
receive only `price_update`, `market_context`, and `tick` messages. This keeps
the WebSocket path consistent with the REST quota model without adding a
per-message counting layer to the broadcast loop.

## Testing Standards

- Use the `override_deps(app, ...)` context manager from
  `backend/tests/conftest.py` to inject mocks (users, DB, and so on) in FastAPI
  route tests.

  Example:
  ```python
  from conftest import override_deps
  from services.auth_svc import get_current_user

  with override_deps(app, get_current_user=lambda: mock_user):
      resp = client.get("/api/protected")
  ```

- Tests run against an isolated SQLite database forced by the
  `_set_test_database_url` session fixture.
