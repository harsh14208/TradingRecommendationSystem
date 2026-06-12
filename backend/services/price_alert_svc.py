import inspect
import logging

from fastapi import HTTPException
from models import PriceAlert
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger("signal.trade.alerts")


async def create_price_alert(
    db: AsyncSession, user_id: int, ticker: str, target_price: float, condition: str
) -> PriceAlert:
    alert = PriceAlert(
        user_id=user_id,
        ticker=ticker,
        target_price=target_price,
        condition=condition,
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


async def delete_price_alert(db: AsyncSession, alert_id: int, user_id: int) -> None:
    alert = await db.get(PriceAlert, alert_id)
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
