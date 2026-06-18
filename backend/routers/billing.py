"""
Billing router — Stripe checkout, webhook, customer portal, subscription status.
All endpoints under /api/billing.
"""

import asyncio
import logging
from datetime import datetime

import stripe
from config import TIER_LABELS, TIER_PLAN_FEATURES, TIER_PRICES_CENTS, get_settings
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from models import StripeEvent, User
from services.auth_svc import get_current_user
from services.signal_quota_svc import apply_signal_quota
from services.email_svc import (
    send_payment_failed,
    send_subscription_canceled,
    send_subscription_confirmed,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger("signal.trade.billing")
router = APIRouter(prefix="/api/billing", tags=["billing"])


PLAN_TIERS = {
    "basic": "basic",
    "pro": "pro",
    "elite": "elite",
}


def _stripe():
    s = get_settings()
    stripe.api_key = s.stripe_secret_key
    return stripe


def _price_id(tier: str) -> str:
    s = get_settings()
    return s.stripe_price_basic if tier == "basic" else s.stripe_price_pro if tier == "pro" else s.stripe_price_elite


# ── Public: pricing info ──────────────────────────────────────────────────────


@router.get("/plans")
async def get_plans():
    plans = [
        {
            "id": "free",
            "name": "Free",
            "price": TIER_PRICES_CENTS["free"],
            "currency": "usd",
            "interval": None,
            "features": TIER_PLAN_FEATURES["free"],
            "cta": "Current plan",
        },
        {
            "id": "basic",
            "name": "Basic",
            "price": TIER_PRICES_CENTS["basic"],
            "currency": "usd",
            "interval": "month",
            "features": TIER_PLAN_FEATURES["basic"],
            "cta": "Start Basic",
        },
        {
            "id": "pro",
            "name": "Pro",
            "price": TIER_PRICES_CENTS["pro"],
            "currency": "usd",
            "interval": "month",
            "features": TIER_PLAN_FEATURES["pro"],
            "cta": "Start Pro",
            "highlight": True,
        },
        {
            "id": "elite",
            "name": "Elite",
            "price": TIER_PRICES_CENTS["elite"],
            "currency": "usd",
            "interval": "month",
            "features": TIER_PLAN_FEATURES["elite"],
            "cta": "Start Elite",
        },
    ]
    return plans


# ── Checkout ──────────────────────────────────────────────────────────────────


@router.post("/checkout/{tier}")
async def create_checkout(
    tier: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if tier not in ("basic", "pro", "elite"):
        raise HTTPException(400, "Invalid plan. Choose 'basic', 'pro', or 'elite'.")

    s = get_settings()
    if not s.stripe_secret_key:
        raise HTTPException(503, "Stripe not configured — set STRIPE_SECRET_KEY in .env")

    price_id = _price_id(tier)
    if not price_id:
        raise HTTPException(503, f"Stripe price ID for '{tier}' not configured.")

    st = _stripe()

    # Create or retrieve Stripe customer
    if not user.stripe_customer_id:
        customer = st.Customer.create(
            email=user.email, name=user.full_name or user.email, metadata={"user_id": user.id}
        )
        user.stripe_customer_id = customer.id
        await db.commit()

    session = st.checkout.Session.create(
        customer=user.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        allow_promotion_codes=True,
        success_url=f"{s.app_url}?sub=success&tier={tier}",
        cancel_url=f"{s.app_url}?sub=cancel",
        metadata={"user_id": str(user.id), "tier": tier},
        subscription_data={
            "trial_period_days": 7,
            "metadata": {"user_id": str(user.id), "tier": tier},
        },
    )
    return {"checkout_url": session.url}


# ── Customer portal (manage / cancel) ────────────────────────────────────────


@router.post("/portal")
async def billing_portal(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    s = get_settings()
    if not s.stripe_secret_key:
        raise HTTPException(503, "Stripe not configured.")
    if not user.stripe_customer_id:
        raise HTTPException(400, "No active subscription to manage.")

    st = _stripe()
    session = st.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=s.app_url,
    )
    return {"portal_url": session.url}


# ── Status ────────────────────────────────────────────────────────────────────


@router.get("/status")
async def billing_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from datetime import timedelta, timezone as _tz

    base = {
        "tier": user.subscription_tier,
        "status": user.subscription_status,
        "period_end": user.subscription_period_end.isoformat() if user.subscription_period_end else None,
        "tier_label": TIER_LABELS.get(user.subscription_tier, "Free"),
        "is_owner": user.is_owner,
        "cancel_at_period_end": False,
        "payment_method": None,
    }

    period_end_dt = user.subscription_period_end
    grace_period_end = None
    cancellation_date = None
    downgrade_date = None

    # Enrich with live Stripe data when keys are configured
    try:
        s = get_settings()
        if s.stripe_secret_key and user.stripe_subscription_id:
            st = _stripe()
            sub = st.Subscription.retrieve(
                user.stripe_subscription_id,
                expand=["default_payment_method"],
            )
            base["cancel_at_period_end"] = sub.get("cancel_at_period_end", False)
            period_end_ts = sub.get("current_period_end")  # Unix timestamp
            if period_end_ts:
                base["period_end"] = period_end_ts
                period_end_dt = datetime.fromtimestamp(period_end_ts, tz=_tz.utc).replace(tzinfo=None)
            pm = sub.get("default_payment_method") or {}
            card = (pm.get("card") or {}) if isinstance(pm, dict) else {}
            if card:
                base["payment_method"] = {
                    "brand": card.get("brand"),
                    "last4": card.get("last4"),
                    "exp_month": card.get("exp_month"),
                    "exp_year": card.get("exp_year"),
                }
    except Exception:
        pass  # return base data if Stripe unreachable

    if period_end_dt:
        if user.subscription_status == "past_due":
            grace_period_end = (period_end_dt + timedelta(days=15)).isoformat()
        if base.get("cancel_at_period_end"):
            cancellation_date = period_end_dt.isoformat()
            downgrade_date = period_end_dt.isoformat()

    base["grace_period_end"] = grace_period_end
    base["cancellation_date"] = cancellation_date
    base["downgrade_date"] = downgrade_date

    quota = await apply_signal_quota(db, user, 0)
    base["signal_quota"] = {
        "limit": quota["limit"],
        "used": quota["quota"].views_count or 0,
        "remaining": quota["remaining"],
        "resets_at": quota["window_start"].isoformat() if quota["window_start"] else None,
    }
    return base


# ── Stripe Webhook ────────────────────────────────────────────────────────────


@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    s = get_settings()

    # Hard-block when no webhook secret is configured: stripe.Webhook.construct_event
    # with an empty secret would raise ValueError, but making this explicit prevents
    # subtle SDK version differences from accidentally accepting unsigned payloads.
    if not s.stripe_webhook_secret:
        log.error("[billing] webhook rejected — STRIPE_WEBHOOK_SECRET not configured")
        raise HTTPException(500, "Webhook not configured")

    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    try:
        st = _stripe()
        event = st.Webhook.construct_event(payload, sig, s.stripe_webhook_secret)
    except Exception as e:
        log.warning(f"[billing] webhook signature failed: {e}")
        raise HTTPException(400, "Invalid signature")

    event_id = event.get("id", "")
    etype = event["type"]
    data = event["data"]["object"]
    log.info(f"[billing] webhook {etype}")

    stripe_event_row = None
    if event_id:
        existing = (await db.execute(select(StripeEvent).where(StripeEvent.event_id == event_id))).scalar_one_or_none()
        if existing:
            existing.is_replay = True
            existing.handler_result = "duplicate_ignored"
            await db.commit()
            return Response(status_code=200)

        cust_id = data.get("customer")
        sub_id = data.get("subscription") or (data.get("id") if data.get("object") == "subscription" else None)
        stripe_event_row = StripeEvent(
            event_id=event_id,
            customer_id=cust_id,
            subscription_id=sub_id,
            event_type=etype,
            is_replay=False,
            handler_result="pending",
        )
        db.add(stripe_event_row)
        await db.commit()

    # Get user state before handler execution
    user_before = None
    cust_id = data.get("customer")
    if cust_id:
        user_before = await _get_user_by_stripe_customer(cust_id, db)
    elif etype == "checkout.session.completed":
        user_id = int(data.get("metadata", {}).get("user_id", 0))
        if user_id:
            user_before = await db.get(User, user_id)

    old_status = user_before.subscription_status if user_before else "unknown"
    old_tier = user_before.subscription_tier if user_before else "unknown"

    handler_result = "success"
    try:
        if etype == "checkout.session.completed":
            await _handle_checkout_completed(data, db)
        elif etype in ("customer.subscription.updated", "customer.subscription.created"):
            await _handle_subscription_updated(data, db)
        elif etype == "customer.subscription.deleted":
            await _handle_subscription_deleted(data, db)
        elif etype == "invoice.payment_failed":
            await _handle_payment_failed(data, db)
    except Exception as e:
        handler_result = f"error: {str(e)}"
        log.exception(f"[billing] error processing webhook {etype}")

    # Record transition and result in database
    if stripe_event_row:
        if user_before:
            await db.refresh(user_before)
            new_status = user_before.subscription_status
            new_tier = user_before.subscription_tier
        else:
            new_status = "unknown"
            new_tier = "unknown"

        stripe_event_row.transition = f"{old_tier}:{old_status} -> {new_tier}:{new_status}"
        stripe_event_row.handler_result = handler_result
        await db.commit()

    if handler_result.startswith("error"):
        raise HTTPException(500, handler_result)

    return {"received": True}


# ── Webhook handlers ──────────────────────────────────────────────────────────


async def _get_user_by_stripe_customer(customer_id: str, db: AsyncSession) -> User | None:
    return (await db.execute(select(User).where(User.stripe_customer_id == customer_id))).scalar_one_or_none()


async def _handle_checkout_completed(session: dict, db: AsyncSession):
    user_id = int(session.get("metadata", {}).get("user_id", 0))
    tier = session.get("metadata", {}).get("tier", "basic")
    if not user_id:
        return
    user = await db.get(User, user_id)
    if not user:
        return
    sub_id = session.get("subscription")
    if sub_id:
        user.stripe_subscription_id = sub_id
    user.subscription_tier = tier
    user.subscription_status = "active"
    await db.commit()
    log.info(f"[billing] checkout completed user={user_id} tier={tier}")

    # Fetch period_end from subscription
    try:
        st = _stripe()
        sub = st.Subscription.retrieve(sub_id)
        from datetime import timezone as _tz

        user.subscription_period_end = datetime.fromtimestamp(sub["current_period_end"], tz=_tz.utc).replace(
            tzinfo=None
        )
        await db.commit()
        period_str = user.subscription_period_end.strftime("%b %d, %Y")
        asyncio.create_task(send_subscription_confirmed(user.email, user.full_name or "", tier, period_str))
    except Exception as e:
        log.warning(f"[billing] period_end fetch failed: {e}")

    # ── Referral reward — apply $29 credit to referrer's Stripe account ─────
    if user.referred_by and not user.referral_rewarded:
        try:
            referrer = await db.get(User, user.referred_by)
            if referrer and referrer.stripe_customer_id:
                _stripe().Customer.create_balance_transaction(
                    referrer.stripe_customer_id,
                    amount=-2900,  # $29 credit — 1 free month of Basic (in cents, negative = credit)
                    currency="usd",
                    description=f"Referral reward — {user.email} converted to {tier}",
                )
                log.info(f"[referral] credited $29 to referrer user={referrer.id} for referee={user.id}")
            else:
                log.info(f"[referral] referrer {user.referred_by} has no Stripe account yet — reward stored pending")
            user.referral_rewarded = True
            await db.commit()
        except Exception as e:
            log.warning(f"[referral] reward failed for referrer={user.referred_by}: {e}")


async def _handle_subscription_updated(sub: dict, db: AsyncSession):
    customer_id = sub.get("customer")
    user = await _get_user_by_stripe_customer(customer_id, db)
    if not user:
        return

    # Determine tier from price
    tier = "basic"
    s = get_settings()
    items = sub.get("items", {}).get("data", [])
    if items:
        price_id = items[0].get("price", {}).get("id", "")
        if price_id == s.stripe_price_pro:
            tier = "pro"

    stripe_status = sub.get("status", "inactive")
    sub_status = (
        "active"
        if stripe_status in ("active", "trialing")
        else ("past_due" if stripe_status == "past_due" else "inactive")
    )
    period_end = sub.get("current_period_end")

    user.subscription_tier = tier if sub_status == "active" else user.subscription_tier
    user.subscription_status = sub_status
    user.stripe_subscription_id = sub.get("id")
    if period_end:
        from datetime import timezone as _tz

        user.subscription_period_end = datetime.fromtimestamp(period_end, tz=_tz.utc).replace(tzinfo=None)
    await db.commit()
    log.info(f"[billing] subscription updated user={user.id} tier={tier} status={sub_status}")


async def _handle_subscription_deleted(sub: dict, db: AsyncSession):
    customer_id = sub.get("customer")
    user = await _get_user_by_stripe_customer(customer_id, db)
    if not user:
        return
    period_end_ts = sub.get("current_period_end")
    from datetime import timezone as _tz

    period_str = datetime.fromtimestamp(period_end_ts, tz=_tz.utc).strftime("%b %d, %Y") if period_end_ts else "soon"
    user.subscription_tier = "free"
    user.subscription_status = "canceled"
    user.stripe_subscription_id = None
    await db.commit()
    log.info(f"[billing] subscription canceled user={user.id}")
    asyncio.create_task(send_subscription_canceled(user.email, user.full_name or "", period_str))


async def _handle_payment_failed(invoice: dict, db: AsyncSession):
    customer_id = invoice.get("customer")
    user = await _get_user_by_stripe_customer(customer_id, db)
    if not user:
        return
    user.subscription_status = "past_due"
    await db.commit()
    log.info(f"[billing] payment failed user={user.id}")
    asyncio.create_task(send_payment_failed(user.email, user.full_name or ""))
