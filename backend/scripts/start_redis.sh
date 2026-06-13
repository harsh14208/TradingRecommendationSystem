#!/bin/bash
# Start (or create) the local Redis container for Signal.Trade.
# Called by the user LaunchAgent com.signal.trade.redis on login.
set -euo pipefail

CONTAINER_NAME="signal-trade-redis"
IMAGE="redis:7-alpine"

if ! docker info >/dev/null 2>&1; then
    echo "[start_redis] Docker daemon not available — skipping Redis start." >&2
    exit 0
fi

if docker ps -a --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
    if ! docker ps --format '{{.Names}}' | grep -qx "${CONTAINER_NAME}"; then
        echo "[start_redis] Starting existing ${CONTAINER_NAME} container..."
        docker start "${CONTAINER_NAME}" >/dev/null
    else
        echo "[start_redis] ${CONTAINER_NAME} already running."
    fi
else
    echo "[start_redis] Creating ${CONTAINER_NAME} container..."
    docker run -d \
        --name "${CONTAINER_NAME}" \
        --restart unless-stopped \
        -p 127.0.0.1:6379:6379 \
        "${IMAGE}"
fi
