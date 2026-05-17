import aiohttp


def format_signal(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf  = f"{signal['confidence']:.0f}%"
    rr    = signal.get("rr", "—")
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}* · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(
            f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}"
        )
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


async def send_telegram(signal: dict) -> tuple[bool, str]:
    from config import get_settings
    s = get_settings()
    if not s.telegram_bot_token or not s.telegram_chat_id:
        return False, "Telegram not configured — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"

    url = f"https://api.telegram.org/bot{s.telegram_bot_token}/sendMessage"
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.post(url, json={
                "chat_id": s.telegram_chat_id,
                "text": format_signal(signal),
                "parse_mode": "Markdown",
            })
            data = await resp.json()
            if data.get("ok"):
                return True, str(data["result"]["message_id"])
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)
