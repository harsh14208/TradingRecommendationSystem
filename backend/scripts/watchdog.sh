#!/bin/bash
# Local watchdog: detect AND self-heal Signal.Trade LaunchAgent / backend issues.
# Designed for a single-user Mac. Auto-reloads any critical LaunchAgent that has
# been UNLOADED (bootout / logout / system event — the state KeepAlive cannot
# recover from), then alerts via macOS notification + log file if anything still
# looks wrong after remediation.
#
# Scope note: a loaded-but-unhealthy backend is alerted, NOT auto-restarted — we
# never kill a process that is loaded and may simply be busy/mid-startup. Only a
# genuinely-gone (unloaded) agent is re-bootstrapped.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/../logs"
LOG_FILE="${LOG_DIR}/watchdog.log"
LA_DIR="${HOME}/Library/LaunchAgents"
GUI_DOMAIN="gui/$(id -u)"
mkdir -p "$LOG_DIR"

ALERT=""
ACTIONS=""
reloaded_backend=0

agent_loaded() {
    launchctl list | awk -v name="$1" '$3 == name {found=1} END {exit !found}'
}

backend_healthy() {
    curl -sf --max-time 5 http://localhost:8000/api/health/uptime >/dev/null 2>&1
}

# 1. Re-load any critical LaunchAgent that has been unloaded.
for agent in com.signal.trade com.signal.trade.keepawake com.cloudflare.cloudflared.signal-trade; do
    if ! agent_loaded "$agent"; then
        plist="${LA_DIR}/${agent}.plist"
        if [[ -f "$plist" ]] && launchctl bootstrap "$GUI_DOMAIN" "$plist" 2>/dev/null && agent_loaded "$agent"; then
            ACTIONS="${ACTIONS}${ACTIONS:+, }re-loaded ${agent}"
            [[ "$agent" == "com.signal.trade" ]] && reloaded_backend=1
        else
            ALERT="${ALERT}${ALERT:+, }LaunchAgent ${agent} not loaded (auto-reload failed)"
        fi
    fi
done

# 2. If we just re-loaded the backend, give it up to 60s to finish startup
#    before judging health, so a normal warm-up isn't reported as a failure.
if [[ "$reloaded_backend" -eq 1 ]]; then
    for _ in $(seq 1 12); do
        backend_healthy && break
        sleep 5
    done
fi

# 3. Backend health check (alert-only — never auto-kills a loaded process).
if ! backend_healthy; then
    ALERT="${ALERT}${ALERT:+, }Backend health check failed (http://localhost:8000/api/health/uptime)"
fi

# 4. Report.
if [[ -n "$ALERT" ]]; then
    MSG="Signal.Trade watchdog alert: ${ALERT}"
    [[ -n "$ACTIONS" ]] && MSG="${MSG} [auto-remediation: ${ACTIONS}]"
    echo "$(date -Iseconds) ${MSG}" >> "$LOG_FILE"
    # macOS notification (non-blocking, best-effort).
    if command -v osascript >/dev/null 2>&1; then
        osascript -e "display notification \"${MSG}\" with title \"Signal.Trade\"" 2>/dev/null || true
    fi
    exit 1
fi

if [[ -n "$ACTIONS" ]]; then
    echo "$(date -Iseconds) OK (self-healed: ${ACTIONS})" >> "$LOG_FILE"
else
    echo "$(date -Iseconds) OK" >> "$LOG_FILE"
fi
exit 0
