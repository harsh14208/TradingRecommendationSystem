from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import AppSettings, User
from pydantic import BaseModel, field_validator
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
from urllib.parse import urlparse

router = APIRouter(prefix="/api/settings", tags=["settings"])

_DEFAULTS = {
    "theme": "dark",
    "accent": "#22d3ee",
    "density": "comfortable",
    "chartStyle": "area",
    "aggressiveness": "balanced",
    "style": "swing",
    "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
    "startTime": "09:30",
    "endTime": "16:00",
    "auto_paper_trade": False,
    "paper_trade_notional": 1000.0,
    # Separate options paper account: auto-simulate VRP option spreads (broker=
    # 'paper_options') under the owner account, distinct from the equity Alpaca
    # paper account above.
    "auto_paper_options": False,
}


@router.get("")
async def get_settings(db: AsyncSession = Depends(get_db), _user: User = Depends(get_current_user)):
    row = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
    return {**_DEFAULTS, **(row.data or {})} if row else _DEFAULTS


class AppSettingsUpdate(BaseModel):
    data: dict

    @field_validator("data")
    @classmethod
    def _reasonable_size(cls, v: dict) -> dict:
        if len(str(v)) > 50_000:
            raise ValueError("Settings payload too large")
        return v


@router.put("")
async def save_settings(
    body: AppSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not user.is_owner:
        raise HTTPException(status_code=403, detail="Owner access required.")
    data = body.data
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

    # Validate webhook URL before posting (SSRF guard)
    parsed = urlparse(db_user.webhook_url)
    if parsed.scheme not in ("https",) or not parsed.hostname:
        return {"ok": False, "error": "Webhook URL must be a valid https URL."}

    secret = (db_user.webhook_secret or "").encode()
    if not secret:
        return {"ok": False, "error": "No webhook secret configured."}

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
                allow_redirects=False,
            ) as resp:
                resp_text = await resp.text()
                return {
                    "ok": resp.status in (200, 201, 202, 204),
                    "status": resp.status,
                    "response": resp_text[:500],  # truncate to prevent excessive response size
                }
    except Exception as e:
        return {"ok": False, "error": str(e)}
