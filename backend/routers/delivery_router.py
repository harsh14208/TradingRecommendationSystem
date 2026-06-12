from database import get_db
from fastapi import APIRouter, Depends
from models import SendLog, User
from services.auth_svc import get_current_user
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/delivery", tags=["delivery"])


@router.get("/log")
async def get_delivery_log(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delivery log — last 50 signal send events for the authenticated user.
    Owner users can see the global log.
    """
    stmt = select(SendLog).order_by(desc(SendLog.created_at))
    if not user.is_owner:
        stmt = stmt.where(SendLog.user_id == user.id)
    rows = (await db.execute(stmt.limit(50))).scalars().all()
    return [
        {
            "time": r.time,
            "status": r.status,
            "message": r.message,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
