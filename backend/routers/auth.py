"""
Auth router — register, login, refresh, me, logout, Telegram link code.
All endpoints are under /api/auth.
"""
import hashlib
import logging
import secrets as _secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from pydantic import BaseModel, EmailStr, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

_limiter = Limiter(key_func=get_remote_address)

from config import get_settings
from database import get_db
from models import RefreshToken, User
from services.auth_svc import (
    create_access_token,
    decode_access_token,
    generate_link_code,
    generate_refresh_token,
    get_current_user,
    hash_password,
    user_to_dict,
    verify_password,
)
from services.email_svc import send_welcome, send_verification_email

log = logging.getLogger("signal.trade.auth")
router = APIRouter(prefix="/api/auth", tags=["auth"])

REFRESH_COOKIE = "st_refresh"


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class RegisterIn(BaseModel):
    email: str
    password: str
    full_name: str = ""

    @field_validator("email")
    @classmethod
    def email_format(cls, v: str) -> str:
        import re
        v = v.strip().lower()
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', v):
            raise ValueError("Invalid email address")
        if len(v) > 254:
            raise ValueError("Email address too long")
        return v

    @field_validator("password")
    @classmethod
    def pw_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("Password must be 128 characters or fewer")
        return v

    @field_validator("full_name")
    @classmethod
    def name_length(cls, v: str) -> str:
        v = v.strip()
        if len(v) > 60:
            raise ValueError("Name must be 60 characters or fewer")
        return v


class LoginIn(BaseModel):
    email: str
    password: str


class ChangePasswordIn(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def pw_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("Password must be 128 characters or fewer")
        return v


class ForgotPasswordIn(BaseModel):
    email: str


class ResetPasswordIn(BaseModel):
    token: str
    new_password: str


# Token store: token → (email, expires_ts)
_reset_tokens: dict[str, tuple[str, float]] = {}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _set_refresh_cookie(response: Response, token: str):
    s = get_settings()
    response.set_cookie(
        REFRESH_COOKIE, token,
        httponly=True, samesite="lax", secure=get_settings().app_url.startswith("https"),
        max_age=s.refresh_token_expire_days * 86400,
        path="/api/auth/refresh-cookie",

    )


def _clear_refresh_cookie(response: Response):
    response.delete_cookie(REFRESH_COOKIE, path="/api/auth/refresh-cookie")


async def _create_tokens(user: User, db: AsyncSession, response: Response) -> dict:
    s = get_settings()
    access = create_access_token(user.id, user.subscription_tier, user.is_owner)
    raw_refresh, hashed_refresh = generate_refresh_token()
    from datetime import timezone
    expire = datetime.now(timezone.utc) + timedelta(days=s.refresh_token_expire_days)
    db.add(RefreshToken(user_id=user.id, token_hash=hashed_refresh, expires_at=expire))
    await db.commit()
    _set_refresh_cookie(response, raw_refresh)
    return {"access_token": access, "token_type": "bearer", "user": user_to_dict(user)}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/register", status_code=201)
@_limiter.limit("10/minute")
async def register(
    request: Request,
    body: RegisterIn,
    response: Response,
    ref: int | None = Query(None),   # ?ref=<user_id> referral tracking
    db: AsyncSession = Depends(get_db),
):
    email = body.email.lower().strip()
    existing = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if existing:
        raise HTTPException(400, "An account with this email already exists.")

    # Validate referrer exists (silently ignore invalid refs)
    referrer_id: int | None = None
    if ref:
        referrer = (await db.execute(select(User).where(User.id == ref))).scalar_one_or_none()
        if referrer:
            referrer_id = referrer.id

    verify_token = _secrets.token_urlsafe(32)
    s = get_settings()
    # Auto-verify when: (a) owner email, or (b) SMTP not configured (can't send email)
    smtp_ready    = bool(s.smtp_host and s.smtp_user)
    auto_verified = email == (s.owner_email or "").lower() or not smtp_ready

    user = User(
        email=email,
        password_hash=hash_password(body.password),
        full_name=body.full_name.strip() or None,
        telegram_link_code=generate_link_code(),
        referred_by=referrer_id,
        email_verified=auto_verified,
        email_verify_token=None if auto_verified else verify_token,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    import asyncio
    if auto_verified:
        asyncio.create_task(send_welcome(user.email, user.full_name or ""))
        if not smtp_ready:
            log.info(f"[auth] registered (auto-verified, SMTP not configured) {user.email}")
        else:
            log.info(f"[auth] registered (owner/auto-verified) {user.email}")
        return await _create_tokens(user, db, response)

    # Send verification email — user must click before they can log in
    verify_link = f"{s.app_url}/verify-email?token={verify_token}"
    asyncio.create_task(send_verification_email(user.email, user.full_name or "", verify_link))
    log.info(f"[auth] registered (pending verification) {user.email}")
    response.status_code = 201
    return {"message": "Account created. Check your email to verify your address.", "email": email}


@router.post("/login")
@_limiter.limit("10/minute")
async def login(request: Request, body: LoginIn, response: Response, db: AsyncSession = Depends(get_db)):
    email = body.email.lower().strip()
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password.")
    if not user.is_active:
        raise HTTPException(403, "Account disabled. Contact support.")
    if not user.email_verified:
        raise HTTPException(403, detail={"code": "email_unverified", "message": "Please verify your email before logging in. Check your inbox or request a new link."})

    from datetime import timezone
    user.last_seen_at = datetime.now(timezone.utc)
    await db.commit()

    log.info(f"[auth] login {user.email}")
    return await _create_tokens(user, db, response)


@router.post("/refresh")
async def refresh_token(response: Response, db: AsyncSession = Depends(get_db)):
    # Cookie is read via Request in this route
    raise HTTPException(501, "Use cookie-based refresh — see /api/auth/refresh-cookie")


@router.post("/refresh-cookie")
async def refresh_cookie(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    raw = request.cookies.get(REFRESH_COOKIE)
    if not raw:
        raise HTTPException(401, "No refresh token.")
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    from datetime import timezone
    now = datetime.now(timezone.utc)
    token_row = (await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == hashed,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > now,
        )
    )).scalar_one_or_none()
    if not token_row:
        _clear_refresh_cookie(response)
        raise HTTPException(401, "Invalid or expired refresh token.")

    user = await db.get(User, token_row.user_id)
    if not user or not user.is_active:
        raise HTTPException(401, "Account not found.")

    # Rotate: revoke old, issue new
    token_row.revoked = True
    user.last_seen_at = now
    return await _create_tokens(user, db, response)


@router.post("/logout")
async def logout(response: Response, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # Revoke all refresh tokens for this user
    from sqlalchemy import update
    await db.execute(
        update(RefreshToken).where(RefreshToken.user_id == user.id).values(revoked=True)
    )
    await db.commit()
    _clear_refresh_cookie(response)
    return {"ok": True}


@router.delete("/me")
async def delete_account(
    response: Response,
    db:   AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """GDPR Article 17 — right to erasure. Anonymises PII, cancels Stripe, revokes tokens."""
    from sqlalchemy import update as _upd
    import hashlib as _hl

    # Anonymise all PII fields (one-way hash the email for audit trail without retaining it)
    anon_email = f"deleted_{_hl.sha256(user.email.encode()).hexdigest()[:20]}@deleted.invalid"
    user.email             = anon_email
    user.full_name         = None
    user.password_hash     = ""
    user.telegram_chat_id  = None
    user.telegram_link_code = None
    user.oauth_sub         = None
    user.oauth_provider    = None
    user.email_verify_token = None
    user.is_active         = False

    # Cancel active Stripe subscription
    if user.stripe_subscription_id:
        try:
            import stripe as _stripe
            s = get_settings()
            _stripe.api_key = s.stripe_secret_key
            _stripe.Subscription.delete(user.stripe_subscription_id)
        except Exception:
            pass  # best-effort; subscription will lapse naturally

    # Revoke all refresh tokens
    await db.execute(
        _upd(RefreshToken).where(RefreshToken.user_id == user.id).values(revoked=True)
    )
    await db.commit()
    _clear_refresh_cookie(response)
    log.info(f"[auth] account deletion completed for user id={user.id}")
    return {"ok": True, "message": "Account deleted. All personal data has been anonymised."}


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return user_to_dict(user)


class UpdateMeIn(BaseModel):
    full_name: str | None = None

    @field_validator("full_name")
    @classmethod
    def name_length(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 60:
            raise ValueError("Name must be 60 characters or fewer")
        return v or None


@router.patch("/me")
async def update_me(
    body: UpdateMeIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if body.full_name is not None:
        user.full_name = body.full_name or None
    await db.commit()
    return user_to_dict(user)


@router.post("/change-password")
async def change_password(
    body: ChangePasswordIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(400, "Current password is incorrect.")
    user.password_hash = hash_password(body.new_password)
    await db.commit()
    return {"ok": True}


@router.post("/telegram-link-code")
async def regenerate_telegram_code(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Generate a new one-time Telegram link code for this user."""
    user.telegram_link_code = generate_link_code()
    await db.commit()
    return {"link_code": user.telegram_link_code}


@router.delete("/telegram-unlink")
async def unlink_telegram(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    user.telegram_chat_id = None
    await db.commit()
    return {"ok": True}


@router.post("/forgot-password")
@_limiter.limit("5/minute")
async def forgot_password(request: Request, body: ForgotPasswordIn, db: AsyncSession = Depends(get_db)):
    import time as _t
    email = body.email.lower().strip()
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    # Always return 200 to prevent email enumeration
    if user:
        token = _secrets.token_urlsafe(32)
        now = _t.time()
        _reset_tokens[token] = (email, now + 3600)
        # GC expired entries on every write so the dict stays small
        for k in [k for k, (_, exp) in list(_reset_tokens.items()) if exp < now]:
            del _reset_tokens[k]
        reset_url = f"{get_settings().app_url}/reset-password?token={token}"
        try:
            from services.email_svc import send_password_reset
            await send_password_reset(email, reset_url)
        except Exception as e:
            log.warning(f"[auth] password reset email failed: {e}")
    return {"message": "If that email is registered, a reset link has been sent."}


@router.post("/reset-password")
@_limiter.limit("10/minute")
async def reset_password(request: Request, body: ResetPasswordIn, db: AsyncSession = Depends(get_db)):
    import time as _t
    entry = _reset_tokens.get(body.token)
    if not entry or _t.time() > entry[1]:
        raise HTTPException(400, "Invalid or expired reset token.")
    email, _ = entry
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    if not user:
        raise HTTPException(400, "User not found.")
    if len(body.new_password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters.")
    user.password_hash = hash_password(body.new_password)
    # Revoke all refresh tokens so stolen sessions can't persist after reset
    await db.execute(update(RefreshToken).where(RefreshToken.user_id == user.id).values(revoked=True))
    await db.commit()
    del _reset_tokens[body.token]
    return {"message": "Password reset successfully. Please log in."}


@router.get("/referral")
async def get_referral_info(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Return the user's referral link and stats."""
    s = get_settings()
    referral_url = f"{s.app_url}/signup?ref={user.id}"
    # Count users who signed up via this user's ref
    from sqlalchemy import func as sqlfunc
    result = await db.execute(
        select(sqlfunc.count()).select_from(User).where(User.referred_by == user.id)
    )
    referrals_total = result.scalar() or 0
    rewarded = await db.execute(
        select(sqlfunc.count()).select_from(User).where(
            User.referred_by == user.id, User.referral_rewarded == True
        )
    )
    rewards_claimed = rewarded.scalar() or 0
    return {
        "referral_url": referral_url,
        "referrals_total": referrals_total,
        "rewards_claimed": rewards_claimed,
        "rewards_pending": referrals_total - rewards_claimed,
    }


class SignalPrefsIn(BaseModel):
    min_confidence: float | None = None  # 0–100, or null to reset to global default


@router.patch("/signal-prefs")
async def update_signal_prefs(
    body: SignalPrefsIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Set a personal minimum confidence threshold for Telegram delivery.
    Set to null to revert to the global server default.
    """
    if body.min_confidence is not None and not (0 <= body.min_confidence <= 100):
        raise HTTPException(400, "min_confidence must be between 0 and 100.")
    user.min_confidence_override = body.min_confidence
    await db.commit()
    return {
        "min_confidence_override": user.min_confidence_override,
        "message": (f"Telegram threshold set to {body.min_confidence:.0f}%."
                    if body.min_confidence is not None
                    else "Reverted to global server default."),
    }


# ── Email Verification ────────────────────────────────────────────────────────

@router.get("/verify-email")
async def verify_email(token: str = Query(...), response: Response = None, db: AsyncSession = Depends(get_db)):
    """Verify email address using the token from the verification email."""
    user = (await db.execute(select(User).where(User.email_verify_token == token))).scalar_one_or_none()
    if not user:
        raise HTTPException(400, "Invalid or expired verification token.")
    if user.email_verified:
        raise HTTPException(400, "Email already verified.")
    user.email_verified = True
    user.email_verify_token = None
    await db.commit()
    await db.refresh(user)
    # Send welcome email now that they're verified
    import asyncio
    asyncio.create_task(send_welcome(user.email, user.full_name or ""))
    log.info(f"[auth] email verified {user.email}")
    # Return tokens — log them straight in
    return await _create_tokens(user, db, response)


class IntegrationsIn(BaseModel):
    discord_webhook_url: str | None = None   # Discord channel webhook; None to clear
    webhook_url:         str | None = None   # HMAC-signed outbound webhook; None to clear


@router.patch("/integrations")
async def update_integrations(
    body: IntegrationsIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Set or clear the user's outbound integrations.
    discord_webhook_url: paste a Discord channel webhook URL
        (Manage Channel → Integrations → Create Webhook → Copy Webhook URL).
    webhook_url: any HTTPS endpoint that accepts POST with HMAC-SHA256 signal JSON.
    """
    if body.discord_webhook_url is not None:
        url = body.discord_webhook_url.strip()
        if url and not url.startswith("https://discord.com/api/webhooks/"):
            raise HTTPException(400, "discord_webhook_url must be a Discord webhook URL.")
        user.discord_webhook_url = url or None
    if body.webhook_url is not None:
        url = body.webhook_url.strip()
        if url:
            if not url.startswith("https://"):
                raise HTTPException(400, "webhook_url must start with https://")
            # SSRF guard: block private/link-local/loopback hostnames
            import urllib.parse as _up, ipaddress as _ip
            try:
                parsed_host = _up.urlparse(url).hostname or ""
                try:
                    addr = _ip.ip_address(parsed_host)
                    if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
                        raise HTTPException(400, "webhook_url hostname is not a public address.")
                except ValueError:
                    # Not a raw IP — hostname is fine (DNS resolution happens at delivery time)
                    pass
                if not parsed_host or parsed_host in ("localhost",):
                    raise HTTPException(400, "webhook_url hostname is not allowed.")
            except HTTPException:
                raise
            except Exception:
                raise HTTPException(400, "webhook_url is not a valid URL.")
        user.webhook_url = url or None
    await db.commit()
    return {
        "discord_webhook_url": user.discord_webhook_url,
        "webhook_url":         user.webhook_url,
        "message": "Integrations updated.",
    }


class ResendVerificationIn(BaseModel):
    email: EmailStr


@router.post("/resend-verification")
@_limiter.limit("3/minute")
async def resend_verification(request: Request, body: ResendVerificationIn, db: AsyncSession = Depends(get_db)):
    """Resend the verification email. Body: {email: string}"""
    email = str(body.email).lower().strip()
    if not email:
        raise HTTPException(400, "email required")
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()
    # Always return 200 to avoid email enumeration
    if not user or user.email_verified:
        return {"message": "If an unverified account exists for this email, a new link has been sent."}
    import asyncio, secrets as _sec
    new_token = _sec.token_urlsafe(32)
    user.email_verify_token = new_token
    await db.commit()
    s = get_settings()
    verify_link = f"{s.app_url}/verify-email?token={new_token}"
    asyncio.create_task(send_verification_email(user.email, user.full_name or "", verify_link))
    log.info(f"[auth] resent verification to {user.email}")
    return {"message": "Verification email sent. Check your inbox."}
