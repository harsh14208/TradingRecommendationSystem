# Signal.Trade — Runbook (DEPLOY-4)

## Overview

This runbook covers deployment, configuration verification, incident response, and routine maintenance for the Signal.Trade backend (FastAPI + SQLite/PostgreSQL, Railway/Fly.io).

---

## 1. First-Time Deployment Checklist

### 1.1 Environment Variables (`.env` → production secrets)

Set all of the following before the first `railway up` or `fly deploy`:

| Variable | Required | Description |
|---|---|---|
| `OWNER_EMAIL` | ✅ | Admin account email |
| `OWNER_PASSWORD` | ✅ | 16+ chars, mixed case + symbols. **Fixed 2026-06-09** — `.env` has 32-char secure password; startup fails on `ChangeMe123!` in production. |
| `JWT_SECRET` | ✅ | 64 random chars: `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | ✅ (prod) | `postgresql://user:pass@host:5432/dbname` — leave empty for SQLite (dev only) |
| `STRIPE_SECRET_KEY` | ✅ | From Stripe Dashboard → API Keys |
| `STRIPE_WEBHOOK_SECRET` | ✅ | From Stripe → Webhooks → Signing secret (`whsec_...`) |
| `STRIPE_PRICE_BASIC` | ✅ | Stripe price ID for Basic tier |
| `STRIPE_PRICE_PRO` | ✅ | Stripe price ID for Pro tier |
| `TELEGRAM_BOT_TOKEN` | ✅ | From @BotFather on Telegram |
| `POLYGON_API_KEY` | ✅ | Polygon.io market data API key |
| `SMTP_HOST` | Strongly rec. | Email delivery host (e.g., `smtp.sendgrid.net`) |
| `SMTP_PORT` | Strongly rec. | Usually 587 (STARTTLS) |
| `SMTP_USER` | Strongly rec. | SMTP username |
| `SMTP_PASSWORD` | Strongly rec. | SMTP password / API key |
| `APP_URL` | ✅ (prod) | Public HTTPS URL: `https://your-app.up.railway.app` |
| `GOOGLE_CLIENT_ID` | Optional | Google OAuth SSO |
| `GOOGLE_CLIENT_SECRET` | Optional | Google OAuth SSO |
| `FRED_API_KEY` | Optional | FRED STLFSI4 macro data (improves signal quality) |
| `LOG_FORMAT` | Optional | Set `json` for structured logging in production |
| `CASH_OVERLAY_ENABLE` | Optional | `true` to auto-invest residual cash (default `false`) |
| `CASH_OVERLAY_TICKER` | Optional | Parking vehicle, default `SGOV` (0–3mo T-bill ETF) |
| `CASH_OVERLAY_BETA_TICKER` | Optional | Beta sleeve, default `VOO` (S&P 500 ETF) |
| `CASH_OVERLAY_MAX_FRACTION` | Optional | Max fraction of equity in overlay, default `0.50` |
| `CASH_OVERLAY_VIX_THRESHOLD` | Optional | VIX level below which beta sleeve is used, default `18.0` |
| `CASH_OVERLAY_MIN_TRADE_DOLLARS` | Optional | Minimum residual order size, default `100.0` |
| `SIGNAL_COHORT_SHADOW_PCT` | Optional | % of signals routed to shadow (logged only), default `0` |
| `SIGNAL_COHORT_WITHHELD_PCT` | Optional | % of signals routed to withheld control group, default `0` |
| `LONG_ONLY` | Optional | `true` (default) disables SELL delivery; `false` enables mirrored SELL MR gate |
| `MAX_SENDS_PER_TICKER_PER_DAY` | Optional | Hard daily send cap per ticker, default `1` (`0` = unlimited) |
| `MAX_BUYS_PER_SECTOR_PER_DAY` | Optional | Hard daily BUY cap per sector, default `2` (`0` = unlimited) |

### 1.2 Deploy Commands

**Railway:**
```bash
railway link          # link to project
railway up            # deploy from local
railway logs          # stream logs
```

**Fly.io:**
```bash
flyctl deploy --remote-only
flyctl logs
```

### 1.3 Post-Deploy Verification

```bash
# 1. Health check (should return {"status": "ok", "db": "connected"})
curl https://your-app/api/health

# 2. Register Stripe webhook
#    → Stripe Dashboard → Webhooks → Add endpoint
#    → URL: https://your-app/api/billing/webhook
#    → Events: customer.subscription.*  checkout.session.completed  invoice.payment_*

# 3. Register Telegram webhook
curl -X POST https://your-app/api/telegram/set-webhook

# 4. Verify owner account (login at /login with OWNER_EMAIL / OWNER_PASSWORD)
```

### 1.4 Residual Cash Overlay

When `CASH_OVERLAY_ENABLE=true`, the portfolio allocator auto-invests any capital not used by active MR signals:

- **Default parking**: `CASH_OVERLAY_TICKER` (SGOV) — 0–3 month T-bill ETF, state-tax-exempt interest, minimal drawdown.
- **Beta sleeve**: `CASH_OVERLAY_BETA_TICKER` (VOO) — used only when all of the following are true:
  - VIX is at or below `CASH_OVERLAY_VIX_THRESHOLD` (default 18)
  - The account is not in a drawdown throttle (portfolio DD ≤ 3%)
  - The engine is not already targeting the beta ticker this cycle
- **Cap**: Total overlay exposure is capped at `CASH_OVERLAY_MAX_FRACTION` (default 50% of equity).
- **Min trade**: Residual orders smaller than `CASH_OVERLAY_MIN_TRADE_DOLLARS` are skipped to avoid micro-trades.

Monitoring:
```bash
# Track invested % vs overlay over time
psql $DATABASE_URL -c "SELECT date, equity, gross_exposure, net_exposure, n_positions FROM pnl_daily ORDER BY date DESC LIMIT 30;"
```

### 1.5 Signal Delivery Tuning

If the system is generating signals but delivering very few, check these knobs first:

| Variable | Effect |
|---|---|
| `SIGNAL_COHORT_SHADOW_PCT` / `SIGNAL_COHORT_WITHHELD_PCT` | Experimental cohorts. Defaults are `0`/`0` so every signal is delivered. Non-zero values silently shadow or withhold signals. |
| `LONG_ONLY` | `true` drops all SELL signals. Set `false` to enable SELL delivery through a mirrored overbought MR gate. |
| `MAX_SENDS_PER_TICKER_PER_DAY` | Hard cap on repeat sends for the same ticker (default `1`). |
| `MAX_BUYS_PER_SECTOR_PER_DAY` | Hard cap on same-sector BUYs (default `2`). |

Telemetry for assembler-level blocks (chronic loser, orthogonality, defensive ticker, saturation, breadth, source independence) is persisted in `signal_gate_traces`:

```bash
# Top assembler/delivery reasons signals become HOLD over last 7 days
psql $DATABASE_URL -c "
SELECT gate_id, passed, count(*)
FROM signal_gate_traces
WHERE signal_id IN (SELECT id FROM signals WHERE created_at >= now() - interval '7 days')
GROUP BY gate_id, passed
ORDER BY count(*) DESC;
"
```

---

## 2. Database Backup and Restore

### 2.1 SQLite (development / small deployments)

```bash
# Backup
sqlite3 backend/trading.db ".backup backup-$(date +%Y%m%d).db"

# Restore
sqlite3 backend/trading.db ".restore backup-20260605.db"
```

### 2.2 PostgreSQL (production)

```bash
# Backup (from Railway CLI or psql)
pg_dump $DATABASE_URL > backup-$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup-20260605.sql
```

### 2.3 Automated Backups

Set up a Railway scheduled task or cron job to run daily backup to Cloudflare R2 / S3:

```bash
# R2 upload (using wrangler or rclone)
rclone copy backend/trading.db r2:signal-trade-backups/$(date +%Y/%m/%d)/trading.db
```

Retention policy: 7 daily, 4 weekly (delete older automatically).

---

## 3. Rollback Procedure

### 3.1 Railway

```bash
# List recent deployments
railway deployments

# Roll back to previous deployment
railway rollback <deployment-id>
```

### 3.2 Fly.io

```bash
flyctl releases list
flyctl deploy --image registry.fly.io/signal-trade:<previous-version>
```

### 3.3 Code rollback

```bash
# Revert last commit and redeploy
git revert HEAD --no-edit
git push origin main
# CI/CD auto-deploys on merge to main
```

---

## 4. Stripe Webhook Re-Registration

After changing `APP_URL` or when `STRIPE_WEBHOOK_SECRET` expires:

1. Go to Stripe Dashboard → Developers → Webhooks
2. Delete the old endpoint
3. Add endpoint: `https://your-new-url/api/billing/webhook`
4. Select events: `customer.subscription.*`, `checkout.session.completed`, `invoice.payment_succeeded`, `invoice.payment_failed`
5. Copy the new `whsec_...` signing secret to `STRIPE_WEBHOOK_SECRET` in `.env`
6. Redeploy

---

## 5. Incident Response

### 5.1 Scanner stopped generating signals

```bash
# Check health endpoint
curl https://your-app/api/health | python3 -m json.tool

# Look for degraded background tasks in response
# Check logs for scanner errors
railway logs --tail 200 | grep -i "scanner\|error\|FAIL"

# Manually trigger a scan (owner only)
curl -X POST https://your-app/api/admin/scan/trigger \
  -H "Authorization: Bearer <owner-jwt>"
```

### 5.2 Emergency stop — halt all auto-executions

```bash
# RISK-4: Pause all signal delivery and broker auto-execution
curl -X POST https://your-app/api/admin/signals/pause \
  -H "Authorization: Bearer <owner-jwt>"

# Resume when resolved
curl -X POST https://your-app/api/admin/signals/resume \
  -H "Authorization: Bearer <owner-jwt>"
```

### 5.3 Broker orders not firing

```bash
# Check execution kill switch status
curl https://your-app/api/admin/signals/status \
  -H "Authorization: Bearer <owner-jwt>"

# Check portfolio drawdown for blocked users
# If DD > 5%, auto-execution is blocked automatically (RISK-2)
# User must close losing positions before execution resumes

# Check Alpaca API status
curl https://api.alpaca.markets/v2/account \
  -H "APCA-API-KEY-ID: <key>" -H "APCA-API-SECRET-KEY: <secret>"
```

### 5.4 High error rate / 5xx responses

```bash
# Check app health
curl https://your-app/api/health

# Review logs
railway logs --tail 500 | grep "ERROR\|CRITICAL\|500"

# Restart app (Railway)
railway restart

# Check if DB is reachable
python3 backend/scripts/check_postgres.py
```

### 5.5 Stripe billing not activating subscriptions

1. Check `STRIPE_WEBHOOK_SECRET` is set in production env
2. Check Stripe Dashboard → Webhooks → Recent deliveries for failures
3. Re-register webhook (Section 4 above)
4. Manually check event: `stripe events resend evt_xxx`

---

## 6. Routine Maintenance

### 6.1 Weekly tasks (mostly automated)

| Task | Schedule | How |
|---|---|---|
| Weekly digest | Sunday 08:00 ET | Auto — `_weekly_digest` background task |
| Factor mining | Sunday 10:00 ET | Auto — `_weekly_factor_mining` |
| ML retrain | Sunday 11:00 ET | Auto — `_weekly_ml_retrain` |
| Outcome resolution | Daily 02:00 ET | Auto — `_nightly_outcome_resolution` |
| Signal cleanup | Daily 04:15 ET | Auto — `_nightly_signal_cleanup` |
| CBOE options snapshot | Daily 18:30 ET | Auto — `_nightly_cboe_options_snapshot` |

### 6.2 Manual monthly tasks

```bash
# Check Brier score drift
cd backend && python scripts/gate_contribution_analysis.py --brier-drift

# Check live WR with CI bands
curl https://your-app/api/admin/live-wr-stats \
  -H "Authorization: Bearer <owner-jwt>"

# Check AUC drift
python -c "from services.signal_ml import compute_rolling_auc; print(compute_rolling_auc())"

# Run security audit
pip-audit -r backend/requirements.txt
npm audit --audit-level=high

# Gate contribution analysis (at N≥200 resolved signals)
cd backend && python scripts/gate_contribution_analysis.py --after 2026-06-01
```

### 6.3 Calibration recalibration (at N≥200 post-§82 (≥2026-05-29) resolved signals)

```bash
cd backend
python scripts/backfill_confidence.py --check           # readiness report
python scripts/backfill_confidence.py --force --apply   # recalibrate
```

### 6.4 Cross-sectional L/S sleeve validation and promotion

The cross-sectional market-neutral sleeve is validated offline and promoted through the §111 research gate.  The MR-vs-cross-sectional diversification test must pass before promotion: correlation < ~0.3 and blended Sharpe > both legs.

```bash
cd backend

# 1. Generate / refresh the h=63 monthly return series (one missing artifact)
../.venv311/bin/python scripts/cross_sectional_alpha_model.py \
  --horizon 63 --walk-forward --cost-bps 10 --save-monthly

# 2. Ensure the continuous MR equity series is current
#    (runs the full MR backtest; ~3 min with warm cache)
../.venv311/bin/python scripts/backtest_technicals.py
#    OR, if mr_trades.csv is already current:
../.venv311/bin/python scripts/generate_mr_equity_series.py

# 3. Run the sleeve-correlation / risk-blend gate
../.venv311/bin/python scripts/backtest_sleeves.py --corr

# 4. If the gate passes, promote the h=63 model to live
../.venv311/bin/python scripts/promote_cross_sectional_live.py
```

After promotion, `services.cross_sectional_shadow._SHADOW_SIZING_ACTIVE` is `True` and `services.alpha_sleeves.allocate_cross_sleeve_capital()` uses the validated MR + CrossSectional Sharpes/vols with risk-parity sizing.

---

## 7. Going Live with Real-Money Auto-Execution

This section is the operational checklist for transitioning from paper trading to live broker auto-execution.

### 7.1 Pre-live validation (do not skip)

| Check | Minimum bar | How to verify |
|---|---|---|
| Paper track record | ≥ 100 resolved signals or ≥ 3 months | `SELECT COUNT(*) FROM broker_orders WHERE account_type='paper' AND status='filled'` |
| Clean live WR | > 55% on delivered BUYs | `GET /api/admin/live-wr-stats` |
| Calibration | Brier ≤ 0.30, confidence gap ≤ 10pp | Backtest → Calibration tab |
| Drawdown simulation | Max DD < 10% at intended size | Simulated Returns panel |
| Kill switch | `pause` works in < 30 seconds | `POST /api/admin/signals/pause` |
| Broker API health | Status `ACTIVE`, equity > 0 | `GET /api/me/broker/status` |

### 7.2 Configure live risk limits

Set these on the user row **before** enabling live auto-execute:

```sql
UPDATE users
SET auto_execute = false,
    auto_execute_min_conf = 75.0,
    auto_execute_qty_dollars = 100.0,
    max_daily_orders = 3,
    max_ticker_notional = 500.0,
    alpaca_account_type = 'live'
WHERE id = <your_user_id>;
```

### 7.3 Connect live broker credentials

```bash
# 1. Acknowledge risk (records immutable timestamp)
curl -X POST https://your-app/api/me/risk-acknowledge \
  -H "Authorization: Bearer <access_token>"

# 2. Connect live Alpaca keys
curl -X POST https://your-app/api/me/broker/connect \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"broker":"alpaca","account_type":"live","api_key":"...","api_secret":"..."}'

# 3. Enable auto-execute
curl -X PATCH https://your-app/api/me/broker/settings \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"enabled":true,"min_conf":75.0,"qty_dollars":100.0}'
```

### 7.4 First live day protocol

- Start with **market open only**; avoid the 11:00–12:00 ET midday window (historically weak).
- Watch Telegram alerts for the first 3 signals.
- Verify each `BrokerOrder` row gets a broker `alpaca_order_id` and fills correctly.
- At market close, run reconciliation:
  ```bash
  cd backend && python scripts/reconcile_broker_orders.py
  ```

### 7.5 Daily live monitoring

| Task | Command / Location |
|---|---|
| Check overnight P&L | `/api/admin/live-wr-stats` |
| Review fills vs signal prices | `SELECT symbol, side, notional, arrival_price, filled_avg_price FROM broker_orders` |
| Verify drawdown circuit breaker | Logs for `RISK-2 portfolio DD` |
| Confirm no orphans | `SELECT * FROM broker_orders WHERE status='submitted' AND created_at < now() - interval '24 hours'` |

### 7.6 Sizing up

Only increase size after 30+ additional resolved live signals:

| Stage | `auto_execute_qty_dollars` | Max account % at risk |
|---|---|---|
| Validation | $100 | ≤ 5% |
| Confirmed edge | $500 | ≤ 10% |
| Full size | $1,000–$2,000 | ≤ 20% |

Never size up while live WR is below 50%.

---

## 8. Security Incident Response

### 8.1 JWT_SECRET leaked or suspected compromised

1. **Rotate immediately** — generate a new secret:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
2. Update `JWT_SECRET` in the production environment (Railway / Fly.io) and
   redeploy.
3. **Invalidate sessions** — because the secret signs access tokens, all
   existing JWTs become invalid on rotation. Users will be forced to
   re-authenticate via their refresh cookie; revoke all stored
   `RefreshToken` rows if you need a hard logout:
   ```bash
   psql $DATABASE_URL -c "DELETE FROM refresh_tokens;"
   ```
4. Audit `auth_audit_log` for unexpected IPs or user agents.
5. If the leak also exposed broker credentials (encrypted with a key derived
   from `JWT_SECRET`), notify affected users to re-enter broker API keys.

### 8.2 Stripe webhook secret suspected compromised

1. **Disable webhook processing** temporarily by unsetting
   `STRIPE_WEBHOOK_SECRET` (the endpoint returns `503` and Stripe retries).
2. In the Stripe Dashboard, delete the old webhook endpoint and create a new
   one.
3. Copy the new `whsec_...` signing secret into `STRIPE_WEBHOOK_SECRET`.
4. Redeploy and verify events resume successfully via the Stripe Dashboard.
5. Review `stripe_events` for any anomalous transitions or replayed events
   during the exposure window.

### 8.3 OAuth credentials leaked (Google)

1. Rotate the compromised client secret in the provider console:
   - Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 Client
2. Update `GOOGLE_CLIENT_SECRET` in production `.env`.
3. Verify that `OAuthState` rows do not contain plaintext long-lived secrets
   (PKCE verifiers are stored but are short-lived).
4. Redeploy and run a test Google login flow end-to-end.
5. Audit `auth_audit_log` for unexpected OAuth login accounts.

---

## 9. Contacts and Resources

| Resource | URL |
|---|---|
| Railway dashboard | https://railway.app/dashboard |
| Fly.io dashboard | https://fly.io/apps |
| Stripe dashboard | https://dashboard.stripe.com |
| Polygon.io dashboard | https://polygon.io/dashboard |
| Telegram @BotFather | https://t.me/BotFather |
| FRED API | https://fred.stlouisfed.org/docs/api/ |
| Alpaca API docs | https://docs.alpaca.markets/reference |
| Signal.Trade GitHub issues | https://github.com/<your-org>/TradingRecommendationSystem/issues |
