from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import User
from pydantic import BaseModel, field_validator
from services.auth_svc import get_current_user
from services.push_svc import save_push_subscription
from sqlalchemy.ext.asyncio import AsyncSession
from urllib.parse import urlparse

router = APIRouter(prefix="/api/push", tags=["push"])


class PushSubscriptionIn(BaseModel):
    endpoint: str | None = None
    keys: dict

    @field_validator("endpoint")
    @classmethod
    def _https_endpoint(cls, v: str) -> str:
        parsed = urlparse(v)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("Push endpoint must be a valid https URL")
        return v


@router.post("/subscribe")
async def subscribe_web_push(
    payload: PushSubscriptionIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    endpoint = payload.endpoint
    keys = payload.keys
    if not endpoint:
        raise HTTPException(400, "Invalid push subscription payload: missing endpoint")
    p256dh = keys.get("p256dh")
    auth = keys.get("auth")

    if not p256dh or not auth:
        raise HTTPException(400, "Invalid push subscription payload: missing keys")

    try:
        inserted = await save_push_subscription(db, user.id, endpoint, p256dh, auth)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    return {"ok": True, "message": "Subscribed to push notifications", "new": inserted}
