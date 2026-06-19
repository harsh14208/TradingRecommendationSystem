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

    # DISC-8: sync min_confidence_override DB column with JSON prefs so the
    # column stays the source of truth for ad-hoc queries and doesn't drift stale.
    if "min_conf" in updates:
        user.min_confidence_override = updates["min_conf"]
        await db.commit()
    else:
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


class OptionsSettingsUpdate(BaseModel):
    options_mode: Optional[str] = None
    options_capital: Optional[float] = None
    options_risk_per_trade: Optional[float] = None
    options_max_book_risk: Optional[float] = None
    options_max_positions: Optional[int] = None
    options_max_iv_sell: Optional[float] = None


@router.get("/options/settings")
async def get_options_settings(
    user: User = Depends(get_current_user),
):
    """Return the current user's options execution settings and acknowledgement state."""
    return {
        "options_mode": user.options_mode,
        "options_capital": user.options_capital,
        "options_risk_per_trade": user.options_risk_per_trade,
        "options_max_book_risk": user.options_max_book_risk,
        "options_max_positions": user.options_max_positions,
        "options_max_iv_sell": user.options_max_iv_sell,
        "options_risk_acknowledged": bool(user.options_risk_acknowledged),
        "options_risk_acknowledged_at": (
            user.options_risk_acknowledged_at.isoformat() if user.options_risk_acknowledged_at else None
        ),
    }


@router.put("/options/settings")
async def update_options_settings(
    update: OptionsSettingsUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update options execution settings.

    ``paper`` and ``live`` modes require the options-specific risk acknowledgement.
    ``live`` additionally requires the generic trading-risk acknowledgement and an
    Alpaca account with options approval level >= 3.
    """
    from fastapi import HTTPException

    from services.audit_svc import ACTION_OPTIONS_SETTINGS, record_action
    from services.broker_svc import decrypt_credential

    merged = await db.merge(user)

    if update.options_mode is not None:
        new_mode = update.options_mode
        if new_mode not in {"none", "signal", "paper", "live"}:
            raise HTTPException(status_code=400, detail=f"Invalid options_mode: {new_mode}")

        if new_mode in ("paper", "live") and not merged.options_risk_acknowledged:
            raise HTTPException(
                status_code=403,
                detail="Options risk acknowledgement is required before enabling paper or live mode.",
            )

        if new_mode == "live":
            if not merged.risk_acknowledged:
                raise HTTPException(
                    status_code=403,
                    detail="Trading risk acknowledgement is required before live options execution.",
                )
            if merged.auto_execute_broker != "alpaca" or not merged.alpaca_key_enc:
                raise HTTPException(
                    status_code=400,
                    detail="Live options requires Alpaca broker credentials. Connect Alpaca first.",
                )
            # Verify Alpaca options approval level.
            try:
                from services import alpaca_rest

                key = decrypt_credential(merged.alpaca_key_enc) or ""
                secret = decrypt_credential(merged.alpaca_secret_enc) if merged.alpaca_secret_enc else ""
                live = merged.alpaca_account_type == "live"
                account = await alpaca_rest.get_account(key, secret, live=live)
                approved = account.get("option_approved_level") or account.get("option_trading_level") or 0
                if int(approved) < 3:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Alpaca account options approval level {approved} is insufficient for live trading.",
                    )
            except HTTPException:
                raise
            except Exception as exc:
                raise HTTPException(
                    status_code=502,
                    detail=f"Could not verify Alpaca account options approval: {exc}",
                )

        merged.options_mode = new_mode

    if update.options_capital is not None:
        merged.options_capital = max(0.0, update.options_capital)
    if update.options_risk_per_trade is not None:
        merged.options_risk_per_trade = max(0.0, min(1.0, update.options_risk_per_trade))
    if update.options_max_book_risk is not None:
        merged.options_max_book_risk = max(0.0, min(1.0, update.options_max_book_risk))
    if update.options_max_positions is not None:
        merged.options_max_positions = max(1, update.options_max_positions)
    if update.options_max_iv_sell is not None:
        merged.options_max_iv_sell = max(0.0, min(2.0, update.options_max_iv_sell))

    await record_action(db, ACTION_OPTIONS_SETTINGS, user_id=user.id, details=update.model_dump(exclude_unset=True))
    await db.commit()
    return await get_options_settings(merged)


@router.post("/options/risk-acknowledge")
async def acknowledge_options_risk(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record the user's acknowledgement of the options-specific risk disclosure."""
    from datetime import datetime, timezone

    from services.audit_svc import ACTION_OPTIONS_RISK_ACK, record_action

    merged = await db.merge(user)
    merged.options_risk_acknowledged = True
    merged.options_risk_acknowledged_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await record_action(db, ACTION_OPTIONS_RISK_ACK, user_id=user.id)
    await db.commit()
    return {"acknowledged": True, "acknowledged_at": merged.options_risk_acknowledged_at.isoformat()}
