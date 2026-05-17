import logging
import aiohttp
from config import get_settings

log = logging.getLogger("signal.trade.discord")

async def send_discord_signal(discord_webhook_url: str, signal_data: dict):
    """
    Delivers a signal to a Discord channel via webhook.
    Format mimics the Telegram delivery for consistency.
    """
    if not discord_webhook_url:
        return False
        
    action = signal_data.get("action", "HOLD")
    color = 0x10B981 if action == "BUY" else 0xEF4444 if action == "SELL" else 0xF59E0B
    
    embed = {
        "title": f"{action} {signal_data.get('ticker')}",
        "description": signal_data.get("headline", ""),
        "color": color,
        "fields": [
            {"name": "Confidence", "value": f"{signal_data.get('confidence')}%", "inline": True},
            {"name": "Price", "value": f"${signal_data.get('price')}", "inline": True},
            {"name": "R:R", "value": str(signal_data.get("rr", "—")), "inline": True},
            {"name": "Entry", "value": f"${signal_data.get('entry')}", "inline": True},
            {"name": "Stop", "value": f"${signal_data.get('stop')}", "inline": True},
            {"name": "Target", "value": f"${signal_data.get('target')}", "inline": True},
            {"name": "Analysis", "value": signal_data.get("plain_english", {}).get("summary", ""), "inline": False}
        ],
        "footer": {"text": "NOT FINANCIAL ADVICE. Trade at your own risk."}
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                discord_webhook_url,
                json={"embeds": [embed]},
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status in (200, 204):
                    return True
                else:
                    log.error(f"Discord delivery failed: {response.status}")
                    return False
    except Exception as e:
        log.error(f"Discord delivery error: {e}")
        return False