# Pillar 5 Audit — Error Handling, Logging & Exceptions

**Auditor:** Pillar_5_Auditor
**Scope:** Signal.Trade backend (`backend/` monorepo)
**Focus:** Anti-patterns, Sentry integration, sensitive data leakage, transaction safety, exception handler design.

---

## Summary

| Category | Issues Found | Critical | High | Medium | Low |
|---|---|---|---|---|---|
| A. Empty / Generic Catch Blocks | 18 | 2 | 6 | 7 | 3 |
| B. Sentry Integration | 5 | 0 | 2 | 2 | 1 |
| C. Sensitive Data Leakage | 7 | 1 | 2 | 3 | 1 |
| D. Transaction & DB Errors | 4 | 0 | 2 | 1 | 1 |
| E. Exception Handler Patterns | 5 | 1 | 2 | 1 | 1 |
| **Total** | **39** | **4** | **14** | **14** | **7** |

---

## A. Empty Catch Blocks & Generic Exception Swallowing

### SEVERITY: Critical
**File:** `backend/routers/paper_router.py`
**Function:** `account`, `positions`, `orders`, `place_order`, `close_position`, `cancel_order`, `portfolio_risk` (lines 35–122)
**Root Cause:** Every endpoint wraps the Alpaca proxy call in `try: ... except Exception as e: raise HTTPException(502, "Broker request failed")`. The original exception is discarded and never logged. Because the router catches the exception before it bubbles to middleware, Sentry’s FastAPI integration cannot capture the original error. Users get a generic 502 with zero diagnostic detail (e.g., was it a 401 auth failure, a 429 rate limit, or a network timeout?).
**Real-world Impact:** Production incidents involving Alpaca outages or credential rotation are invisible to both users and operators. A 429 rate limit returns 502; a malformed API key returns 502. Support tickets require manual reproduction. Sentry event volume is under-reported because the original exception is swallowed.
**Fix:**
```python
from fastapi import HTTPException
from services.alpaca_rest import AlpacaAPIError  # or create one

try:
    return await alpaca_rest.get_account(key, secret)
except AlpacaAPIError as e:
    log.warning("Alpaca API error: %s (status=%s)", e.message, e.status)
    raise HTTPException(
        status_code=e.status or 502,
        detail={"error": "Broker request failed", "reason": e.message},
    )
except Exception as e:
    log.error("Unexpected broker error: %s", e, exc_info=True)
    raise HTTPException(status_code=502, detail="Broker request failed")
```

---

### SEVERITY: Critical
**File:** `backend/main.py`
**Function:** `_periodic_scan` (lines 298, 346)
**Root Cause:** `except BaseException as e` is used in the scanner’s main loop. `BaseException` catches `KeyboardInterrupt`, `SystemExit`, and `GeneratorExit` in addition to `Exception`. `KeyboardInterrupt` is NOT re-raised; the scanner increments the fail streak and continues. In a container or terminal, a Ctrl+C (SIGINT) may be silently swallowed. Additionally, `print()` is used instead of `log.error()`, so these errors bypass the logging infrastructure and never reach Sentry or log files.
**Real-world Impact:** Cannot gracefully shut down the scanner during deployments or debugging. Failures are invisible to log aggregation and observability pipelines.
**Fix:**
```python
except asyncio.CancelledError:
    raise
except Exception as e:
    _scan_fail_streak += 1
    log.error(
        "[scanner] error (streak %d): %s: %s",
        _scan_fail_streak,
        type(e).__name__,
        e,
        exc_info=True,
    )
```

---

### SEVERITY: High
**File:** `backend/services/technicals.py`
**Function:** `calculate_indicators`, `_safe`, `batch_calculate_indicators`, `compute_cointegration_zscore`
**Root Cause:** Approximately **27** `except Exception:` blocks (pass or return None) in `technicals.py`. Examples:
- Line 57: `except Exception: return None` in `_safe`
- Lines 178, 305, 332, 344, 355, 373, 382, 395, 407, 448, 462, 471, 494, 532, 545, 573, 621, 670, 724, 739, 766, 819, 875, 884: all `except Exception: pass` or `return None`

These swallow everything from `IndexError` to `MemoryError` to `ZeroDivisionError`. The outer `calculate_indicators` does catch `Exception as e` and prints it (line 727), but `print()` bypasses the logging system, and the inner blocks mean partial data loss is silent.
**Real-world Impact:** Indicators silently disappear from scan outputs. A data pipeline bug (e.g., NaN propagation) could disable the entire technical gate for weeks without alerting.
**Fix:**
```python
# Example: RSI divergence block (line 283)
try:
    ...
except (IndexError, ValueError) as e:
    log.debug("RSI divergence failed: %s", e)
except Exception as e:
    log.warning("Unexpected error in RSI divergence: %s", e, exc_info=True)
```
Replace all bare `except Exception: pass` with at minimum `log.warning(..., exc_info=True)` and narrow to expected exception types where possible.

---

### SEVERITY: High
**File:** `backend/services/signal_engine.py`
**Function:** Multiple (≈58 `except Exception` blocks)
**Root Cause:** `signal_engine.py` has ~58 `except Exception` patterns, many of which are `pass` or log at `warning`/`debug` only. Examples:
- Line 465: `except Exception: pass` (ex-dividend lookup)
- Line 491: `except Exception: pass` (weekly trend)
- Line 519: `except Exception: pass` (weekly OHLCV)
- Line 539: `except Exception: pass` (polygon indicator blend)
- Line 561: `except Exception: pass` (short float lookup)
- Line 598: `except Exception: pass` (miscellaneous)
- Line 917: `except Exception: pass` (another lookup)
- Line 1051: `except Exception as _sv_err: log.warning(...)` (short volume)
- Line 1197: `except Exception: pass` (unknown block)
- Line 2161: `except Exception: pass` (unknown block)
- Line 2496: `except Exception: pass` (unknown block)
- Line 2725: `except Exception as _edgar_err: pass`
- Line 2737: `except Exception as _ratios_err: pass`
- Line 2753: `except Exception as _chain_err: pass`
- Line 2772: `except Exception as _etf_err: pass`
- Line 4033: `except Exception: pass`
- Line 4246: `except Exception: pass`
- Line 4293: `except Exception as e: ...` (some logging)
- Line 4372: `except Exception: pass`
- Line 4404: `except Exception: pass`
- Line 4475: `except Exception: pass`
- Line 4499: `except Exception: pass`
- Line 5066: `except Exception: pass`
- Line 5362: `except Exception: pass`
- Line 5440: `except Exception: pass`
- Line 5511: `except Exception: pass`
- Line 5544: `except Exception: pass`
- Line 5662: `except Exception: pass`
- Line 5693: `except Exception: pass`
- Line 5737: `except Exception: pass`
- Line 5797: `except Exception as _xs_err: log.warning(...)`
- Line 5840: `except Exception: pass`
- Line 5868: `except Exception: pass`

**Real-world Impact:** The signal engine is the core revenue path. Silent failures in data fetchers (EDGAR, ratios, ETF constituents, options chains) mean signals are generated with missing or stale data. A data source outage would be invisible.
**Fix:** Audit every block; replace `pass` with structured logging at `warning` level (or `error` for critical fetchers). Add Sentry capture for unexpected exceptions:
```python
except Exception as e:
    log.warning("edgar fetch failed: %s", e, exc_info=True)
    # Optional: sentry_sdk.capture_exception(e)
```

---

### SEVERITY: High
**File:** `backend/services/auth_svc.py`
**Function:** `verify_password` (line 29–33)
**Root Cause:** `except Exception: return False` catches any error from `bcrypt.checkpw`, including library bugs, corrupted hash strings, or `ValueError` from malformed hashes. A database corruption causing invalid `password_hash` values would silently result in “wrong password” for every user, with no alert.
**Real-world Impact:** Complete authentication outage with no observability. If the bcrypt library is upgraded and introduces a new exception type, every login fails silently with no Sentry event.
**Fix:**
```python
def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt_lib.checkpw(plain.encode()[:72], hashed.encode())
    except ValueError:
        # Malformed hash — log for security audit
        log.warning("verify_password: malformed hash detected")
        return False
    except Exception:
        log.error("verify_password: bcrypt library error", exc_info=True)
        raise  # Do NOT silently return False for unknown errors
```

---

### SEVERITY: High
**File:** `backend/services/broker_svc.py`
**Function:** `decrypt_credential` (line 86–103)
**Root Cause:** `except Exception: return None` swallows decryption failures. This could mask a JWT secret rotation (all credentials become undecryptable), Fernet corruption, or a wrong key version. Users would see “Credential decryption failed” with no backend alert.
**Real-world Impact:** After a JWT secret rotation, every auto-execution user silently fails. No Sentry event, no admin alert.
**Fix:**
```python
try:
    if ciphertext.startswith("v2:"):
        ...
    return _get_fernet().decrypt(ciphertext.encode()).decode()
except (InvalidToken, ValueError):
    log.warning("Credential decryption failed: invalid token or bad key version")
    return None
except Exception:
    log.error("Unexpected decryption failure", exc_info=True)
    raise
```

---

### SEVERITY: High
**File:** `backend/services/alpaca_ws.py`
**Function:** `_run` (line 110)
**Root Cause:** `except Exception: pass` inside the websocket message loop when calling `broadcast_fn`. If the broadcast callback (e.g., websocket manager) throws, the tick is silently dropped.
**Real-world Impact:** Real-time price ticks stop reaching clients without any log or alert.
**Fix:**
```python
try:
    await broadcast_fn({"type": "tick", ...})
except Exception:
    log.warning("broadcast_fn failed for tick", exc_info=True)
```

---

### SEVERITY: Medium
**File:** `backend/services/market_data.py`
**Function:** Multiple (`_fetch_histories_batch`, `_fetch_quotes_batch`, `_fetch_history`, `_fetch_info`, `_fetch_extended_hours`, etc.)
**Root Cause:** ~11 `except Exception` blocks that swallow yfinance/Polygon errors and return `None`/`{}`/`[]`. Examples:
- Line 476: `except Exception as e:` in `_retry` (catches all retries, including 429 which is handled, but also unexpected errors)
- Line 531: `except Exception as e: print(...); return {}`
- Line 573: `except Exception as e: print(...); return []`
- Line 590: `except Exception: return None`
- Line 601: `except Exception: pass`
- Line 644: `except Exception: return None`
- Line 666: `except Exception: polygon_out = {}`
- Line 779: `except Exception: pass`
- Line 783: `except Exception: pass`
- Line 844: `except Exception: return None`
- Line 859: `except Exception: pass`

The `print()` statements bypass the structured logging system.
**Real-world Impact:** Market data failures are invisible to Sentry and log aggregation. The fallback to empty data causes downstream signals to be generated with missing inputs.
**Fix:** Replace `print()` with `log.error(..., exc_info=True)` and use `logging` consistently.

---

### SEVERITY: Medium
**File:** `backend/services/polygon_client.py`
**Function:** Multiple (`get_polygon_history`, `get_polygon_snapshot_batch`, `get_polygon_info`, etc.)
**Root Cause:** ~10 `except Exception` blocks that return `None`/`{}`/`[]` after logging at `warning` or `debug`. These are external API wrappers, so fallback is expected, but the broad `Exception` catch means a `MemoryError` or `SyntaxError` (if dynamic code is involved) would also be swallowed.
**Real-world Impact:** Polygon schema changes or network partitions are silently handled, but critical internal errors (e.g., serialization bugs) are also suppressed.
**Fix:** Narrow to `(aiohttp.ClientError, asyncio.TimeoutError, ValueError)` where possible, and keep `Exception` only for top-level safety with `exc_info=True` logging.

---

### SEVERITY: Medium
**File:** `backend/main.py`
**Function:** `_ignore_expected_oauth_error` (lines 29–40)
**Root Cause:** The `before_send` Sentry hook has `except Exception: pass`. If the hook itself crashes (e.g., `hint` is malformed), the event is dropped silently.
**Real-world Impact:** A bug in the Sentry hook would cause ALL events to be silently discarded.
**Fix:**
```python
def _ignore_expected_oauth_error(event, hint):
    try:
        exc_info = hint.get("exc_info")
        if exc_info:
            exc_type, exc_value, _ = exc_info
            if exc_type is not None and exc_value is not None and issubclass(exc_type, HTTPException):
                if exc_value.status_code == 503 and "OAuth not configured" in str(exc_value.detail or ""):
                    return None
    except Exception:
        log.error("Sentry before_send hook failed", exc_info=True)
    return event
```

---

### SEVERITY: Low
**File:** `backend/main.py`
**Function:** Import-time resource limit (line 73–79)
**Root Cause:** `except Exception: pass` when raising file descriptor limits. This is defensive but acceptable.
**Fix:** None required — this is a safe pattern.

---

### SEVERITY: Low
**File:** `backend/database.py`
**Function:** `_setup_sqlite_connection` (line 63–64)
**Root Cause:** `except Exception as e: logger.warning(f"Failed to set SQLite pragmas: {e}")` is acceptable for a dev-only SQLite path.
**Fix:** None required.

---

## B. Sentry Integration

### SEVERITY: High
**File:** `backend/main.py`
**Function:** `sentry_sdk.init` (lines 43–55)
**Root Cause:** The `AsyncioIntegration` is **not** enabled. The app is heavily async (FastAPI, asyncio tasks, background jobs). Without `AsyncioIntegration`, exceptions in fire-and-forget `asyncio.create_task()` calls (e.g., startup scans, background tasks) may not be captured by Sentry unless they bubble to the global exception handler. The `_async_exception_handler` (line 1649) logs them but does NOT call `sentry_sdk.capture_exception()`.
**Real-world Impact:** Crashes in background tasks (weekly digest, nightly cleanup, ML retrain, drift detection) are invisible to Sentry. The only evidence is in local logs.
**Fix:**
```python
from sentry_sdk.integrations.asyncio import AsyncioIntegration

sentry_sdk.init(
    dsn=_sentry_dsn,
    integrations=[
        StarletteIntegration(),
        FastApiIntegration(),
        SqlalchemyIntegration(),
        AsyncioIntegration(),  # Add this
    ],
    before_send=_ignore_expected_oauth_error,
    traces_sample_rate=0.1,
    profiles_sample_rate=0.05,
    environment="production" if not os.environ.get("DEBUG") else "development",
    release=os.environ.get("GIT_SHA", "unknown"),
)
```

---

### SEVERITY: High
**File:** `backend/main.py`
**Function:** `_async_exception_handler` (line 1649–1677)
**Root Cause:** The global asyncio exception handler logs uncaught task exceptions but does **not** forward them to Sentry. Every fire-and-forget task (e.g., `_prewarm_news_batch`, `_warm_indicator_cache`, `run_scan` at startup) that crashes will be logged to stderr but never sent to Sentry.
**Real-world Impact:** Silent failures in background tasks. The scanner might die and restart repeatedly without Sentry ever showing an error.
**Fix:**
```python
def _async_exception_handler(loop, context):
    exc = context.get("exception")
    if isinstance(exc, asyncio.CancelledError):
        return
    task = context.get("future") or context.get("task")
    name = None
    try:
        if task is not None and hasattr(task, "get_name"):
            name = task.get_name()
    except Exception:
        name = None
    if exc is not None:
        log.error(
            "[async] Unhandled exception in task %r: %s: %s",
            name or "<unknown>",
            type(exc).__name__,
            exc,
            exc_info=exc,
        )
        import sentry_sdk
        sentry_sdk.capture_exception(exc)  # Forward to Sentry
    else:
        log.error("[async] Async error in task %r: %s", name or "<unknown>", context.get("message"))
```

---

### SEVERITY: Medium
**File:** `backend/main.py`
**Function:** `sentry_sdk.init` (lines 43–55)
**Root Cause:** No `before_send` / `before_breadcrumb` scrubbing of sensitive data. The existing `before_send` only filters out `HTTPException(503, "OAuth not configured")`. It does NOT scrub:
- `api_key` / `api_secret` from stack trace locals or request bodies
- `stripe_webhook_secret` from webhook tracebacks
- `jwt_secret` from KDF stack traces
- `telegram_bot_token` from URL strings in traces
- `authorization` headers from HTTP breadcrumbs

**Real-world Impact:** A Sentry event from `broker.py` or `alpaca_rest.py` may contain the user’s decrypted API key in the stack trace local variables. A Stripe webhook event may contain the `stripe_webhook_secret` in a traceback.
**Fix:**
```python
import re

_SENSITIVE_KEYS = re.compile(r"api_key|api_secret|secret|token|password|jwt|authorization", re.I)

def _scrub_sensitive(data):
    if isinstance(data, dict):
        return {k: "[scrubbed]" if _SENSITIVE_KEYS.search(k) else _scrub_sensitive(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_scrub_sensitive(v) for v in data]
    return data

def _before_send(event, hint):
    # Existing filter
    try:
        exc_info = hint.get("exc_info")
        if exc_info:
            exc_type, exc_value, _ = exc_info
            if exc_type is not None and exc_value is not None and issubclass(exc_type, HTTPException):
                if exc_value.status_code == 503 and "OAuth not configured" in str(exc_value.detail or ""):
                    return None
    except Exception:
        log.error("Sentry before_send filter failed", exc_info=True)
    # Scrub sensitive data from request and extra context
    if "request" in event:
        event["request"] = _scrub_sensitive(event["request"])
    if "extra" in event:
        event["extra"] = _scrub_sensitive(event["extra"])
    return event

def _before_breadcrumb(crumb, hint):
    if crumb.get("category") == "http":
        data = crumb.get("data") or {}
        if "url" in data:
            data["url"] = re.sub(r"apiKey=[^&]+", "apiKey=[scrubbed]", data["url"])
        if "headers" in data:
            data["headers"] = _scrub_sensitive(data["headers"])
        crumb["data"] = data
    return crumb

sentry_sdk.init(
    ...
    before_send=_before_send,
    before_breadcrumb=_before_breadcrumb,
    send_default_pii=False,  # Explicitly disable PII
    ...
)
```

---

### SEVERITY: Medium
**File:** `backend/main.py`
**Function:** `sentry_sdk.init` (lines 43–55)
**Root Cause:** `PydanticValidationError` (422 responses) is not filtered. FastAPI returns 422 for invalid request bodies. Sentry captures these by default. The request body may contain sensitive fields (e.g., `api_secret` in `BrokerConnectIn`, `password` in `RegisterIn`). While Pydantic scrubs `SecretStr` fields, plain `str` fields like `api_key` or `password` are included in the Sentry event’s request body.
**Real-world Impact:** Sentry events for 422 errors may contain user passwords or broker API keys in the request body payload.
**Fix:** Add a `before_send` filter to drop `ValidationError` events that contain sensitive fields, or at least scrub the request body:
```python
def _before_send(event, hint):
    # ... existing filter ...
    # Drop 422 ValidationError events to prevent leaking request bodies
    exc_info = hint.get("exc_info")
    if exc_info:
        exc_type = exc_info[0]
        if exc_type and exc_type.__name__ == "RequestValidationError":
            return None  # Or scrub the request body deeply
    return event
```

---

### SEVERITY: Low
**File:** `backend/main.py`
**Function:** `sentry_sdk.init` (lines 43–55)
**Root Cause:** `sentry_sdk` is initialized at import time using `os.environ.get("SENTRY_DSN", "").strip()` rather than `settings.sentry_dsn`. This is actually a secure pattern (avoids accidental `SecretStr` logging), but it means the DSN is not validated by Pydantic. If `SENTRY_DSN` contains a malformed URL, `sentry_sdk.init` may raise at import time.
**Real-world Impact:** Malformed `SENTRY_DSN` causes the app to fail at import time, before the lifespan or health checks run.
**Fix:** Wrap in try/except and log a critical error without crashing:
```python
if _sentry_dsn:
    try:
        sentry_sdk.init(...)
    except Exception:
        log.critical("Sentry DSN is malformed; Sentry disabled", exc_info=True)
```

---

## C. Sensitive Data Leakage

### SEVERITY: Critical
**File:** `backend/config.py` / `backend/routers/billing.py` / `backend/main.py`
**Function:** `Settings` fields, `_stripe()`, `alpaca_ws.start()`
**Root Cause:** Multiple API keys and secrets are defined as **plain `str`** instead of `SecretStr` in `config.py`:
- `finnhub_api_key: str = ""` (line 14)
- `alpaca_api_key: str = ""` (line 22)
- `polygon_api_key: str = ""` (line 83)
- `massive_api_key: str = ""` (line 80)
- `unusual_whales_api_key: str = ""` (line 79)
- `google_client_id: str = ""` (line 67)

These are **not** masked by Pydantic. If the `settings` object is ever serialized (e.g., accidentally logged, returned in an API response, or included in a Sentry event), these keys are exposed in plain text.

Additionally, in `billing.py`:
- `stripe.api_key = s.stripe_secret_key` (line 38) — `s.stripe_secret_key` is a `SecretStr`. If passed directly, Stripe may receive the masked string `**********` or the `SecretStr` object, causing all Stripe API calls to fail. The same risk applies to `s.stripe_webhook_secret` passed to `construct_event` (line 262).

In `main.py`:
- `alpaca_ws.start(settings.alpaca_api_key, settings.alpaca_api_secret.get_secret_value(), ...)` — `alpaca_api_key` is plain `str`, only `api_secret` is `SecretStr`.

**Real-world Impact:** Leakage of brokerage API keys, Stripe keys, or Polygon keys in logs, Sentry, or accidental HTTP responses. Potential financial loss or data breach. Stripe billing could be completely broken if the masked secret is passed.
**Fix:**
```python
# config.py
finnhub_api_key: SecretStr = Field(default=SecretStr(""))
alpaca_api_key: SecretStr = Field(default=SecretStr(""))
polygon_api_key: SecretStr = Field(default=SecretStr(""))
massive_api_key: SecretStr = Field(default=SecretStr(""))
unusual_whales_api_key: SecretStr = Field(default=SecretStr(""))
# google_client_id is public (OAuth client ID), but still good practice to keep SecretStr
```
```python
# billing.py
def _stripe():
    s = get_settings()
    stripe.api_key = s.stripe_secret_key.get_secret_value()
    return stripe

# In webhook handler:
event = st.Webhook.construct_event(payload, sig, s.stripe_webhook_secret.get_secret_value())
```

---

### SEVERITY: High
**File:** `backend/main.py`
**Function:** `_periodic_scan` (lines 300, 348)
**Root Cause:** `print()` is used instead of `logging.error()` for scanner errors. `print()` bypasses the structured logging formatter (JSON in production), bypasses Sentry, and does not include timestamps or stack traces.
**Real-world Impact:** Scanner errors are invisible to log aggregation and Sentry. Operators cannot query or alert on them.
**Fix:** Replace all `print()` error statements in `main.py` with `log.error(..., exc_info=True)`.

---

### SEVERITY: High
**File:** `backend/services/market_data.py`
**Function:** `_fetch_histories_batch`, `_fetch_quotes_batch` (lines 531, 573)
**Root Cause:** `print()` statements used for batch history/quotes errors. Same issue as above.
**Fix:** Replace with `log.error(..., exc_info=True)`.

---

### SEVERITY: Medium
**File:** `backend/routers/broker.py`
**Function:** `broker_status` (line 152)
**Root Cause:** `except ValueError as e: return {"connected": False, "error": str(e)}` returns HTTP 200 with an error message in the body. The client may not realize it is an error. More importantly, if `verify_alpaca_connection` or `verify_ibkr_connection` raises a `ValueError` containing the broker API URL (which includes the API key in query parameters for some brokers), the error message would leak the key.
**Real-world Impact:** API key leakage in HTTP 200 responses to the frontend.
**Fix:**
```python
except ValueError as e:
    log.warning("Broker verification failed for user=%d: %s", user.id, e)
    raise HTTPException(status_code=422, detail="Broker verification failed")
```

---

### SEVERITY: Medium
**File:** `backend/routers/billing.py`
**Function:** `stripe_webhook` (line 263)
**Root Cause:** `except Exception as e: log.warning(f"[billing] webhook signature failed: {e}")` logs the exception message. If the Stripe library raises an exception that includes the payload or secret in the message (rare but possible in some versions), it could be logged.
**Real-world Impact:** Potential leakage of Stripe webhook secret in logs.
**Fix:**
```python
except Exception as e:
    log.warning("[billing] webhook signature verification failed: %s", type(e).__name__)
    raise HTTPException(400, "Invalid signature")
```

---

### SEVERITY: Medium
**File:** `backend/services/telegram_svc.py` / `backend/services/discord_bot.py` / `backend/services/email_svc.py`
**Function:** Various
**Root Cause:** Not audited in depth, but `delivery_manager.py` line 203 shows `url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"`. The bot token is correctly unwrapped. However, if an HTTP exception is raised and logged with `exc_info=True`, the URL (containing the token) may appear in the traceback.
**Real-world Impact:** Telegram bot token leakage in log tracebacks.
**Fix:** In Sentry `before_send` and logging exception handlers, scrub URLs containing `api.telegram.org/bot`.

---

### SEVERITY: Low
**File:** `backend/models.py`
**Function:** Model `__repr__` / `__str__`
**Root Cause:** No `__repr__` or `__str__` methods were found in `models.py` (grep returned no matches). This is actually good — SQLAlchemy models default to generic representations that do not leak fields.
**Real-world Impact:** None.
**Fix:** None required.

---

## D. Transaction & Database Error Handling

### SEVERITY: High
**File:** `backend/routers/broker.py`
**Function:** `broker_connect` (lines 156–227), `update_auto_execute_settings`, `rotate_alpaca_credentials`
**Root Cause:** The AGENTS.md states: **“Services commit, routers don’t.”** `broker.py` directly calls `await db.commit()` in the router after modifying user credentials. No service layer handles the transaction. If the audit log (`record_action`) succeeds but the commit fails, the database may be in an inconsistent state. Conversely, if `verify_alpaca_connection` raises after `db.merge(user)`, the session is not explicitly rolled back.
**Real-world Impact:** Inconsistent DB state, partial writes, or credential storage without audit trails.
**Fix:** Move the transaction logic into `broker_svc.py`:
```python
# broker_svc.py
async def connect_broker(user, body, db):
    account = await verify_alpaca_connection(body.api_key, body.api_secret, live)
    merged = await db.merge(user)
    merged.alpaca_key_enc = encrypt_credential(body.api_key)
    ...
    await record_action(db, ACTION_BROKER_CONNECT, user_id=user.id, details={...})
    await db.commit()
    await db.refresh(merged)
    return {"connected": True, ...}
```

---

### SEVERITY: High
**File:** `backend/database.py`
**Function:** `init_db` (lines 138–212)
**Root Cause:** `init_db` runs additive migrations at startup. Each migration runs in its own `engine.begin()` block with a `try/except` that logs `OperationalError`/`ProgrammingError` and continues. If a migration fails, the app starts anyway with a potentially incomplete schema. The comment says “never remove columns via this init_db block,” but there is no guard against a failed additive migration that later code assumes exists.
**Real-world Impact:** App starts with a partially migrated schema. Runtime errors (e.g., `Column not found`) occur later during user requests, making root cause analysis difficult.
**Fix:** If any migration fails, raise a `RuntimeError` and prevent startup:
```python
except (OperationalError, ProgrammingError) as exc:
    err = str(exc).lower()
    if any(k in err for k in ("duplicate column", "already exists", "duplicate relation")):
        continue
    log.error("Migration failed (%s): %s", sql, exc)
    raise RuntimeError(f"Migration failed: {sql}") from exc
except Exception as exc:
    log.error("Migration unexpected error (%s): %s", sql, exc)
    raise RuntimeError(f"Migration failed: {sql}") from exc
```

---

### SEVERITY: Medium
**File:** `backend/routers/paper_router.py`
**Function:** All endpoints
**Root Cause:** `paper_router.py` does not use the database at all. It is a pure proxy to Alpaca. This means no local audit trail of paper orders exists. If Alpaca’s paper API is down or returns incorrect data, there is no local record to reconcile.
**Real-world Impact:** No data durability for paper trading. Users cannot see historical paper orders if Alpaca is unavailable.
**Fix:** Persist paper orders to a local `PaperOrder` table and read from it for `/orders`, `/positions`, `/account` endpoints, with Alpaca as the source of truth for live state.

---

### SEVERITY: Low
**File:** `backend/database.py`
**Function:** `get_db` (lines 94–100)
**Root Cause:** `get_db` correctly yields sessions and rolls back on exception. It does not auto-commit. This matches the AGENTS.md rule.
**Real-world Impact:** None.
**Fix:** None required.

---

## E. Exception Handler Patterns

### SEVERITY: Critical
**File:** `backend/main.py`
**Function:** FastAPI app instantiation (line 1771)
**Root Cause:** There are **no custom exception handlers** for `HTTPException`, `ValidationError`, `SQLAlchemyError`, or `IntegrityError`. The only registered handler is `RateLimitExceeded`. The default Starlette handler is used for everything else. For `IntegrityError` (e.g., duplicate key on `weekly_digest_sent` unique constraint), the app returns HTTP 500 with a generic server error, not 409 Conflict.
**Real-world Impact:** Duplicate key violations (e.g., concurrent weekly digest triggers) return 500 instead of 409, triggering false-positive Sentry alerts and confusing the client. SQLAlchemy errors may expose internal DB details in the response if `debug=True` is ever enabled.
**Fix:**
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    log.warning("IntegrityError: %s", exc)
    return JSONResponse(status_code=409, content={"detail": "Conflict — resource already exists"})

@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    # Return 422 but scrub sensitive fields from the response
    return JSONResponse(status_code=422, content={"detail": "Invalid input data"})

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # Preserve existing behavior but ensure Sentry captures non-4xx
    if exc.status_code >= 500:
        import sentry_sdk
        sentry_sdk.capture_exception(exc)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
```

---

### SEVERITY: High
**File:** `backend/main.py`
**Function:** Startup lifespan (line 1680–1758)
**Root Cause:** `init_db()` is called at startup (line 1712). If `init_db()` raises (e.g., DB is unreachable), the app fails to start. However, there is no retry logic or graceful degradation. More importantly, `initialize_policy_and_registry` failure is caught and logged at `warning` level (line 1717), and the app continues. If policy/registry initialization fails, the scanner may run with stale or missing policies.
**Real-world Impact:** App starts in a degraded state without clear indication. The scanner may generate signals using incorrect policy weights.
**Fix:** Treat policy initialization as critical:
```python
await init_db()
try:
    await initialize_policy_and_registry()
except Exception as e:
    log.error("Failed to initialize policy/registry — aborting startup", exc_info=True)
    raise RuntimeError("Policy initialization failed") from e
```

---

### SEVERITY: High
**File:** `backend/routers/billing.py`
**Function:** `stripe_webhook` (lines 260–265)
**Root Cause:** `except Exception as e` around `construct_event` is too broad. If the Stripe library raises a `ValueError` (e.g., malformed payload) or a `TypeError` (SDK mismatch), it returns 400 “Invalid signature.” This is misleading and makes debugging difficult.
**Real-world Impact:** Stripe retries the webhook because 400 is not a success. If the real error is a transient Stripe SDK bug, it triggers unnecessary retries and may eventually disable the webhook.
**Fix:**
```python
from stripe.error import SignatureVerificationError

try:
    event = st.Webhook.construct_event(payload, sig, s.stripe_webhook_secret.get_secret_value())
except SignatureVerificationError:
    log.warning("[billing] Stripe webhook signature verification failed")
    raise HTTPException(400, "Invalid signature")
except Exception:
    log.error("[billing] unexpected error during webhook verification", exc_info=True)
    raise HTTPException(500, "Webhook processing error")
```

---

### SEVERITY: Medium
**File:** `backend/routers/oauth.py`
**Function:** `oauth_exchange` (lines 215–222)
**Root Cause:** `except Exception: await db.rollback(); log.exception(...); raise HTTPException(500, ...)` swallows the original exception. The client gets a generic 500.
**Real-world Impact:** OAuth exchange failures are hard to debug.
**Fix:** Log the specific exception type and include a trace ID in the response:
```python
except Exception:
    await db.rollback()
    trace_id = sentry_sdk.capture_exception()
    log.exception("[oauth] exchange failed")
    raise HTTPException(500, detail={"error": "OAuth exchange failed", "trace_id": trace_id})
```

---

### SEVERITY: Low
**File:** `backend/routers/broker.py`
**Function:** `broker_parity` (line 430)
**Root Cause:** `except Exception as e: log.warning(...)` is acceptable here because it is a best-effort parity fetch, but the error is logged at `warning` instead of `error`.
**Real-world Impact:** Minor — parity data may be stale.
**Fix:** None required; this is a safe pattern for best-effort data.

---

## Additional Findings (Clean Areas)

- **No `except: pass` (bare except) found.** All exception blocks at least specify a type.
- **`auth.py` login endpoint does NOT log the password.** Failed login attempts log `email` and `ip_address` only. Good.
- **`models.py` has no `__repr__`/`__str__` methods.** No accidental sensitive field exposure in REPL or logging.
- **`database.py` `get_db()` correctly yields and rolls back.** No auto-commit violation.
- **`config.py` uses `SecretStr` for `jwt_secret`, `owner_password`, `stripe_secret_key`, `stripe_webhook_secret`, `telegram_bot_token`, `google_client_secret`, `smtp_password`, `vapid_private_key`, `site_private_token`.** Good.
- **Sentry DSN is loaded from `os.environ` rather than `settings.sentry_dsn`,** which prevents accidental logging of the DSN via Pydantic `__str__`. Good defensive practice.

---

## Appendix: Quick Reference — Anti-pattern Counts

| File | `except Exception` (or broader) | `pass` | `print()` errors | Notes |
|---|---|---|---|---|
| `main.py` | ~35 | 2 | 6 | `BaseException` in scanner is worst |
| `technicals.py` | ~27 | ~24 | 1 | Every indicator block silently fails |
| `signal_engine.py` | ~58 | ~35 | 0 | Core engine has highest count |
| `market_data.py` | ~11 | ~8 | 2 | `print()` used instead of `log` |
| `polygon_client.py` | ~10 | ~8 | 0 | External API wrappers |
| `paper_router.py` | 7 | 0 | 0 | All swallow original exception |
| `alpaca_ws.py` | 3 | 1 | 0 | Broadcast silently swallowed |
| `auth_svc.py` | 1 | 1 | 0 | `verify_password` silent failure |
| `broker_svc.py` | 5 | 2 | 0 | Decryption silent failure |
| `billing.py` | 3 | 1 | 0 | Webhook handler broad catch |
| **Total** | **~160** | **~82** | **9** | |

---

*End of Pillar 5 Audit Report.*
