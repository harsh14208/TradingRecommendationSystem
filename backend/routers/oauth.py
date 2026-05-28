"""
Social OAuth router — Google + Discord.
All providers share the same redirect→callback→one-time-code pattern:
  1. GET /api/auth/{provider}           → redirect to consent screen
  2. GET /api/auth/{provider}/callback  → exchange code, find/create user, issue JWT
  3. GET /api/auth/oauth-exchange?code= → frontend redeems one-time code for access_token
"""
import asyncio
import logging
import secrets
import time
from urllib.parse import urlencode

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from services.email_svc import send_welcome
from database import get_db
from models import User
from services.auth_svc import (
    create_access_token,
    generate_link_code,
    generate_refresh_token,
    hash_password,
    user_to_dict,
)
from models import RefreshToken
from datetime import datetime, timedelta, timezone

log = logging.getLogger("signal.trade.oauth")
router = APIRouter(prefix="/api/auth", tags=["auth"])

GOOGLE_AUTH_URL   = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL  = "https://oauth2.googleapis.com/token"
GOOGLE_INFO_URL   = "https://www.googleapis.com/oauth2/v2/userinfo"

DISCORD_AUTH_URL  = "https://discord.com/api/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_INFO_URL  = "https://discord.com/api/users/@me"

# In-memory stores (single-process safe; resets on restart which is acceptable)
_state_store: dict[str, tuple[int | None, float]] = {}   # state → (ref_user_id, expires)
_code_store:  dict[str, tuple[str, dict, float]]  = {}   # one-time-code → (access_token, user_dict, expires)

_STATE_TTL = 300   # 5 minutes
_CODE_TTL  = 60    # 60 seconds


def _prune(store: dict, now: float):
    expired = [k for k, v in store.items() if v[-1] < now]
    for k in expired:
        del store[k]


# ── Step 1: Redirect to Google ─────────────────────────────────────────────────

@router.get("/google")
async def google_oauth_start(ref: int | None = Query(None)):
    s = get_settings()
    if not s.google_client_id:
        raise HTTPException(503, "Google OAuth not configured — set GOOGLE_CLIENT_ID in .env")

    state = secrets.token_urlsafe(24)
    _state_store[state] = (ref, time.monotonic() + _STATE_TTL)

    params = urlencode({
        "client_id":     s.google_client_id,
        "redirect_uri":  f"{s.app_url}/api/auth/google/callback",
        "response_type": "code",
        "scope":         "openid email profile",
        "access_type":   "offline",
        "state":         state,
        "prompt":        "select_account",
    })
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{params}")


# ── Step 2: Google callback ────────────────────────────────────────────────────

@router.get("/google/callback")
async def google_oauth_callback(
    code:  str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    s = get_settings()
    now = time.monotonic()
    _prune(_state_store, now)

    state_entry = _state_store.pop(state, None)
    if not state_entry or state_entry[1] < now:
        raise HTTPException(400, "OAuth state invalid or expired. Please try again.")
    ref_user_id = state_entry[0]

    # Exchange code for tokens
    async with aiohttp.ClientSession() as session:
        token_resp = await session.post(GOOGLE_TOKEN_URL, data={
            "code":          code,
            "client_id":     s.google_client_id,
            "client_secret": s.google_client_secret,
            "redirect_uri":  f"{s.app_url}/api/auth/google/callback",
            "grant_type":    "authorization_code",
        })
        if token_resp.status != 200:
            body = await token_resp.text()
            log.error(f"[oauth] token exchange failed: {body}")
            raise HTTPException(502, "Failed to exchange OAuth code with Google.")
        tokens = await token_resp.json()

        info_resp = await session.get(
            GOOGLE_INFO_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        if info_resp.status != 200:
            raise HTTPException(502, "Failed to fetch Google user info.")
        info = await info_resp.json()

    email    = info.get("email", "").lower().strip()
    sub      = info.get("id", "")
    name     = info.get("name", "")
    verified = info.get("verified_email", False)

    if not email or not verified:
        raise HTTPException(400, "Google account has no verified email.")

    user = await _upsert_oauth_user(
        db, provider="google", sub=sub,
        email=email, name=name, ref_user_id=ref_user_id,
    )
    otc = _issue_otc(user)
    return RedirectResponse(f"{s.app_url}/app?oauth_code={otc}")


# ── Step 3: Frontend exchanges one-time code for token ────────────────────────

_REFRESH_COOKIE = "st_refresh"
_REFRESH_EXPIRE_DAYS = 30


def _utcnow_naive() -> datetime:
    """UTC timestamp compatible with existing naive SQLAlchemy DateTime columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

@router.get("/oauth-exchange")
async def oauth_exchange(
    code: str = Query(...),
    db:   AsyncSession = Depends(get_db),
):
    from fastapi.responses import JSONResponse
    import hashlib

    now = time.monotonic()
    _prune(_code_store, now)

    entry = _code_store.pop(code, None)
    if not entry or entry[2] < now:
        raise HTTPException(400, "OAuth code invalid or expired.")

    access_token, user_dict, _, user_id, raw_refresh = entry

    # Persist the refresh token so the user can renew their session silently
    try:
        token_hash = hashlib.sha256(raw_refresh.encode()).hexdigest()
        expires_at = _utcnow_naive() + timedelta(days=_REFRESH_EXPIRE_DAYS)
        db.add(RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at))
        await db.commit()
    except Exception:
        pass  # non-fatal; worst case user re-authenticates after access token expires

    resp = JSONResponse({"access_token": access_token, "token_type": "bearer", "user": user_dict})
    resp.set_cookie(
        key=_REFRESH_COOKIE,
        value=raw_refresh,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=_REFRESH_EXPIRE_DAYS * 86400,
        path="/",
    )
    return resp

# ── Shared helper ─────────────────────────────────────────────────────────────

async def _upsert_oauth_user(
    db: AsyncSession,
    *,
    provider: str,
    sub: str,
    email: str,
    name: str,
    ref_user_id: int | None,
) -> User:
    """Find or create a user from any OAuth provider. Always sets email_verified=True."""
    user = (await db.execute(select(User).where(User.oauth_sub == sub))).scalar_one_or_none()
    if not user:
        user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()

    if user:
        if not user.oauth_sub:
            user.oauth_sub = sub
            user.oauth_provider = provider
        if not user.email_verified:
            user.email_verified = True
            user.email_verify_token = None
        user.last_seen_at = _utcnow_naive()
        if name and not user.full_name:
            user.full_name = name
    else:
        user = User(
            email=email,
            password_hash=hash_password(secrets.token_hex(32)),
            full_name=name or None,
            oauth_provider=provider,
            oauth_sub=sub,
            telegram_link_code=generate_link_code(),
            referred_by=ref_user_id,
            email_verified=True,
            email_verify_token=None,
        )
        db.add(user)
        asyncio.create_task(send_welcome(email, name or ""))
        log.info(f"[oauth] new user via {provider}: {email}")

    await db.commit()
    await db.refresh(user)
    return user


def _issue_otc(user: User) -> str:
    """Create a short-lived one-time code, store it, return the code."""
    access_token = create_access_token(user.id, user.subscription_tier, user.is_owner)
    refresh_token = generate_refresh_token()
    otc = secrets.token_urlsafe(32)
    # Store (access_token, user_dict, expiry, user_id, raw_refresh_token)
    _code_store[otc] = (access_token, user_to_dict(user), time.monotonic() + _CODE_TTL, user.id, refresh_token)
    return otc


# ── Discord: Step 1 ───────────────────────────────────────────────────────────

@router.get("/discord")
async def discord_oauth_start(ref: int | None = Query(None)):
    s = get_settings()
    if not s.discord_client_id:
        raise HTTPException(503, "Discord OAuth not configured — set DISCORD_CLIENT_ID in .env")

    state = secrets.token_urlsafe(24)
    _state_store[state] = (ref, time.monotonic() + _STATE_TTL)

    params = urlencode({
        "client_id":     s.discord_client_id,
        "redirect_uri":  f"{s.app_url}/api/auth/discord/callback",
        "response_type": "code",
        "scope":         "identify email",
        "state":         state,
        "prompt":        "none",   # skip consent if already authorised
    })
    return RedirectResponse(f"{DISCORD_AUTH_URL}?{params}")


# ── Discord: Step 2 ───────────────────────────────────────────────────────────

@router.get("/discord/callback")
async def discord_oauth_callback(
    code:  str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    s = get_settings()
    now = time.monotonic()
    _prune(_state_store, now)

    state_entry = _state_store.pop(state, None)
    if not state_entry or state_entry[1] < now:
        raise HTTPException(400, "OAuth state invalid or expired. Please try again.")
    ref_user_id = state_entry[0]

    async with aiohttp.ClientSession() as session:
        # Exchange code for access token
        token_resp = await session.post(
            DISCORD_TOKEN_URL,
            data={
                "client_id":     s.discord_client_id,
                "client_secret": s.discord_client_secret,
                "grant_type":    "authorization_code",
                "code":          code,
                "redirect_uri":  f"{s.app_url}/api/auth/discord/callback",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if token_resp.status != 200:
            body = await token_resp.text()
            log.error(f"[oauth/discord] token exchange failed: {body}")
            raise HTTPException(502, "Failed to exchange OAuth code with Discord.")
        tokens = await token_resp.json()

        # Fetch user profile
        info_resp = await session.get(
            DISCORD_INFO_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        if info_resp.status != 200:
            raise HTTPException(502, "Failed to fetch Discord user info.")
        info = await info_resp.json()

    email    = info.get("email", "").lower().strip()
    verified = info.get("verified", False)
    sub      = str(info.get("id", ""))
    # Use global_name first (Discord display name), fall back to username
    name     = info.get("global_name") or info.get("username") or ""

    if not email:
        return RedirectResponse(f"{s.app_url}/login?error=discord_no_email")
    if not verified:
        return RedirectResponse(f"{s.app_url}/login?error=discord_unverified_email")

    user = await _upsert_oauth_user(
        db, provider="discord", sub=f"discord:{sub}",
        email=email, name=name, ref_user_id=ref_user_id,
    )
    otc = _issue_otc(user)
    return RedirectResponse(f"{s.app_url}/app?oauth_code={otc}")
