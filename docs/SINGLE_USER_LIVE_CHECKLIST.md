# Single-User Localhost — Go-To-Live-Capital Checklist

> For a single owner running the backend on a local Mac/Linux machine 24/7.
> Public-launch items (HTTPS, Stripe, Google OAuth, AdSense, Telegram webhooks, Cloudflare) are intentionally omitted because they are not required to trade your own account.
>
> **Rule:** do not enable live auto-execute until all **MUST** items below are checked.
> A small first capital is still real money; the empirical gates exist because the code can be "ready" while the signal is not.

---

## Phase 0 — Local Machine Hardening

- [ ] **1.1. Pin Python to `.venv311`.**
  ```bash
  cd backend
  ../.venv311/bin/python --version  # should be 3.11.x
  ```

- [ ] **1.2. Move secrets out of the repo.**
  - Broker API keys, `JWT_SECRET`, encryption keys, and OAuth tokens live in `backend/.env` **only**.
  - File permissions: `chmod 600 backend/.env`.
  - Do **not** commit `.env`; verify `git status` is clean of secrets.
  - Optional: load secrets from macOS Keychain or 1Password CLI instead of disk.

- [ ] **1.3. Start Redis locally.**
  ```bash
  docker run -d --name signal-redis -p 6379:6379 --restart unless-stopped redis:7-alpine
  ```
  Add to `backend/.env`:
  ```
  REDIS_URL=redis://localhost:6379
  ```

- [ ] **1.4. Set up automated DB backups.**
  - `backend/scripts/backup_db.sh` already exists and uses `sqlite3 .backup` for online-consistent copies.
  - LaunchAgent `com.signal.trade.backup` runs daily at 04:00 and keeps 7 days in `$HOME/Backups/signal-trade/`.
  - Test restore: copy a backup to `backend/data/trading.db.restore-test`, start app, verify data.

- [ ] **1.5. Run the backend with a process manager.**
  - Use a `launchd` user agent so the app restarts on crash and after reboot.
  - Plist: `~/Library/LaunchAgents/com.signal.trade.plist`
  - Use `.venv311/bin/python` (already configured).
  - Reload:
    ```bash
    MYUID=$(id -u)
    launchctl bootout gui/${MYUID}/com.signal.trade 2>/dev/null
    launchctl bootstrap gui/${MYUID} ~/Library/LaunchAgents/com.signal.trade.plist
    ```

- [ ] **1.5a. Keep the Mac awake and monitored.**
  - A user LaunchAgent runs `caffeinate -i` permanently: `~/Library/LaunchAgents/com.signal.trade.keepawake.plist`.
  - Watchdog `com.signal.trade.watchdog` polls `/api/health/uptime` and critical agents every 5 minutes and alerts via macOS notification.
  - Log rotation `com.signal.trade.rotate-logs` runs daily at 03:30 and keeps 14 days of compressed logs.
  - For full sleep disable (display + battery + lid), also run:
    ```bash
    sudo pmset -c sleep 0
    ```

- [ ] **1.6. Optional but recommended: wire Sentry.**
  - Add `SENTRY_DSN=...` to `backend/.env`.
  - Verify error reporting with `curl http://localhost:8000/api/health/sentry`.
  - For Sentry Uptime Monitoring, point the monitor at:
    ```
    https://<your-domain>/api/health/uptime
    ```
    This endpoint is public, requires no auth, and returns HTTP 200 only when the DB is reachable.

- [ ] **1.7. Use a named Cloudflare Tunnel for a stable public URL.**
  - Quick tunnels change domain on every restart. For 24/7 access and Sentry uptime checks, create a named tunnel with your own domain.
  - Authenticate once:
    ```bash
    cloudflared tunnel login
    ```
  - Then run the helper script (replace `app.yourdomain.com`):
    ```bash
    ./scripts/setup_cloudflare_tunnel.sh app.yourdomain.com
    ```
  - The script creates the tunnel, writes `~/.cloudflared/config.yml`, routes DNS, and installs a user LaunchAgent that survives reboots.

---

## Phase 1 — Broker & Account Setup

- [ ] **2.1. Fund and connect a live brokerage account.**
  - Alpaca or IBKR.
  - Add live keys to `backend/.env`.
  - Verify endpoint:
    ```bash
    curl -H "Authorization: Bearer $OWNER_TOKEN" \
      http://localhost:8000/api/me/broker/status
    # expected: {"connected": true, "account_type": "live"}
    ```

- [ ] **2.2. Keep a parallel paper account as control.**
  - Do not disable paper trading when you turn on live.
  - Paper signals continue to accrue for comparison.

- [ ] **2.3. Record your risk acknowledgement in the DB.**
  ```bash
  curl -X POST -H "Authorization: Bearer $OWNER_TOKEN" \
    http://localhost:8000/api/me/risk-acknowledge
  ```
  Verify `users.risk_acknowledged_at` is populated.

---

## Phase 2 — Risk Limits & Safety Switches

- [ ] **3.1. Set conservative initial limits (DB or admin endpoint).**
  | Setting | Recommended start value |
  |---------|--------------------------|
  | `max_daily_orders` | 3 |
  | `auto_execute_min_conf` | 75.0 |
  | `auto_execute_qty_dollars` | 100 |
  | `max_ticker_notional` | 500 |
  | `max_total_position_pct` | 10% of account |

- [ ] **3.2. Test the kill switch from your phone.**
  - Connect phone to same Wi-Fi.
  - Run:
    ```bash
    curl -X POST -H "Authorization: Bearer $OWNER_TOKEN" \
      https://<your-tunnel-domain>/api/admin/execution-kill-switch
    ```
  - Expected response: `{"execution_paused": true}`.
  - Confirm in logs that the scan loop pauses and no new signals are generated for 5 minutes.
  - Call the same endpoint again to resume; expected response: `{"execution_paused": false}`.

- [ ] **3.3. Verify global kill switch UI.**
  - In the web app, toggle the owner-only **KILL SWITCH** button in the top bar.
  - It should turn into **RESUME AUTO-EXEC** and call `POST /api/admin/execution-kill-switch`.
  - Verify over a Cloudflare Tunnel public URL as well as localhost.

- [ ] **3.4. Confirm drawdown circuit breaker is enabled.**
  - Check `backend/.env` / settings for drawdown threshold (e.g., 10% account-level pause).

---

## Phase 3 — Empirical Gates (cannot be rushed)

These require elapsed time and resolved signals. Do not proceed to Phase 4 until all are checked.

- [ ] **4.1. Paper track record — ≥100 resolved paper trades OR ≥3 months of continuous paper auto-execution.**
  - Run paper auto-execute 24/7.
  - Resolve outcomes via `scripts/resolve_outcomes.py` or automated EOD job.

- [ ] **4.2. Clean delivered BUY win rate >55% over ≥100 resolved signals.**
  - Check `/api/admin/live-wr-stats`.
  - Use **clean** BUYs only (exclude blocked sectors, SELLs, and stale/EOD-bypassed deliveries).
  - Current post-fix read: 57.8% net WR, +2.06%/trade, but sample size must reach ≥100.

- [ ] **4.3. Calibration check — Brier ≤0.30 and confidence gap ≤10pp.**
  - Run `python scripts/backfill_confidence.py --validate` once ≥50 post-A19 resolved signals exist.
  - If Brier is high, do **not** increase size until `CAL-1` is run.

- [ ] **4.4. Drawdown simulation <10% at intended live size.**
  - Use the backtest + intended position size and account equity.
  - Document max DD and worst 30-day P&L.

- [ ] **4.5. Decay monitor green for 30 consecutive days.**
  - Run `python scripts/decay_monitor.py` daily.
  - No `"decay"` alarm for 30 days straight.

---

## Phase 4 — First Live Capital Protocol

- [ ] **5.1. Enable live auto-execute only for the owner account.**
  - Ensure no other user accounts have live execution enabled.

- [ ] **5.2. Start with tiny size.**
  - `$100 per trade`, max `3 trades/day`, `75% min confidence`.
  - Do not raise size for at least 30 live trades or until the live WR remains >55%.

- [ ] **5.3. Bracket orders on.**
  - Verify Alpaca/IBKR dashboard shows bracket order legs (entry, stop, target).
  - Confirm stop is placed before target in the order object.

- [ ] **5.4. Review every fill same day.**
  - Check realized slippage vs `tca_service` estimate.
  - If realized slippage >20 bps repeatedly, size down or pause.

- [ ] **5.5. Weekly live-vs-paper reconciliation.**
  - Compare live fills to paper signals for the same ticker/date.
  - Flag any divergence >1% or missing fills.

---

## Phase 5 — Ongoing Monitoring

- [ ] **6.1. Daily:** check `/api/admin/system-readiness` and decay monitor.
- [ ] **6.2. Weekly:** review `ActionAuditLog`, delivery `skip_reason` distribution, and live WR.
- [ ] **6.3. Monthly:** verify DB backup restore works; rotate broker API keys if provider allows.
- [ ] **6.4. Sector blocks:** keep XLF/XLP/XLU/XLI blocked until a sector model is promoted via §117 QENG-1c.
- [ ] **6.5. XLV watch:** if live WR stays <45% at N≥100, add to watch-block.

---

## Sign-Off

Before toggling `auto_execute = true` on a live broker connection, confirm:

- [ ] Secrets secured, Redis running, DB backed up, app supervised.
- [ ] Live broker status returns `connected: true`.
- [ ] Risk limits set to conservative values.
- [ ] Kill switch tested from mobile.
- [ ] Risk acknowledgement recorded.
- [ ] Paper record ≥100 trades / 3 months.
- [ ] Clean live BUY WR >55% over ≥100 signals.
- [ ] Brier ≤0.30 and confidence gap ≤10pp.
- [ ] Drawdown simulation <10%.
- [ ] Decay monitor green for 30 days.

**If any item above is unchecked, keep auto-execute on paper only.**
