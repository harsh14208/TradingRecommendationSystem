import inspect
import logging

from fastapi import HTTPException
from models import SignalAlert
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger("signal.trade.alerts")


async def create_signal_alert(
    db: AsyncSession,
    user_id: int,
    ticker: str,
    min_confidence: float,
    action_filter: str,
) -> SignalAlert:
    existing = (
        await db.execute(
            select(SignalAlert).where(
                SignalAlert.user_id == user_id,
                SignalAlert.ticker == ticker,
                SignalAlert.is_active == True,
            )
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=409, detail=f"Active rule for {ticker} already exists — update or delete it first"
        )

    alert = SignalAlert(
        user_id=user_id,
        ticker=ticker,
        min_confidence=min_confidence,
        action_filter=action_filter,
    )
    db.add(alert)
    try:
        await db.commit()
        if inspect.iscoroutinefunction(getattr(db, "refresh", None)):
            await db.refresh(alert)
    except Exception:
        if inspect.iscoroutinefunction(getattr(db, "rollback", None)):
            await db.rollback()
        raise
    return alert


async def update_signal_alert(
    db: AsyncSession,
    alert_id: int,
    user_id: int,
    min_confidence: float | None,
    action_filter: str | None,
    is_active: bool | None,
) -> SignalAlert:
    alert = await db.get(SignalAlert, alert_id)
    if not alert or alert.user_id != user_id:
        raise HTTPException(status_code=404, detail="Alert not found")
    if min_confidence is not None:
        alert.min_confidence = min_confidence
    if action_filter is not None:
        alert.action_filter = action_filter
    if is_active is not None:
        alert.is_active = is_active
    try:
        await db.commit()
        if inspect.iscoroutinefunction(getattr(db, "refresh", None)):
            await db.refresh(alert)
    except Exception:
        if inspect.iscoroutinefunction(getattr(db, "rollback", None)):
            await db.rollback()
        raise
    return alert


async def delete_signal_alert(db: AsyncSession, alert_id: int, user_id: int) -> None:
    alert = await db.get(SignalAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    await db.delete(alert)
    try:
        await db.commit()
    except Exception:
        if inspect.iscoroutinefunction(getattr(db, "rollback", None)):
            await db.rollback()
        raise
