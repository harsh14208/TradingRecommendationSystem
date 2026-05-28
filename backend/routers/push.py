from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import PushSubscription, User
from services.auth_svc import get_current_user
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/push", tags=["push"])


@router.post("/subscribe")
async def subscribe_web_push(payload: dict, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    endpoint = payload.get("endpoint")
    keys = payload.get("keys", {})
    p256dh = keys.get("p256dh")
    auth = keys.get("auth")

    if not endpoint or not p256dh or not auth:
        raise HTTPException(400, "Invalid push subscription payload")

    # Check if exists
    existing = (
        await db.execute(select(PushSubscription).where(PushSubscription.endpoint == endpoint))
    ).scalar_one_or_none()
    if not existing:
        sub = PushSubscription(user_id=user.id, endpoint=endpoint, p256dh=p256dh, auth=auth)
        db.add(sub)
        await db.commit()

    return {"ok": True, "message": "Subscribed to push notifications"}
