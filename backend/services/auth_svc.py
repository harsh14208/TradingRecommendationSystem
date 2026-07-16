"""
Auth service: JWT creation/validation, password hashing,
FastAPI dependencies for authentication and tier-gating.
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt as _bcrypt_lib
from config import get_settings, tier_gte
from database import get_db
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from models import User
from sqlalchemy.ext.asyncio import AsyncSession

_bearer = HTTPBearer(auto_error=False)


# ── Passwords ─────────────────────────────────────────────────────────────────


def hash_password(plain: str) -> str:
    return _bcrypt_lib.hashpw(plain.encode()[:72], _bcrypt_lib.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt_lib.checkpw(plain.encode()[:72], hashed.encode())
    except Exception:
        return False


# ── JWT ───────────────────────────────────────────────────────────────────────


def _secret() -> str:
    return get_settings().jwt_secret_key


def _algo() -> str:
    return get_settings().jwt_algorithm


def _utcnow_naive() -> datetime:
    """UTC timestamp compatible with existing naive DB/JWT datetime usage."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def create_access_token(user_id: int, tier: str, is_owner: bool) -> str:
    s = get_settings()
    expire = _utcnow_naive() + timedelta(minutes=s.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "tier": tier, "owner": is_owner, "exp": expire},
        _secret(),
        algorithm=_algo(),
    )


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, _secret(), algorithms=[_algo()])
    except jwt.InvalidTokenError:
        return None


# ── Refresh tokens ────────────────────────────────────────────────────────────


def generate_refresh_token() -> tuple[str, str]:
    """Returns (raw_token_to_send_to_client, sha256_hash_to_store)."""
    raw = secrets.token_urlsafe(48)
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return raw, hashed


# ── Telegram link codes ───────────────────────────────────────────────────────


def generate_link_code() -> str:
    return secrets.token_hex(8).upper()  # e.g. "A1B2C3D4E5F6A7B8"


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def _get_user_from_token(
    creds: HTTPAuthorizationCredentials | None,
    db: AsyncSession,
) -> User | None:
    if not creds:
        return None
    payload = decode_access_token(creds.credentials)
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    row = await db.get(User, user_id)
    if not row or not row.is_active:
        return None
    return row


async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_from_token(creds, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_user_optional(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Returns None instead of raising when not authenticated."""
    return await _get_user_from_token(creds, db)


def require_tier(min_tier: str):
    """
    Dependency factory.  Usage:
        @router.get("/feature", dependencies=[Depends(require_tier("pro"))])
    """

    async def _dep(user: User = Depends(get_current_user)):
        if user.is_owner:
            return user
        if not tier_gte(user.subscription_tier, min_tier):
            raise HTTPException(
                status_code=402,
                detail=f"This feature requires the {min_tier.capitalize()} plan or higher.",
            )
        return user

    return _dep


def user_to_dict(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "full_name": u.full_name,
        "is_owner": u.is_owner,
        "subscription_tier": u.subscription_tier,
        "subscription_status": u.subscription_status,
        "subscription_period_end": (u.subscription_period_end.isoformat() if u.subscription_period_end else None),
        "telegram_linked": bool(u.telegram_chat_id),
        "telegram_link_code": u.telegram_link_code,
        "min_confidence_override": u.min_confidence_override,
        "discord_webhook_url": getattr(u, "discord_webhook_url", None),
        "webhook_url": getattr(u, "webhook_url", None),
        "oauth_provider": getattr(u, "oauth_provider", None),
        "auto_execute": getattr(u, "auto_execute", False),
        "auto_execute_min_conf": getattr(u, "auto_execute_min_conf", None),
        "auto_execute_broker": getattr(u, "auto_execute_broker", None),
        "auto_execute_qty_dollars": getattr(u, "auto_execute_qty_dollars", None),
        "options_mode": getattr(u, "options_mode", "signal"),
        "options_risk_acknowledged": bool(getattr(u, "options_risk_acknowledged", False)),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }
