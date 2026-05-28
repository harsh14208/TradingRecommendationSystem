import re

from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import PriceAlert, User
from pydantic import BaseModel, field_validator
from services.auth_svc import get_current_user
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

_TICKER_RE = re.compile(r"^[A-Z]{1,5}$")
_VALID_CONDITIONS = {"above", "below"}


class AlertCreate(BaseModel):
    ticker: str
    target_price: float
    condition: str = "above"

    @field_validator("ticker")
    @classmethod
    def ticker_format(cls, v: str) -> str:
        v = v.strip().upper()
        if not _TICKER_RE.match(v):
            raise ValueError("Ticker must be 1–5 uppercase letters")
        return v

    @field_validator("target_price")
    @classmethod
    def price_positive(cls, v: float) -> float:
        if v <= 0 or v >= 1_000_000:
            raise ValueError("Price must be between 0 and 1,000,000")
        return round(v, 2)

    @field_validator("condition")
    @classmethod
    def condition_valid(cls, v: str) -> str:
        if v not in _VALID_CONDITIONS:
            raise ValueError(f"condition must be one of {_VALID_CONDITIONS}")
        return v


@router.get("/")
async def get_alerts(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PriceAlert).where(PriceAlert.user_id == user.id, PriceAlert.is_active == True))
    alerts = result.scalars().all()
    return {
        "alerts": [
            {"id": a.id, "ticker": a.ticker, "target_price": a.target_price, "condition": a.condition} for a in alerts
        ]
    }


@router.post("/")
async def create_alert(body: AlertCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    alert = PriceAlert(
        user_id=user.id,
        ticker=body.ticker,
        target_price=body.target_price,
        condition=body.condition,
    )
    db.add(alert)
    await db.commit()
    return {"ok": True, "message": "Alert created successfully", "alert_id": alert.id}


@router.delete("/{alert_id}")
async def delete_alert(alert_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Delete a price alert."""
    alert = await db.get(PriceAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    await db.delete(alert)
    await db.commit()
    return {"ok": True}
