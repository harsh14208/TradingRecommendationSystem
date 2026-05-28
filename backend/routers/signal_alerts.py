"""
Per-ticker signal confidence alert rules.

Endpoints:
  GET    /api/alerts/signals          — list user's rules
  POST   /api/alerts/signals          — create rule
  PATCH  /api/alerts/signals/{id}     — update rule
  DELETE /api/alerts/signals/{id}     — delete rule
"""

import re
from typing import Optional

from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from models import SignalAlert, User
from pydantic import BaseModel, field_validator
from services.auth_svc import get_current_user
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/alerts/signals", tags=["signal-alerts"])

_TICKER_RE = re.compile(r"^[A-Z]{1,5}$")
_VALID_ACTIONS = {"BUY", "SELL", "any"}


class SignalAlertCreate(BaseModel):
    ticker: str
    min_confidence: float
    action_filter: str = "any"

    @field_validator("ticker")
    @classmethod
    def ticker_format(cls, v: str) -> str:
        v = v.strip().upper()
        if not _TICKER_RE.match(v):
            raise ValueError("Ticker must be 1–5 uppercase letters")
        return v

    @field_validator("min_confidence")
    @classmethod
    def conf_range(cls, v: float) -> float:
        if not (0 <= v <= 100):
            raise ValueError("min_confidence must be between 0 and 100")
        return round(v, 1)

    @field_validator("action_filter")
    @classmethod
    def action_valid(cls, v: str) -> str:
        v = v.strip()
        if v not in _VALID_ACTIONS:
            raise ValueError(f"action_filter must be one of {_VALID_ACTIONS}")
        return v


class SignalAlertUpdate(BaseModel):
    min_confidence: Optional[float] = None
    action_filter: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("min_confidence")
    @classmethod
    def conf_range(cls, v):
        if v is not None and not (0 <= v <= 100):
            raise ValueError("min_confidence must be between 0 and 100")
        return round(v, 1) if v is not None else v

    @field_validator("action_filter")
    @classmethod
    def action_valid(cls, v):
        if v is not None and v not in _VALID_ACTIONS:
            raise ValueError(f"action_filter must be one of {_VALID_ACTIONS}")
        return v


def _fmt(a: SignalAlert) -> dict:
    return {
        "id": a.id,
        "ticker": a.ticker,
        "min_confidence": a.min_confidence,
        "action_filter": a.action_filter,
        "is_active": a.is_active,
    }


@router.get("/")
async def list_signal_alerts(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = (await db.execute(select(SignalAlert).where(SignalAlert.user_id == user.id))).scalars().all()
    return {"alerts": [_fmt(a) for a in rows]}


@router.post("/")
async def create_signal_alert(
    body: SignalAlertCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = (
        await db.execute(
            select(SignalAlert).where(
                SignalAlert.user_id == user.id,
                SignalAlert.ticker == body.ticker,
                SignalAlert.is_active == True,
            )
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=409, detail=f"Active rule for {body.ticker} already exists — update or delete it first"
        )

    alert = SignalAlert(
        user_id=user.id,
        ticker=body.ticker,
        min_confidence=body.min_confidence,
        action_filter=body.action_filter,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return {"ok": True, "alert": _fmt(alert)}


@router.patch("/{alert_id}")
async def update_signal_alert(
    alert_id: int,
    body: SignalAlertUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    alert = await db.get(SignalAlert, alert_id)
    if not alert or alert.user_id != user.id:
        raise HTTPException(status_code=404, detail="Alert not found")
    if body.min_confidence is not None:
        alert.min_confidence = body.min_confidence
    if body.action_filter is not None:
        alert.action_filter = body.action_filter
    if body.is_active is not None:
        alert.is_active = body.is_active
    await db.commit()
    return {"ok": True, "alert": _fmt(alert)}


@router.delete("/{alert_id}")
async def delete_signal_alert(
    alert_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    alert = await db.get(SignalAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    await db.delete(alert)
    await db.commit()
    return {"ok": True}
