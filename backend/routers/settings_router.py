from database import get_db
from fastapi import APIRouter, Depends
from models import AppSettings, User
from services.auth_svc import get_current_user
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import secrets
import time
import hmac
import hashlib
import json
import ssl
import certifi
import aiohttp
from config import get_settings as get_app_settings

router = APIRouter(prefix="/api/settings", tags=["settings"])

_DEFAULTS = {
    "theme": "dark",
    "accent": "#10b981",
    "density": "comfortable",
    "chartStyle": "area",
    "aggressiveness": "balanced",
    "style": "swing",
    "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
    "startTime": "09:30",
    "endTime": "16:00",
    "auto_paper_trade": False,
    "paper_trade_notional": 1000.0,
}


@router.get("")
async def get_settings(db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    row = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
    return {**_DEFAULTS, **(row.data or {})} if row else _DEFAULTS


@router.put("")
async def save_settings(data: dict, db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    row = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
    if row is None:
        db.add(AppSettings(id=1, data=data))
    else:
        row.data = data
    await db.commit()
    return data


@router.get("/webhooks/secret")
async def get_webhook_secret(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """TSYS-3d: Get current webhook secret (generate one if it doesn't exist yet)."""
    db_user = await db.get(User, user.id)
    if not db_user.webhook_secret:
        db_user.webhook_secret = secrets.token_hex(32)
        await db.commit()
    return {"webhook_secret": db_user.webhook_secret}


@router.post("/webhooks/rotate-secret")
async def rotate_webhook_secret(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """TSYS-3d: Rotate the outbound webhook signing secret."""
    db_user = await db.get(User, user.id)
    db_user.webhook_secret = secrets.token_hex(32)
    await db.commit()
    return {"webhook_secret": db_user.webhook_secret}


@router.post("/webhooks/test")
async def test_webhook(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    """TSYS-3d: Send a signed test event to user's webhook_url to verify integration."""
    db_user = await db.get(User, user.id)
    if not db_user.webhook_url:
        return {"ok": False, "error": "No webhook URL configured."}

    # Retrieve secret (or default to app settings secret if none configured yet)
    secret = (db_user.webhook_secret or get_app_settings().jwt_secret or "").encode()

    test_payload = {
        "event": "test",
        "message": "This is a signed test event from Trading Recommendation System.",
        "timestamp": int(time.time()),
        "user_id": db_user.id,
    }

    payload_bytes = json.dumps(test_payload).encode()
    sig_hdr = "sha256=" + hmac.new(secret, payload_bytes, hashlib.sha256).hexdigest()

    try:
        ssl_ctx = ssl.create_default_context(cafile=certifi.where())
        async with aiohttp.ClientSession() as sess:
            async with sess.post(
                db_user.webhook_url,
                data=payload_bytes,
                headers={"Content-Type": "application/json", "X-Signal-Trade-Signature": sig_hdr},
                ssl=ssl_ctx,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                resp_text = await resp.text()
                return {
                    "ok": resp.status in (200, 201, 202, 204),
                    "status": resp.status,
                    "response": resp_text[:500],  # truncate to prevent excessive response size
                }
    except Exception as e:
        return {"ok": False, "error": str(e)}
