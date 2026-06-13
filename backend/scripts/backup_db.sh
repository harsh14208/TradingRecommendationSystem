#!/bin/bash
# Backup the local SQLite trading database.
# Intended for a single-user localhost deployment.
# Add to cron or launchd to run daily.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="${SCRIPT_DIR}/../data/trading.db"
BACKUP_ROOT="${SIGNAL_TRADE_BACKUP_DIR:-$HOME/Backups/signal-trade}"
RETAIN_DAYS="${SIGNAL_TRADE_BACKUP_RETAIN_DAYS:-7}"

if [[ ! -f "$SRC" ]]; then
    echo "ERROR: source database not found: $SRC" >&2
    exit 1
fi

mkdir -p "$BACKUP_ROOT"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DST="${BACKUP_ROOT}/${TIMESTAMP}_trading.db"

cp "$SRC" "$DST"

# Remove backups older than retention window.
find "$BACKUP_ROOT" -name '*_trading.db' -type f -mtime +"$RETAIN_DAYS" -delete

echo "Backed up $SRC -> $DST"
echo "Current backups:"
ls -la "$BACKUP_ROOT"
