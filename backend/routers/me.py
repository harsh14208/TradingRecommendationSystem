"""
Per-user account endpoints — /api/me/*

Provides personal signal delivery history and performance stats
based on the current user's SignalDelivery records.
"""

import math
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import AppSettings, Signal, SignalDelivery, User
from pydantic import BaseModel
from services.auth_svc import get_current_user

router = APIRouter(prefix="/api/me", tags=["me"])


def _sig_row(s: Signal, sent_at) -> dict:
    return {
        "id": s.id,
        "ticker": s.ticker,
        "company": s.company or s.ticker,
        "action": s.action,
        "confidence": s.confidence,
        "price": s.price,
        "style": s.style,
        "sent_at": sent_at.isoformat() if sent_at else None,
        "created_at": s.created_at.isoformat() if s.created_at else None,
        "outcome_pct": round(s.outcome_pct, 2) if s.outcome_pct is not None else None,
        "outcome_14d": round(s.outcome_14d, 2) if s.outcome_14d is not None else None,
        "hit_target": s.hit_target,
        "hit_stop": s.hit_stop,
        "exit_type": s.exit_type,
        "mae": round(s.mae, 2) if s.mae is not None else None,
        "mfe": round(s.mfe, 2) if s.mfe is not None else None,
    }


@router.get("/performance")
async def my_performance(
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Return the current user's personal signal delivery history and performance stats.

    Stats are computed from signals actually delivered to this user
    (via signal_deliveries). Useful for personal P&L review.
    """
    rows = (
        await db.execute(
            select(Signal, SignalDelivery.sent_at)
            .join(SignalDelivery, Signal.id == SignalDelivery.signal_id)
            .where(SignalDelivery.user_id == user.id)
            .order_by(desc(SignalDelivery.sent_at))
            .limit(min(limit, 200))
        )
    ).all()

    recent = [_sig_row(sig, sent_at) for sig, sent_at in rows]

    # Count total delivered (may exceed the limit window)
    total_delivered = (
        (await db.execute(select(SignalDelivery.id).where(SignalDelivery.user_id == user.id))).scalars().all()
    )
    total_count = len(total_delivered)

    resolved = [r for r in recent if r["outcome_pct"] is not None and r["exit_type"] != "pending"]
    wins = [r for r in resolved if r["outcome_pct"] > 0]
    returns = [r["outcome_pct"] for r in resolved]

    win_rate = round(len(wins) / len(resolved) * 100, 1) if resolved else None
    avg_return = round(sum(returns) / len(returns), 2) if returns else None

    sharpe = None
    if len(returns) >= 5:
        mean_r = sum(returns) / len(returns)
        std_r = math.sqrt(sum((r - mean_r) ** 2 for r in returns) / max(len(returns) - 1, 1))
        if std_r > 0:
            sharpe = round((mean_r / std_r) * math.sqrt(252 / 10), 2)

    return {
        "stats": {
            "delivered": total_count,
            "resolved": len(resolved),
            "pending": len([r for r in recent if r["exit_type"] == "pending" or r["outcome_pct"] is None]),
            "win_rate": win_rate,
            "avg_return": avg_return,
            "sharpe": sharpe,
            "wins": len(wins),
            "losses": len(resolved) - len(wins),
        },
        "recent": recent,
    }


# ── PROD-3: Per-user notification preferences ─────────────────────────────────

_NOTIF_PREF_DEFAULTS = {
    "telegram": True,
    "push": True,
    "email": False,
    "min_conf": 45.0,  # override global min_confidence for this user's notifications
    "sectors": [],  # empty list = all sectors; e.g. ["XLK", "XLV"]
    "score_min": 50,  # only notify if raw score >= this threshold
    "actions": ["BUY", "SELL"],  # "BUY" | "SELL" | both — default to both
    "quiet_hours_start": None,
    "quiet_hours_end": None,
    "timezone": "America/New_York",
    "digest_vs_realtime": "realtime",
    "channel_escalation": None,
}

_NOTIF_PREF_KEY = "notification_prefs"


def _user_pref_key(user_id: int) -> str:
    return f"user_{user_id}_{_NOTIF_PREF_KEY}"


class NotificationPrefsIn(BaseModel):
    telegram: Optional[bool] = None
    push: Optional[bool] = None
    email: Optional[bool] = None
    min_conf: Optional[float] = None
    sectors: Optional[list[str]] = None
    score_min: Optional[int] = None
    actions: Optional[list[str]] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    timezone: Optional[str] = None
    digest_vs_realtime: Optional[str] = None
    channel_escalation: Optional[list[str]] = None


@router.get("/notification-prefs")
async def get_notification_prefs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """PROD-3: Return this user's notification preferences (with defaults)."""
    row = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
    stored = ((row.data or {}).get(_user_pref_key(user.id)) or {}) if row else {}
    return {**_NOTIF_PREF_DEFAULTS, **stored}


@router.put("/notification-prefs")
async def update_notification_prefs(
    body: NotificationPrefsIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    PROD-3: Update per-user notification preferences.

    Partial update: only provided fields are changed. Omitted fields keep their
    current value. Preferences are stored in AppSettings JSON — no schema change needed.
    """
    row = (await db.execute(select(AppSettings).where(AppSettings.id == 1))).scalar_one_or_none()
    if row is None:
        row = AppSettings(id=1, data={})
        db.add(row)

    pref_key = _user_pref_key(user.id)
    current = dict(_NOTIF_PREF_DEFAULTS)
    current.update((row.data or {}).get(pref_key) or {})

    updates = body.model_dump(exclude_none=True)
    current.update(updates)

    row.data = {**(row.data or {}), pref_key: current}
    await db.commit()
    return current


@router.get("/risk-acknowledgement")
async def get_risk_acknowledgement(
    user: User = Depends(get_current_user),
):
    """TSYS-13b: whether this user has acknowledged the trading-risk disclosure."""
    return {
        "acknowledged": bool(getattr(user, "risk_acknowledged", False)),
        "acknowledged_at": user.risk_acknowledged_at.isoformat() if user.risk_acknowledged_at else None,
    }


@router.post("/risk-acknowledge")
async def acknowledge_risk(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """TSYS-13b: record the user's acknowledgement of the trading-risk/suitability
    disclosure. Required before connecting a live broker account."""
    from datetime import datetime, timezone

    from services.audit_svc import ACTION_RISK_ACK, record_action

    merged = await db.merge(user)
    merged.risk_acknowledged = True
    merged.risk_acknowledged_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await record_action(db, ACTION_RISK_ACK, user_id=user.id)
    await db.commit()
    return {"acknowledged": True, "acknowledged_at": merged.risk_acknowledged_at.isoformat()}
