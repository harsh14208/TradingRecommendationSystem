"""
Broker connection management — users connect their own Alpaca account
for auto-execution of signals.

Endpoints:
  GET  /api/me/broker/status      — connection status + account summary
  POST /api/me/broker/connect     — save credentials (verified before storing)
  DELETE /api/me/broker/disconnect — clear credentials
  GET  /api/me/broker/orders      — recent auto-executed orders
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import tier_gte
from database import get_db
from models import BrokerOrder, User
from services.auth_svc import get_current_user

log = logging.getLogger("broker_router")

router = APIRouter(prefix="/api/me/broker", tags=["broker"])

_VALID_ACCOUNT_TYPES = frozenset({"paper", "live"})
_VALID_BROKERS = frozenset({"alpaca"})


def _require_pro(user: User) -> None:
    """Raise 403 if user is not Pro or owner."""
    if user.is_owner:
        return
    if not (user.subscription_status == "active" and tier_gte(user.subscription_tier, "pro")):
        raise HTTPException(status_code=403, detail="Broker auto-execution requires a Pro subscription")


# ── Schemas ───────────────────────────────────────────────────────────────────


class BrokerConnectIn(BaseModel):
    broker: str = "alpaca"
    account_type: str  # "paper" | "live"
    api_key: str
    api_secret: str

    @field_validator("broker")
    @classmethod
    def _valid_broker(cls, v: str) -> str:
        if v not in _VALID_BROKERS:
            raise ValueError(f"broker must be one of {sorted(_VALID_BROKERS)}")
        return v

    @field_validator("account_type")
    @classmethod
    def _valid_account_type(cls, v: str) -> str:
        if v not in _VALID_ACCOUNT_TYPES:
            raise ValueError(f"account_type must be one of {sorted(_VALID_ACCOUNT_TYPES)}")
        return v

    @field_validator("api_key", "api_secret")
    @classmethod
    def _non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be empty")
        return v.strip()


class AutoExecuteSettingsIn(BaseModel):
    enabled: bool | None = None
    min_conf: float | None = None  # 50–100
    qty_dollars: float | None = None  # minimum $1

    @field_validator("min_conf")
    @classmethod
    def _valid_conf(cls, v: float | None) -> float | None:
        if v is not None and not (50 <= v <= 100):
            raise ValueError("min_conf must be between 50 and 100")
        return v

    @field_validator("qty_dollars")
    @classmethod
    def _valid_qty(cls, v: float | None) -> float | None:
        if v is not None and v < 1.0:
            raise ValueError("qty_dollars must be at least $1")
        return v


# ── Routes ────────────────────────────────────────────────────────────────────


@router.get("/status")
async def broker_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return broker connection status and Alpaca account summary if connected."""
    _require_pro(user)

    if not user.alpaca_key_enc or not user.alpaca_secret_enc:
        return {
            "connected": False,
            "broker": user.auto_execute_broker,
            "account_type": user.alpaca_account_type,
            "auto_execute": user.auto_execute,
            "min_conf": user.auto_execute_min_conf or 75.0,
            "qty_dollars": user.auto_execute_qty_dollars or 100.0,
        }

    from services.broker_svc import decrypt_credential, verify_alpaca_connection

    key = decrypt_credential(user.alpaca_key_enc)
    secret = decrypt_credential(user.alpaca_secret_enc)
    live = user.alpaca_account_type == "live"

    if not key or not secret:
        return {"connected": False, "error": "Credential decryption failed — please reconnect"}

    try:
        account = await verify_alpaca_connection(key, secret, live)
        return {
            "connected": True,
            "broker": user.auto_execute_broker or "alpaca",
            "account_type": user.alpaca_account_type,
            "auto_execute": user.auto_execute,
            "min_conf": user.auto_execute_min_conf or 75.0,
            "qty_dollars": user.auto_execute_qty_dollars or 100.0,
            "account": {
                "id": account.get("id", ""),
                "status": account.get("status", ""),
                "equity": account.get("equity", ""),
                "buying_power": account.get("buying_power", ""),
                "currency": account.get("currency", "USD"),
            },
        }
    except ValueError as e:
        return {"connected": False, "error": str(e)}


@router.post("/connect", status_code=201)
async def broker_connect(
    body: BrokerConnectIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify and save Alpaca API credentials.

    Credentials are verified by calling /v2/account before being encrypted
    and stored. Returns the Alpaca account summary on success.
    """
    _require_pro(user)

    from services.broker_svc import encrypt_credential, verify_alpaca_connection

    live = body.account_type == "live"
    try:
        account = await verify_alpaca_connection(body.api_key, body.api_secret, live)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    merged = await db.merge(user)
    merged.alpaca_key_enc = encrypt_credential(body.api_key)
    merged.alpaca_secret_enc = encrypt_credential(body.api_secret)
    merged.alpaca_account_type = body.account_type
    merged.auto_execute_broker = body.broker
    await db.commit()
    await db.refresh(merged)

    log.info("broker_connect: user=%d connected alpaca/%s", user.id, body.account_type)

    return {
        "connected": True,
        "broker": body.broker,
        "account_type": body.account_type,
        "account": {
            "id": account.get("id", ""),
            "status": account.get("status", ""),
            "equity": account.get("equity", ""),
            "buying_power": account.get("buying_power", ""),
        },
    }


@router.delete("/disconnect", status_code=200)
async def broker_disconnect(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Clear stored broker credentials and disable auto-execution."""
    _require_pro(user)

    merged = await db.merge(user)
    merged.alpaca_key_enc = None
    merged.alpaca_secret_enc = None
    merged.alpaca_account_type = None
    merged.auto_execute = False
    await db.commit()

    log.info("broker_disconnect: user=%d disconnected", user.id)
    return {"connected": False}


@router.patch("/settings", status_code=200)
async def update_auto_execute_settings(
    body: AutoExecuteSettingsIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update auto-execution toggle, confidence threshold, and notional size."""
    _require_pro(user)

    if body.enabled and not user.alpaca_key_enc:
        raise HTTPException(status_code=422, detail="Connect a broker account before enabling auto-execution")

    merged = await db.merge(user)
    if body.enabled is not None:
        merged.auto_execute = body.enabled
    if body.min_conf is not None:
        merged.auto_execute_min_conf = body.min_conf
    if body.qty_dollars is not None:
        merged.auto_execute_qty_dollars = body.qty_dollars
    await db.commit()

    return {
        "auto_execute": merged.auto_execute,
        "min_conf": merged.auto_execute_min_conf or 75.0,
        "qty_dollars": merged.auto_execute_qty_dollars or 100.0,
    }


@router.get("/orders")
async def list_broker_orders(
    limit: int = 50,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the user's recent auto-executed orders (newest first)."""
    _require_pro(user)

    rows = (
        (
            await db.execute(
                select(BrokerOrder)
                .where(BrokerOrder.user_id == user.id)
                .order_by(BrokerOrder.created_at.desc())
                .limit(min(limit, 200))
            )
        )
        .scalars()
        .all()
    )

    return [
        {
            "id": r.id,
            "signal_id": r.signal_id,
            "broker": r.broker,
            "account_type": r.account_type,
            "alpaca_order_id": r.alpaca_order_id,
            "symbol": r.symbol,
            "notional": r.notional,
            "side": r.side,
            "status": r.status,
            "error_msg": r.error_msg,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
