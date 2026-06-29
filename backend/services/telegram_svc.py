import aiohttp
from services.http_client import get_ssl_context, shared_session


def format_signal(signal: dict) -> str:
    emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal["action"], "⚪")
    conf = f"{signal['confidence']:.0f}%"
    # `.get(key, default)` only defaults on a MISSING key; VRP/defined-risk signals
    # carry rr=None (present), which would render "R:R None". Coerce None/empty to "—".
    rr = signal.get("rr")
    rr = rr if rr not in (None, "", "None") else "—"
    company = signal.get("company", "")
    name_part = f" ({company})" if company and company != signal["ticker"] else ""
    lines = [
        f"{emoji} *{signal['action']} {signal['ticker']}*{name_part} · ${signal['price']:.2f} · {conf} conf · R:R {rr}",
        f"_{signal['headline']}_",
    ]
    if signal.get("entry") and signal.get("stop") and signal.get("target"):
        lines.append(f"Entry ${signal['entry']:.2f}  Stop ${signal['stop']:.2f}  TP ${signal['target']:.2f}")
    lines.append("_Not financial advice · Signal.Trade_")
    return "\n".join(lines)


async def send_telegram_message(
    chat_id: str,
    text: str,
    parse_mode: str = "Markdown",
    timeout: int = 8,
) -> tuple[bool, str]:
    """Single shared Telegram send function used by all call sites."""

    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not chat_id:
        return False, "Not configured"
    url = f"https://api.telegram.org/bot{s.telegram_bot_token.get_secret_value()}/sendMessage"
    ctx = get_ssl_context()
    try:
        async with shared_session() as session:
            resp = await session.post(
                url,
                json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
                ssl=ctx,
                timeout=aiohttp.ClientTimeout(total=timeout),
            )
            data = await resp.json()
            if data.get("ok"):
                return True, str(data.get("result", {}).get("message_id", ""))
            return False, data.get("description", "Unknown Telegram error")
    except Exception as e:
        return False, str(e)


async def send_telegram(signal: dict) -> tuple[bool, str]:
    from config import get_settings

    s = get_settings()
    if not s.telegram_bot_token or not s.telegram_chat_id:
        return False, "Telegram not configured — set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env"
    return await send_telegram_message(s.telegram_chat_id, format_signal(signal))
