#!/bin/bash
# Local watchdog: alert if the Signal.Trade backend or LaunchAgents are unhealthy.
# Designed for a single-user Mac. Alerts via macOS notification and log file.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/../logs"
LOG_FILE="${LOG_DIR}/watchdog.log"
mkdir -p "$LOG_DIR"

ALERT=""

# Check backend health endpoint.
if ! curl -sf --max-time 5 http://localhost:8000/api/health/uptime >/dev/null 2>&1; then
    ALERT="Backend health check failed (http://localhost:8000/api/health/uptime)"
fi

# Check critical LaunchAgents.
for agent in com.signal.trade com.signal.trade.keepawake com.cloudflare.cloudflared.signal-trade; do
    if ! launchctl list | awk -v name="$agent" '$3 == name {found=1} END {exit !found}'; then
        ALERT="${ALERT}${ALERT:+, }LaunchAgent ${agent} not loaded"
    fi
done

if [[ -n "$ALERT" ]]; then
    MSG="Signal.Trade watchdog alert: ${ALERT}"
    echo "$(date -Iseconds) ${MSG}" >> "$LOG_FILE"
    # macOS notification (non-blocking, best-effort).
    if command -v osascript >/dev/null 2>&1; then
        osascript -e "display notification \"${MSG}\" with title \"Signal.Trade\"" 2>/dev/null || true
    fi
    exit 1
fi

echo "$(date -Iseconds) OK" >> "$LOG_FILE"
exit 0
