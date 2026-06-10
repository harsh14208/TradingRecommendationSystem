# Signal.Trade — Architecture Guide

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
