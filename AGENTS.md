# Agent Guide — Signal.Trade

Conventions for coding agents working on the Signal.Trade monorepo.

## Code Style Conventions

- Python 3.11+ with type hints. Prefer `str | None`, `list[dict]`, and so on.
- Format with `ruff`; imports are sorted (`isort` profile).
- Keep functions small and single-purpose. Name the module logger `log`.
- Use Pydantic models for request/response schemas in routers.
- Prefer explicit `try/except` clauses; bare `except:` is prohibited.
- Frontend: React functional components, hooks, and `AbortController` for every
  async effect.

## Security Rules

- **Secrets**: use `pydantic.SecretStr` for every credential or environment
  secret. Never hardcode fallback values.
- `JWT_SECRET` is required in production; startup must fail if it is missing.
- Never log secrets, tokens, or password hashes.
- Do not persist access tokens in `localStorage` or `sessionStorage` on the
  frontend.
- OAuth flows must use PKCE (`S256`) and single-use state.
- Verify Stripe webhook signatures with `STRIPE_WEBHOOK_SECRET` before
  processing any event.
- Broker credentials must be encrypted with scrypt KDF v2 and a per-credential
  salt.

## Transaction Rules

- **Services commit, routers don't.**
- `database.py` / `get_db()` only yields sessions; it must not auto-commit.
- Routers call services, which explicitly commit when the business unit of work
  is complete.
- Always `await db.rollback()` before re-raising inside a service on error.

## Testing Conventions

- Use the Python 3.11 virtual environment (`.venv311`) for the test suite.
  Python 3.14's asyncio event-loop handling conflicts with `pytest-asyncio` and
  causes mass `RuntimeError: Runner.run() cannot be called from a running event
  loop` failures.
- E2E tests live under `backend/tests/e2e` and require the Playwright plugin.
  They are skipped by default; run them with `pytest tests/e2e --run-e2e`.
- Use `override_deps` from `backend/tests/conftest.py` to mock FastAPI
  dependencies in tests.
- Never point tests at the production or development PostgreSQL database; the
  test fixture forces SQLite.
- Add tests for auth, tier-gating, webhook idempotency, and security
  regressions.

## Documentation Requirements

When changing any of the following, update the relevant docs files
(`docs/README.md`, `docs/SECURITY.md`, `docs/ARCHITECTURE.md`,
`docs/RUNBOOK.md`):

- Authentication or authorization flows (JWT, OAuth, tier checks, owner-only
  endpoints).
- Billing, Stripe webhooks, subscription lifecycle, or trial logic.
- Database schema, migrations, or foreign-key / delete policies.
- Secrets / config keys, encryption / KDF versions, or rate-limiting rules.
