#!/bin/bash
# Rotate backend logs. Keeps 14 days of compressed history.
# Run daily via launchd.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${SCRIPT_DIR}/../logs"
RETAIN_DAYS=14

mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

for logfile in "$LOG_DIR"/*.log; do
    # Skip if no logs exist.
    [[ -e "$logfile" ]] || continue

    # Only rotate non-empty files.
    [[ -s "$logfile" ]] || continue

    base=$(basename "$logfile" .log)
    mv "$logfile" "${LOG_DIR}/${base}-${TIMESTAMP}.log"
    touch "$logfile"
done

# Compress any uncompressed rotated logs older than 1 day.
find "$LOG_DIR" -maxdepth 1 -name '*.log' ! -name '*-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_[0-9][0-9][0-9][0-9][0-9][0-9].log' -type f -mtime +1 -exec gzip {} \; 2>/dev/null || true

# Delete compressed logs older than retention window.
find "$LOG_DIR" -maxdepth 1 -name '*.gz' -type f -mtime +"$RETAIN_DAYS" -delete

echo "Log rotation complete: $LOG_DIR"
ls -la "$LOG_DIR"
