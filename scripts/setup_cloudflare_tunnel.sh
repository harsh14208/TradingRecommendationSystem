#!/bin/bash
# Create a named Cloudflare Tunnel for Signal.Trade with a fixed domain.
# Run this AFTER authenticating cloudflared: cloudflared tunnel login

set -euo pipefail

DOMAIN="${1:-}"
TUNNEL_NAME="${2:-signal-trade}"

if [[ -z "$DOMAIN" ]]; then
  echo "Usage: $0 <hostname> [tunnel-name]"
  echo "Example: $0 app.signal.trade"
  exit 1
fi

CONFIG_DIR="$HOME/.cloudflared"
mkdir -p "$CONFIG_DIR"

echo "[1/5] Creating tunnel: $TUNNEL_NAME"
cloudflared tunnel create "$TUNNEL_NAME" | tee /tmp/tunnel-create.log

TUNNEL_ID=$(grep -oE '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' /tmp/tunnel-create.log | head -1)
if [[ -z "$TUNNEL_ID" ]]; then
  echo "ERROR: Could not extract tunnel ID. Check /tmp/tunnel-create.log"
  exit 1
fi
CREDS_FILE="$CONFIG_DIR/$TUNNEL_ID.json"

echo "[2/5] Writing config to $CONFIG_DIR/config.yml"
cat > "$CONFIG_DIR/config.yml" <<EOF
tunnel: $TUNNEL_ID
credentials-file: $CREDS_FILE

ingress:
  - hostname: $DOMAIN
    service: http://localhost:8000
    originRequest:
      noTLSVerify: false
  - service: http_status:404
EOF

echo "[3/5] Routing DNS: $DOMAIN -> tunnel $TUNNEL_ID"
cloudflared tunnel route dns "$TUNNEL_NAME" "$DOMAIN"

echo "[4/5] Installing user LaunchAgent"
PLIST="$HOME/Library/LaunchAgents/com.cloudflare.cloudflared.signal-trade.plist"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cloudflare.cloudflared.signal-trade</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/cloudflared</string>
        <string>tunnel</string>
        <string>run</string>
        <string>$TUNNEL_ID</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/harshv.singh/TradingRecommendationSystem/backend/logs/cloudflared.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/harshv.singh/TradingRecommendationSystem/backend/logs/cloudflared.log</string>
</dict>
</plist>
EOF

MYUID=$(id -u)
launchctl bootstrap "gui/$MYUID" "$PLIST"

echo "[5/5] Done. Tunnel should be reachable at https://$DOMAIN"
echo "You can point Sentry Uptime Monitoring at: https://$DOMAIN/api/health/uptime"
echo ""
echo "To stop:  launchctl bootout gui/$MYUID/com.cloudflare.cloudflared.signal-trade"
echo "Logs:     tail -f /Users/harshv.singh/TradingRecommendationSystem/backend/logs/cloudflared.log"
