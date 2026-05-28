from database import get_db
from fastapi import APIRouter, Depends
from models import AppSettings, User
from services.auth_svc import get_current_user
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
