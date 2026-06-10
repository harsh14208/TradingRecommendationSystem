"""
Auth router — register, login, refresh, me, logout, Telegram link code.
All endpoints are under /api/auth.
"""

import hashlib
import logging
import secrets as _secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, EmailStr, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

_limiter = Limiter(key_func=get_remote_address)

from config import get_settings
from database import get_db
from models import (
    PasswordResetToken,
    RefreshToken,
    User,
    AuthAuditLog,
    EmailChangeRequest,
    SignalDelivery,
    PushSubscription,
    PriceAlert,
    SignalAlert,
)
from services.auth_svc import (
    create_access_token,
    generate_link_code,
    generate_refresh_token,
    get_current_user,
    hash_password,
    user_to_dict,
    verify_password,
)
from services.email_svc import send_verification_email, send_welcome

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
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
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


class ChangeEmailIn(BaseModel):
    new_email: str

    @field_validator("new_email")
    @classmethod
    def email_format(cls, v: str) -> str:
        import re

        v = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Invalid email address")
        if len(v) > 254:
            raise ValueError("Email address too long")
        return v


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# ── Helpers ───────────────────────────────────────────────────────────────────


def _utcnow_naive() -> datetime:
    """UTC timestamp compatible with existing naive SQLAlchemy DateTime columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _set_refresh_cookie(response: Response, token: str):
    s = get_settings()
    response.set_cookie(
        REFRESH_COOKIE,
        token,
        httponly=True,
        samesite="lax",
        secure=get_settings().app_url.startswith("https"),
        max_age=s.refresh_token_expire_days * 86400,
        path="/api/auth/refresh-cookie",
    )


def _clear_refresh_cookie(response: Response):
    response.delete_cookie(REFRESH_COOKIE, path="/api/auth/refresh-cookie")


async def _create_tokens(user: User, db: AsyncSession, response: Response, request: Request = None) -> dict:
    s = get_settings()
    access = create_access_token(user.id, user.subscription_tier, user.is_owner)
    raw_refresh, hashed_refresh = generate_refresh_token()
    expire = _utcnow_naive() + timedelta(days=s.refresh_token_expire_days)

    user_agent = request.headers.get("user-agent") if request else None
    ip_address = request.client.host if request and request.client else None

    db.add(
        RefreshToken(
            user_id=user.id, token_hash=hashed_refresh, expires_at=expire, user_agent=user_agent, ip_address=ip_address
        )
    )
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
    ref: int | None = Query(None),  # ?ref=<user_id> referral tracking
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
    smtp_ready = bool(s.smtp_host and s.smtp_user)
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
        return await _create_tokens(user, db, response, request)

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

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    if user:
        if user.lockout_until and user.lockout_until > _utcnow_naive():
            db.add(
                AuthAuditLog(
                    user_id=user.id,
                    email=email,
                    event="lockout_active_rejected",
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
            )
            await db.commit()
            raise HTTPException(401, "Account temporarily locked. Please try again later.")

    if not user or not verify_password(body.password, user.password_hash):
        if user:
            attempts = (user.failed_login_attempts or 0) + 1
            user.failed_login_attempts = attempts
            if attempts >= 5:
                user.lockout_until = _utcnow_naive() + timedelta(minutes=15)
                db.add(
                    AuthAuditLog(
                        user_id=user.id,
                        email=email,
                        event="lockout_triggered",
                        ip_address=ip_address,
                        user_agent=user_agent,
                    )
                )
                log.warning(f"[auth] lockout triggered for {email}")
            else:
                db.add(
                    AuthAuditLog(
                        user_id=user.id, email=email, event="failed_login", ip_address=ip_address, user_agent=user_agent
                    )
                )
            await db.commit()
        else:
            db.add(
                AuthAuditLog(
                    user_id=None,
                    email=email,
                    event="failed_login_nonexistent_user",
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
            )
            await db.commit()
        raise HTTPException(401, "Invalid email or password.")

    if not user.is_active:
        raise HTTPException(403, "Account disabled. Contact support.")
    if not user.email_verified:
        raise HTTPException(
            403,
            detail={
                "code": "email_unverified",
                "message": "Please verify your email before logging in. Check your inbox or request a new link.",
            },
        )

    user.failed_login_attempts = 0
    user.lockout_until = None
    user.last_seen_at = _utcnow_naive()

    db.add(
        AuthAuditLog(
            user_id=user.id, email=email, event="successful_login", ip_address=ip_address, user_agent=user_agent
        )
    )
    await db.commit()

    log.info(f"[auth] login {user.email}")
    return await _create_tokens(user, db, response, request)


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
    now = _utcnow_naive()
    token_row = (
        await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == hashed,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > now,
            )
        )
    ).scalar_one_or_none()
    if not token_row:
        _clear_refresh_cookie(response)
        raise HTTPException(401, "Invalid or expired refresh token.")

    user = await db.get(User, token_row.user_id)
    if not user or not user.is_active:
        raise HTTPException(401, "Account not found.")

    # Rotate: revoke old, issue new
    token_row.revoked = True
    user.last_seen_at = now
    return await _create_tokens(user, db, response, request)


@router.post("/logout")
async def logout(response: Response, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    # Revoke all refresh tokens for this user
    from sqlalchemy import update

    await db.execute(update(RefreshToken).where(RefreshToken.user_id == user.id).values(revoked=True))
    await db.commit()
    _clear_refresh_cookie(response)
    return {"ok": True}


@router.delete("/me")
async def delete_account(
    response: Response,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """GDPR Article 17 — right to erasure. Anonymises PII, cancels Stripe, revokes tokens, and cleans up user data."""
    import hashlib as _hl

    from sqlalchemy import update as _upd

    # Anonymise all PII fields (one-way hash the email for audit trail without retaining it)
    anon_email = f"deleted_{_hl.sha256(user.email.encode()).hexdigest()[:20]}@deleted.invalid"
    user.email = anon_email
    user.full_name = None
    user.password_hash = ""
    user.telegram_chat_id = None
    user.telegram_link_code = None
    user.oauth_sub = None
    user.oauth_provider = None
    user.email_verify_token = None
    user.is_active = False
    # Clear outbound integrations and broker credentials
    user.webhook_url = None
    user.discord_webhook_url = None
    user.webhook_secret = None
    user.alpaca_key_enc = None
    user.alpaca_secret_enc = None
    user.alpaca_account_type = None
    user.alpaca_key_version = 1
    user.auto_execute = False
    user.auto_execute_broker = None
    user.auto_execute_min_conf = None
    user.auto_execute_qty_dollars = None

    # Cancel active Stripe subscription at period end to preserve paid time
    if user.stripe_subscription_id:
        try:
            import stripe as _stripe

            s = get_settings()
            _stripe.api_key = s.stripe_secret_key.get_secret_value()
            _stripe.Subscription.modify(user.stripe_subscription_id, cancel_at_period_end=True)
            log.info(f"[auth] marked Stripe subscription {user.stripe_subscription_id} cancel_at_period_end for user id={user.id}")
        except Exception as e:
            log.warning(f"[auth] Stripe cancellation failed for user id={user.id}: {e}")

    # Revoke all refresh tokens
    await db.execute(_upd(RefreshToken).where(RefreshToken.user_id == user.id).values(revoked=True))

    # Delete associated user data covered by GDPR
    await db.execute(delete(SignalDelivery).where(SignalDelivery.user_id == user.id))
    await db.execute(delete(PushSubscription).where(PushSubscription.user_id == user.id))
    await db.execute(delete(PriceAlert).where(PriceAlert.user_id == user.id))
    await db.execute(delete(SignalAlert).where(SignalAlert.user_id == user.id))
    await db.execute(delete(AuthAuditLog).where(AuthAuditLog.user_id == user.id))
    await db.execute(delete(EmailChangeRequest).where(EmailChangeRequest.user_id == user.id))

    await db.commit()
    _clear_refresh_cookie(response)
    log.info(f"[auth] account deletion completed for user id={user.id}")
    return {"ok": True, "message": "Account deleted. All personal data has been anonymised."}


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return user_to_dict(user)


_VALID_BROKERS = {"alpaca", "ibkr"}


class UpdateMeIn(BaseModel):
    full_name: str | None = None
    auto_execute: bool | None = None
    auto_execute_min_conf: float | None = None  # 50–100, or null to reset to 75
    auto_execute_broker: str | None = None  # "alpaca" | "ibkr" | "" to clear

    @field_validator("full_name")
    @classmethod
    def name_length(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 60:
            raise ValueError("Name must be 60 characters or fewer")
        return v or None

    @field_validator("auto_execute_min_conf")
    @classmethod
    def conf_range(cls, v: float | None) -> float | None:
        if v is not None and not (50.0 <= v <= 100.0):
            raise ValueError("auto_execute_min_conf must be between 50 and 100")
        return v

    @field_validator("auto_execute_broker")
    @classmethod
    def broker_valid(cls, v: str | None) -> str | None:
        if v is not None and v != "" and v not in _VALID_BROKERS:
            raise ValueError(f"auto_execute_broker must be one of {sorted(_VALID_BROKERS)}")
        return v or None


@router.patch("/me")
async def update_me(
    body: UpdateMeIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if body.full_name is not None:
        user.full_name = body.full_name or None
    if body.auto_execute is not None:
        user.auto_execute = body.auto_execute
    if body.auto_execute_min_conf is not None:
        user.auto_execute_min_conf = body.auto_execute_min_conf
    elif body.auto_execute_min_conf == 0:  # explicit null reset
        user.auto_execute_min_conf = None
    if body.auto_execute_broker is not None:
        user.auto_execute_broker = body.auto_execute_broker or None
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
    email = body.email.lower().strip()
    user = (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Always return 200 to prevent email enumeration
    if user:
        token = _secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        expires = now + timedelta(hours=1)
        # Invalidate prior reset tokens for this email before issuing a new one
        await db.execute(
            update(PasswordResetToken)
            .where(PasswordResetToken.email == email, PasswordResetToken.used == False)
            .values(used=True)
        )
        db.add(
            AuthAuditLog(
                user_id=user.id,
                email=email,
                event="forgot_password_request",
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )
        db.add(PasswordResetToken(token_hash=_hash_token(token), email=email, expires_at=expires))
        await db.commit()
        reset_url = f"{get_settings().app_url}/reset-password?token={token}"
        try:
            from services.email_svc import send_password_reset

            await send_password_reset(email, reset_url)
        except Exception as e:
            log.warning(f"[auth] password reset email failed: {e}")
    else:
        db.add(
            AuthAuditLog(
                user_id=None,
                email=email,
                event="forgot_password_request_nonexistent_user",
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )
        await db.commit()
    return {"message": "If that email is registered, a reset link has been sent."}


@router.post("/reset-password")
@_limiter.limit("10/minute")
async def reset_password(request: Request, body: ResetPasswordIn, db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    row = (
        await db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == _hash_token(body.token),
                PasswordResetToken.used == False,
                PasswordResetToken.expires_at > now,
            )
        )
    ).scalar_one_or_none()
    if not row:
        db.add(
            AuthAuditLog(
                user_id=None,
                email="unknown",
                event="failed_password_reset_invalid_token",
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )
        await db.commit()
        raise HTTPException(400, "Invalid or expired reset token.")
    user = (await db.execute(select(User).where(User.email == row.email))).scalar_one_or_none()
    if not user:
        raise HTTPException(400, "User not found.")
    # Validation is handled by ResetPasswordIn validator; keep a defensive fallback.
    if len(body.new_password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters.")
    user.password_hash = hash_password(body.new_password)
    row.used = True

    # Reset lockouts on successful reset
    user.failed_login_attempts = 0
    user.lockout_until = None

    db.add(
        AuthAuditLog(
            user_id=user.id,
            email=user.email,
            event="successful_password_reset",
            ip_address=ip_address,
            user_agent=user_agent,
        )
    )

    # Revoke all refresh tokens so stolen sessions can't persist after reset
    await db.execute(update(RefreshToken).where(RefreshToken.user_id == user.id).values(revoked=True))
    await db.commit()
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

    result = await db.execute(select(sqlfunc.count()).select_from(User).where(User.referred_by == user.id))
    referrals_total = result.scalar() or 0
    rewarded = await db.execute(
        select(sqlfunc.count()).select_from(User).where(User.referred_by == user.id, User.referral_rewarded == True)
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
        "message": (
            f"Telegram threshold set to {body.min_confidence:.0f}%."
            if body.min_confidence is not None
            else "Reverted to global server default."
        ),
    }


# ── Email Verification ────────────────────────────────────────────────────────


@router.get("/verify-email")
@_limiter.limit("10/minute")
async def verify_email(request: Request, response: Response, token: str = Query(...), db: AsyncSession = Depends(get_db)):
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
    discord_webhook_url: str | None = None  # Discord channel webhook; None to clear
    webhook_url: str | None = None  # HMAC-signed outbound webhook; None to clear


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
            import ipaddress as _ip
            import urllib.parse as _up

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
        "webhook_url": user.webhook_url,
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
    import asyncio
    import secrets as _sec

    new_token = _sec.token_urlsafe(32)
    user.email_verify_token = new_token
    await db.commit()
    s = get_settings()
    verify_link = f"{s.app_url}/verify-email?token={new_token}"
    asyncio.create_task(send_verification_email(user.email, user.full_name or "", verify_link))
    log.info(f"[auth] resent verification to {user.email}")
    return {"message": "Verification email sent. Check your inbox."}


# ── Device/Session Management & Security ──────────────────────────────────────


class SessionResponse(BaseModel):
    id: int
    created_at: datetime
    expires_at: datetime
    user_agent: str | None
    ip_address: str | None
    is_current: bool


@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all active refresh token sessions for the authenticated user."""
    now = _utcnow_naive()
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user.id, RefreshToken.revoked == False, RefreshToken.expires_at > now
        )
    )
    tokens = result.scalars().all()

    current_raw = request.cookies.get(REFRESH_COOKIE)
    current_hash = hashlib.sha256(current_raw.encode()).hexdigest() if current_raw else None

    sessions = []
    for t in tokens:
        sessions.append(
            SessionResponse(
                id=t.id,
                created_at=t.created_at,
                expires_at=t.expires_at,
                user_agent=t.user_agent,
                ip_address=t.ip_address,
                is_current=(current_hash == t.token_hash),
            )
        )
    return sessions


@router.post("/sessions/revoke/{session_id}")
async def revoke_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Revoke a specific active refresh token session."""
    token = await db.get(RefreshToken, session_id)
    if not token or token.user_id != user.id:
        raise HTTPException(404, "Session not found.")

    token.revoked = True
    await db.commit()
    return {"message": "Session successfully revoked."}


@router.post("/sessions/revoke-others")
async def revoke_other_sessions(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Revoke all refresh token sessions except the current one."""
    current_raw = request.cookies.get(REFRESH_COOKIE)
    current_hash = hashlib.sha256(current_raw.encode()).hexdigest() if current_raw else None

    if not current_hash:
        raise HTTPException(400, "Current session token not found in cookies.")

    # Revoke all other active refresh tokens
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user.id, RefreshToken.token_hash != current_hash, RefreshToken.revoked == False)
        .values(revoked=True)
    )
    await db.commit()
    return {"message": "All other sessions successfully revoked."}


# ── Email Change with Confirmation ───────────────────────────────────────────


@router.post("/change-email")
@_limiter.limit("3/minute")
async def request_change_email(
    request: Request,
    body: ChangeEmailIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Request an email change. Generates token and sends verification to the new email."""
    new_email = body.new_email.lower().strip()
    if new_email == user.email:
        raise HTTPException(400, "New email must be different from current email.")

    # Check if new email already exists
    existing = (await db.execute(select(User).where(User.email == new_email))).scalar_one_or_none()
    if existing:
        raise HTTPException(400, "Email address already registered.")

    token = _secrets.token_urlsafe(32)
    expires = _utcnow_naive() + timedelta(hours=2)

    # Invalidate old requests
    await db.execute(delete(EmailChangeRequest).where(EmailChangeRequest.user_id == user.id))

    db.add(
        EmailChangeRequest(
            user_id=user.id,
            old_email=user.email,
            new_email=new_email,
            token_hash=_hash_token(token),
            expires_at=expires,
        )
    )
    await db.commit()

    confirm_url = f"{get_settings().app_url}/api/auth/confirm-email-change?token={token}"
    try:
        from services.email_svc import send_verification_email

        await send_verification_email(new_email, user.full_name or "User", confirm_url)
        log.info(f"[auth] email change requested from {user.email} to {new_email}")
    except Exception as e:
        log.warning(f"[auth] email change confirmation send failed: {e}")

    return {"message": "A confirmation link has been sent to your new email address."}


@router.get("/confirm-email-change")
async def confirm_email_change(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Confirm the email change using the token sent to the new email address."""
    from fastapi.responses import RedirectResponse

    now = _utcnow_naive()
    row = (
        await db.execute(
            select(EmailChangeRequest).where(
                EmailChangeRequest.token_hash == _hash_token(token), EmailChangeRequest.expires_at > now
            )
        )
    ).scalar_one_or_none()

    if not row:
        return RedirectResponse(f"{get_settings().app_url}/login?error=invalid_email_change_token")

    user = await db.get(User, row.user_id)
    if not user:
        return RedirectResponse(f"{get_settings().app_url}/login?error=user_not_found")

    # Double check new email is not occupied
    existing = (await db.execute(select(User).where(User.email == row.new_email))).scalar_one_or_none()
    if existing:
        return RedirectResponse(f"{get_settings().app_url}/login?error=email_already_registered")

    old_email = user.email
    user.email = row.new_email

    # Audit log
    db.add(
        AuthAuditLog(
            user_id=user.id,
            email=row.new_email,
            event="email_changed",
            ip_address=None,
            user_agent="email_change_confirmation",
        )
    )

    await db.delete(row)

    # Invalidate all sessions — require re-login after email change
    await db.execute(update(RefreshToken).where(RefreshToken.user_id == user.id).values(revoked=True))
    await db.commit()

    log.info(f"[auth] email changed successfully for user {user.id} from {old_email} to {row.new_email}")

    return RedirectResponse(f"{get_settings().app_url}/login?email_changed=success")


# ── Admin Account Unlock ──────────────────────────────────────────────────────


@router.post("/unlock")
async def unlock_user(
    email: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Admin unlock endpoint. Only owners/admins can unlock accounts."""
    if not current_user.is_owner:
        raise HTTPException(403, "Forbidden: Only owners/admins can unlock accounts.")

    target_user = (await db.execute(select(User).where(User.email == email.lower().strip()))).scalar_one_or_none()
    if not target_user:
        raise HTTPException(404, "User not found.")

    target_user.failed_login_attempts = 0
    target_user.lockout_until = None

    db.add(
        AuthAuditLog(
            user_id=current_user.id,
            email=email.lower().strip(),
            event="admin_unlock",
            ip_address=None,
            user_agent="system/admin",
        )
    )
    await db.commit()

    log.info(f"[auth] user {email} unlocked by admin {current_user.email}")
    return {"message": f"User {email} has been successfully unlocked."}
