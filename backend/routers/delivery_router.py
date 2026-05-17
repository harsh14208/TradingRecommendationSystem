from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import SendLog

router = APIRouter(prefix="/api/delivery", tags=["delivery"])


@router.get("/log")
async def get_delivery_log(db: AsyncSession = Depends(get_db)):
    """Delivery log — last 50 signal send events (sent / fail / queue)."""
    rows = (await db.execute(
        select(SendLog).order_by(desc(SendLog.created_at)).limit(50)
    )).scalars().all()
    return [
        {
            "time":       r.time,
            "status":     r.status,
            "message":    r.message,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
