"""
Telegram bot webhook — handles /start <code> to link a chat_id to a user account.

Setup:
  1. Set the webhook URL in Telegram:
     curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=<APP_URL>/api/telegram/webhook"
  2. Users run /start <link_code> in their Telegram chat with the bot.
  3. The bot links their chat_id to their Signal.Trade account.
"""

import logging
import secrets as _secrets

import aiohttp
from config import get_settings
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Request
from models import User
from services.auth_svc import get_current_user
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger("signal.trade.tg_webhook")
router = APIRouter(prefix="/api/telegram", tags=["telegram"])


async def _reply(chat_id: str, text: str):
    s = get_settings()
    if not s.telegram_bot_token:
        return
    url = f"https://api.telegram.org/bot{s.telegram_bot_token}/sendMessage"
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
    except Exception as e:
        log.warning(f"[tg_webhook] reply failed: {e}")


@router.post("/webhook", include_in_schema=False)
async def telegram_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    # Validate Telegram webhook secret token if configured.
    # Set via setWebhook?secret_token=... — Telegram sends it in X-Telegram-Bot-Api-Secret-Token.
    s = get_settings()
    if s.telegram_bot_token:
        expected_secret = request.app.state.__dict__.get("_tg_webhook_secret")
        incoming_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if expected_secret and not _secrets.compare_digest(incoming_secret, expected_secret):
            # Return 200 to avoid Telegram retrying; silently drop forged requests
            return {"ok": True}

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "Invalid JSON")

    message = body.get("message") or body.get("edited_message")
    if not message:
        return {"ok": True}

    chat_id = str(message.get("chat", {}).get("id", ""))
    text = (message.get("text") or "").strip()
    username = message.get("from", {}).get("username", "there")

    if not text.startswith("/start"):
        await _reply(chat_id, "Send `/start <link-code>` to connect your Signal.Trade account.")
        return {"ok": True}

    parts = text.split()
    if len(parts) < 2:
        await _reply(
            chat_id,
            "👋 Welcome to Signal.Trade!\n\n"
            "To connect your account, go to *Account Settings* in the app and copy your Telegram link code. "
            "Then send:\n`/start YOUR_CODE`",
        )
        return {"ok": True}

    code = parts[1].strip().upper()

    user = (await db.execute(select(User).where(User.telegram_link_code == code))).scalar_one_or_none()

    if not user:
        await _reply(
            chat_id, "❌ Invalid or expired link code.\n\nGo to *Account Settings* in Signal.Trade to get a fresh code."
        )
        return {"ok": True}

    # Check if this chat is already linked to another account
    existing = (await db.execute(select(User).where(User.telegram_chat_id == chat_id))).scalar_one_or_none()
    if existing and existing.id != user.id:
        await _reply(
            chat_id,
            "⚠️ This Telegram account is already linked to a different Signal.Trade account. "
            "Unlink it first from Account Settings.",
        )
        return {"ok": True}

    # Link the chat
    user.telegram_chat_id = chat_id
    user.telegram_link_code = None  # one-time use — clear it
    await db.commit()

    tier_msg = {
        "free": "You're on the *Free* plan — upgrade to Basic or Pro to receive signal alerts.",
        "basic": "You're on *Basic* — you'll now receive signal alerts here.",
        "pro": "You're on *Pro* — you'll now receive all signal alerts and weekly digests here.",
    }.get(user.subscription_tier, "")

    await _reply(
        chat_id,
        f"✅ *Telegram linked to Signal.Trade!*\n\n"
        f"Account: `{user.email}`\n{tier_msg}\n\n"
        "⚠️ _Signals are for informational purposes only. Not financial advice._",
    )

    log.info(f"[tg_webhook] linked chat_id={chat_id} user={user.id} email={user.email}")
    return {"ok": True}


@router.post("/set-webhook")
async def set_webhook(owner: User = Depends(get_current_user)):
    """Register the bot webhook URL with Telegram. Call once after deployment. Owner-only."""
    if not owner.is_owner:
        raise HTTPException(403, "Owner access required.")
    s = get_settings()
    if not s.telegram_bot_token:
        raise HTTPException(503, "TELEGRAM_BOT_TOKEN not set.")
    webhook_url = f"{s.app_url}/api/telegram/webhook"
    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            f"https://api.telegram.org/bot{s.telegram_bot_token}/setWebhook",
            json={"url": webhook_url, "allowed_updates": ["message"]},
        )
        data = await resp.json()
    return {"webhook_url": webhook_url, "telegram_response": data}
