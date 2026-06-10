"""
Social OAuth router — Google + Discord.
All providers share the same redirect→callback→one-time-code pattern:
  1. GET /api/auth/{provider}           → redirect to consent screen
  2. GET /api/auth/{provider}/callback  → exchange code, find/create user, issue JWT
  3. GET /api/auth/oauth-exchange?code= → frontend redeems one-time code for access_token
"""

import asyncio
import base64
import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import aiohttp
from config import get_settings
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from models import RefreshToken, User, OAuthState, OAuthOneTimeCode
from services.auth_svc import (
    create_access_token,
    generate_link_code,
    generate_refresh_token,
    hash_password,
    user_to_dict,
)
from services.email_svc import send_welcome
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger("signal.trade.oauth")
router = APIRouter(prefix="/api/auth", tags=["auth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

DISCORD_AUTH_URL = "https://discord.com/api/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_INFO_URL = "https://discord.com/api/users/@me"

from sqlalchemy import delete

_STATE_TTL = 300  # 5 minutes
_CODE_TTL = 60  # 60 seconds

_REFRESH_COOKIE = "st_refresh"
_REFRESH_EXPIRE_DAYS = 30


def _utcnow_naive() -> datetime:
    """UTC timestamp compatible with existing naive SQLAlchemy DateTime columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _generate_pkce() -> tuple[str, str]:
    """Return (code_verifier, code_challenge) using S256."""
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode("ascii")
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode("ascii")
    return verifier, challenge


async def _prune_expired_oauth_data(db: AsyncSession):
    try:
        now = _utcnow_naive()
        await db.execute(delete(OAuthState).where(OAuthState.expires_at < now))
        await db.execute(delete(OAuthOneTimeCode).where(OAuthOneTimeCode.expires_at < now))
        await db.commit()
    except Exception as e:
        log.error(f"[oauth] failed to prune expired oauth data: {e}")


# ── Step 1: Redirect to Google ─────────────────────────────────────────────────


@router.get("/google")
async def google_oauth_start(
    ref: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    s = get_settings()
    if not s.google_client_id:
        raise HTTPException(503, "Google OAuth not configured — set GOOGLE_CLIENT_ID in .env")

    state = secrets.token_urlsafe(24)
    code_verifier, code_challenge = _generate_pkce()
    expires_at = _utcnow_naive() + timedelta(seconds=_STATE_TTL)
    db.add(
        OAuthState(
            state=state,
            referred_by=ref,
            code_challenge=code_challenge,
            code_verifier=code_verifier,
            expires_at=expires_at,
        )
    )
    await db.commit()

    params = urlencode(
        {
            "client_id": s.google_client_id,
            "redirect_uri": f"{s.app_url}/api/auth/google/callback",
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "state": state,
            "prompt": "select_account",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
    )
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{params}")


# ── Step 2: Google callback ────────────────────────────────────────────────────


@router.get("/google/callback")
async def google_oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    s = get_settings()
    await _prune_expired_oauth_data(db)

    state_entry = (await db.execute(select(OAuthState).where(OAuthState.state == state))).scalar_one_or_none()
    if not state_entry or state_entry.expires_at < _utcnow_naive():
        if state_entry:
            await db.delete(state_entry)
            await db.commit()
        raise HTTPException(400, "OAuth state invalid or expired. Please try again.")
    ref_user_id = state_entry.referred_by
    code_verifier = state_entry.code_verifier
    await db.delete(state_entry)
    await db.commit()

    # Exchange code for tokens
    async with aiohttp.ClientSession() as session:
        token_payload = {
            "code": code,
            "client_id": s.google_client_id,
            "client_secret": s.google_client_secret.get_secret_value(),
            "redirect_uri": f"{s.app_url}/api/auth/google/callback",
            "grant_type": "authorization_code",
        }
        if code_verifier:
            token_payload["code_verifier"] = code_verifier
        token_resp = await session.post(GOOGLE_TOKEN_URL, data=token_payload)
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

    email = info.get("email", "").lower().strip()
    sub = info.get("id", "")
    name = info.get("name", "")
    verified = info.get("verified_email", False)

    if not email or not verified:
        raise HTTPException(400, "Google account has no verified email.")

    user = await _upsert_oauth_user(
        db,
        provider="google",
        sub=f"google:{sub}",
        email=email,
        name=name,
        ref_user_id=ref_user_id,
    )
    otc = await _issue_otc(user, db)
    return RedirectResponse(f"{s.app_url}/app?oauth_code={otc}")


# ── Step 3: Frontend exchanges one-time code for token ────────────────────────


@router.get("/oauth-exchange")
async def oauth_exchange(
    code: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    from fastapi.responses import JSONResponse

    await _prune_expired_oauth_data(db)

    code_entry = (await db.execute(select(OAuthOneTimeCode).where(OAuthOneTimeCode.code == code))).scalar_one_or_none()
    if not code_entry or code_entry.expires_at < _utcnow_naive():
        if code_entry:
            await db.delete(code_entry)
            await db.commit()
        raise HTTPException(400, "OAuth code invalid, already consumed, or expired.")

    user_data = code_entry.user_data
    access_token = user_data["access_token"]
    raw_refresh = user_data["refresh_token"]
    user_id = user_data["user_id"]
    user_dict = user_data["user"]

    # Atomically consume the code and persist the refresh token
    await db.delete(code_entry)
    token_hash = hashlib.sha256(raw_refresh.encode()).hexdigest()
    expires_at = _utcnow_naive() + timedelta(days=_REFRESH_EXPIRE_DAYS)
    db.add(RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at))

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(400, "OAuth code already consumed.")
    except Exception:
        await db.rollback()
        log.exception("[oauth] failed to persist refresh token during exchange")
        raise HTTPException(500, "OAuth exchange failed. Please try again.")

    s = get_settings()
    resp = JSONResponse({"access_token": access_token, "token_type": "bearer", "user": user_dict})
    resp.set_cookie(
        key=_REFRESH_COOKIE,
        value=raw_refresh,
        httponly=True,
        secure=s.app_url.startswith("https"),
        samesite="lax",
        max_age=_REFRESH_EXPIRE_DAYS * 86400,
        path="/api/auth/refresh-cookie",
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
    """Find or create a user from any OAuth provider. Always sets email_verified=True.

    Never auto-link by email — if a password account exists with the same email,
    the user must log in with their password first and explicitly link the OAuth
    account to prevent account takeover via pre-registration.
    """
    user = (await db.execute(select(User).where(User.oauth_sub == sub))).scalar_one_or_none()
    if not user:
        existing_by_email = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
        if existing_by_email:
            raise HTTPException(
                409,
                "An account with this email already exists. Log in with your password first, then link your social account from settings.",
            )

    if user:
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


async def _issue_otc(user: User, db: AsyncSession) -> str:
    """Create a short-lived one-time code, store it, return the code."""
    access_token = create_access_token(user.id, user.subscription_tier, user.is_owner)
    raw_refresh, _hashed_refresh = generate_refresh_token()
    otc = secrets.token_urlsafe(32)
    expires_at = _utcnow_naive() + timedelta(seconds=_CODE_TTL)

    user_data = {
        "access_token": access_token,
        "refresh_token": raw_refresh,
        "user_id": user.id,
        "user": user_to_dict(user),
    }
    db.add(OAuthOneTimeCode(code=otc, access_token=access_token, user_data=user_data, expires_at=expires_at))
    await db.commit()
    return otc


# ── Discord: Step 1 ───────────────────────────────────────────────────────────


@router.get("/discord")
async def discord_oauth_start(
    ref: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    s = get_settings()
    if not s.discord_client_id:
        raise HTTPException(503, "Discord OAuth not configured — set DISCORD_CLIENT_ID in .env")

    state = secrets.token_urlsafe(24)
    code_verifier, code_challenge = _generate_pkce()
    expires_at = _utcnow_naive() + timedelta(seconds=_STATE_TTL)
    db.add(
        OAuthState(
            state=state,
            referred_by=ref,
            code_challenge=code_challenge,
            code_verifier=code_verifier,
            expires_at=expires_at,
        )
    )
    await db.commit()

    params = urlencode(
        {
            "client_id": s.discord_client_id,
            "redirect_uri": f"{s.app_url}/api/auth/discord/callback",
            "response_type": "code",
            "scope": "identify email",
            "state": state,
            "prompt": "none",  # skip consent if already authorised
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
    )
    return RedirectResponse(f"{DISCORD_AUTH_URL}?{params}")


# ── Discord: Step 2 ───────────────────────────────────────────────────────────


@router.get("/discord/callback")
async def discord_oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    s = get_settings()
    await _prune_expired_oauth_data(db)

    state_entry = (await db.execute(select(OAuthState).where(OAuthState.state == state))).scalar_one_or_none()
    if not state_entry or state_entry.expires_at < _utcnow_naive():
        if state_entry:
            await db.delete(state_entry)
            await db.commit()
        raise HTTPException(400, "OAuth state invalid or expired. Please try again.")
    ref_user_id = state_entry.referred_by
    code_verifier = state_entry.code_verifier
    await db.delete(state_entry)
    await db.commit()

    async with aiohttp.ClientSession() as session:
        # Exchange code for access token
        token_payload = {
            "client_id": s.discord_client_id,
            "client_secret": s.discord_client_secret.get_secret_value(),
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": f"{s.app_url}/api/auth/discord/callback",
        }
        if code_verifier:
            token_payload["code_verifier"] = code_verifier
        token_resp = await session.post(
            DISCORD_TOKEN_URL,
            data=token_payload,
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

    email = info.get("email", "").lower().strip()
    verified = info.get("verified", False)
    sub = str(info.get("id", ""))
    # Use global_name first (Discord display name), fall back to username
    name = info.get("global_name") or info.get("username") or ""

    if not email:
        return RedirectResponse(f"{s.app_url}/login?error=discord_no_email")
    if not verified:
        return RedirectResponse(f"{s.app_url}/login?error=discord_unverified_email")

    user = await _upsert_oauth_user(
        db,
        provider="discord",
        sub=f"discord:{sub}",
        email=email,
        name=name,
        ref_user_id=ref_user_id,
    )
    otc = await _issue_otc(user, db)
    return RedirectResponse(f"{s.app_url}/app?oauth_code={otc}")
