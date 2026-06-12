# Signal.Trade — Security Guide

This document summarises the security controls and operational rules for the
Signal.Trade backend after the security/architecture refactor.

---

## 1. Secret Management

- All environment secrets are modelled with `pydantic.SecretStr` in
  `backend/config.py`.
- There is **no hardcoded fallback** for `JWT_SECRET`. Production startup fails
  if it is unset.
- `JWT_SECRET` must be at least 32 characters (64+ random characters recommended:
  `python3 -c "import secrets; print(secrets.token_hex(32))"`).
- Other `SecretStr` fields include:
  `ALPACA_API_SECRET`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`,
  `GOOGLE_CLIENT_SECRET`, `DISCORD_CLIENT_SECRET`, `SMTP_PASSWORD`,
  `VAPID_PRIVATE_KEY`, `TELEGRAM_BOT_TOKEN`, and `OWNER_PASSWORD`.
- `OWNER_PASSWORD` startup check enforces ≥16 characters; production fails
  on `ChangeMe123!` (fixed 2026-06-09 — `.env` now has 32-char secure password).
- VAPID keys documented in `.env.example`; generate with `py_vapid`.
- Secrets are exposed only via `.get_secret_value()` at the point of use and are
  never logged, serialised, or returned to clients.

## 2. Authentication

- Short-lived JWT access tokens (default 60 minutes) plus long-lived HTTP-only
  `st_refresh` cookies (30 days).
- OAuth 2.0 via Google and Discord uses **PKCE** (`code_challenge_method=S256`)
  with per-flow state and verifier stored in `OAuthState`.
- One-time OAuth exchange codes (`OAuthOneTimeCode`) are single-use, short-lived
  (60 seconds), and atomically consumed during exchange.
- The frontend stores access tokens in **module memory only** — never
  `localStorage` or `sessionStorage`. Silent refresh uses the HTTP-only cookie
  endpoint `/api/auth/refresh-cookie`.
- Passwords are hashed with bcrypt.

## 3. Authorization

- Tier gating is enforced by `services.auth_svc.require_tier(min_tier)`. Owner
  bypasses all tier checks.
- `paper_router.py` requires authentication on all endpoints;
  `POST /api/paper/orders` requires the **Pro** tier (or owner).
- Admin/owner endpoints (`/api/admin/*`) enforce `current_user.is_owner`.
- User-scoped endpoints (`/api/me/*`, broker connect, paper trading) enforce
  resource ownership.

## 4. Billing Security

- Stripe webhook signatures are verified with
  `stripe.Webhook.construct_event` using `STRIPE_WEBHOOK_SECRET`.
- The webhook endpoint rejects all events with `503` when
  `STRIPE_WEBHOOK_SECRET` is not configured.
- Every Stripe mutating call uses an `idempotency_key`.
- Webhook events are deduplicated by `StripeEvent.event_id`; replays return
  `200` immediately.
- Trial abuse prevention: `trial_consumed_at` is set on first checkout
  completion; only one trial is granted per account.
- Subscription transitions are logged in `stripe_events` with before/after state.

## 5. Broker Security

- Broker credentials (Alpaca/IBKR keys) are encrypted at rest with **Fernet over
  a scrypt KDF v2 key and a random 16-byte per-credential salt**
  (`v2:<salt>:<ct>`).
- Legacy v1 ciphertexts remain decryptable via `MultiFernet`; rotation
  re-encrypts them to v2 automatically.
- The encryption key is derived from `JWT_SECRET`, so rotating the JWT secret
  invalidates stored credentials until users re-enter them.
- Portfolio drawdown circuit breaker: auto-execution is blocked if unrealised
  P&L / equity falls below **−5%**.
- Per-user runtime risk limits (`max_daily_orders`, `max_ticker_notional`) are
  enforced in `broker_svc.py`.

## 6. Rate Limiting

- A global `slowapi` limiter is mounted on the FastAPI app
  (`app.state.limiter`).
- All auth, billing, checkout, portal, and critical endpoints declare per-route
  limits (for example: `10/minute` for register/checkout, `60/minute` for
  plans/status, `200/minute` for Stripe webhooks).
- Limiters default to client IP via `get_remote_address`.

## 7. Database & Audit Retention

- `database.py` does not auto-commit. `get_db()` yields an `AsyncSession` and
  rolls back only on unhandled exceptions.
- Financial and audit tables use `ON DELETE SET NULL` on user references so
  deleting a user does not erase transaction history (`broker_orders`,
  `pnl_daily`, `stripe_events`, and others).
- GDPR deletion anonymises PII but preserves immutable records for compliance.

## 8. Frontend Security

- The access token is never persisted to `localStorage`; only a short-lived
  in-memory string is kept.
- `SecurityHeadersMiddleware` adds CSP, HSTS, `X-Frame-Options`,
  `X-Content-Type-Options`, and `Referrer-Policy`.
- CSP `script-src` is locked to `'self'` + trusted CDNs; `unsafe-eval` is
  removed in the production bundle.
- All async `fetch` paths use `AbortController` to cancel in-flight requests on
  unmount or navigation.

## 9. Compliance Language (TSYS-13a)

*(Folded in from the retired `docs/COMPLIANCE_LANGUAGE_AUDIT.md`; last audit run 2026-06-07.)*

**Method:** grep across `frontend/`, `backend/`, `docs/` for prohibited-claim patterns
(`guarantee[d]`, `risk-free`, `will profit`, `can't lose`, `sure thing`, `riskless`) and for
required disclaimers (`not financial advice`, `past performance`, `informational/educational`).

**Last result: no prohibited performance or suitability claims found.** All `risk-free` hits are
the risk-free *rate* in scoring code; all `guarantee` hits are disclaimers or code comments.
Required disclaimers are present on every surface: README/public site, email footer
(`email_svc.py`), Telegram/Discord signal messages ("NOT FINANCIAL ADVICE"), and live broker
auto-execution is gated by an explicit, immutably-recorded risk acknowledgement
(`POST /api/me/risk-acknowledge`, TSYS-13b/13c).

**Standing rules:**
1. Re-run the grep audit before each marketing push; extend the pattern list as copy expands.
2. The risk-ack UI must render the suitability/risk disclosure *before* the user acknowledges
   (consent must be informed, not just recorded).
3. Prefer "algorithmic signal" over "recommendation" in auto-execution copy to reduce
   RIA-advice ambiguity.

> This is engineering due diligence, not legal advice — a securities/fintech attorney should
> review before paid marketing or live-trading GA.
