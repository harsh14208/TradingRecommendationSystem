import asyncio
import logging
from datetime import datetime, timezone as _tz
import stripe
from sqlalchemy import select
from config import get_settings
from models import User

log = logging.getLogger("signal.trade.reconciliation")


async def reconcile_stripe_subscriptions(db):
    """
    Nightly Stripe entitlement reconciliation job (TSYS-2a).
    Compares local database subscription state against Stripe.
    """
    s = get_settings()
    if not s.stripe_secret_key:
        log.warning("[reconcile] Stripe is not configured (missing STRIPE_SECRET_KEY)")
        return

    stripe.api_key = s.stripe_secret_key

    # Query all users connected to Stripe
    stmt = select(User).where((User.stripe_customer_id.isnot(None)) | (User.stripe_subscription_id.isnot(None)))
    users = (await db.execute(stmt)).scalars().all()
    log.info(f"[reconcile] Starting Stripe reconciliation for {len(users)} users")

    reconciled_count = 0

    for user in users:
        # Case A: User has a specific subscription ID recorded
        if user.stripe_subscription_id:
            try:
                sub = await asyncio.to_thread(stripe.Subscription.retrieve, user.stripe_subscription_id)

                stripe_status = sub.get("status", "inactive")
                mapped_status = (
                    "active"
                    if stripe_status in ("active", "trialing")
                    else ("past_due" if stripe_status == "past_due" else "inactive")
                )

                tier = "basic"
                items = sub.get("items", {}).get("data", [])
                if items:
                    price_id = items[0].get("price", {}).get("id", "")
                    if price_id == s.stripe_price_pro:
                        tier = "pro"

                mismatch = False
                if user.subscription_status != mapped_status:
                    log.info(
                        f"[reconcile] Status mismatch for user {user.id}: DB={user.subscription_status}, Stripe={mapped_status}"
                    )
                    user.subscription_status = mapped_status
                    mismatch = True

                if mapped_status == "active":
                    expected_tier = tier
                elif mapped_status == "past_due":
                    expected_tier = user.subscription_tier  # Keep current tier during grace period
                else:
                    expected_tier = "free"

                if user.subscription_tier != expected_tier:
                    log.info(
                        f"[reconcile] Tier mismatch for user {user.id}: DB={user.subscription_tier}, Stripe_expected={expected_tier}"
                    )
                    user.subscription_tier = expected_tier
                    mismatch = True

                period_end = sub.get("current_period_end")
                if period_end:
                    expected_period_end = datetime.fromtimestamp(period_end, tz=_tz.utc).replace(tzinfo=None)
                    if (
                        not user.subscription_period_end
                        or abs((user.subscription_period_end - expected_period_end).total_seconds()) > 60
                    ):
                        user.subscription_period_end = expected_period_end
                        mismatch = True

                if mismatch:
                    db.add(user)
                    reconciled_count += 1
                    log.info(f"[reconcile] Corrected subscription details for user={user.id}")

            except stripe.error.InvalidRequestError as e:
                # If subscription does not exist on Stripe, downgrade to free
                if "No such subscription" in str(e):
                    log.warning(
                        f"[reconcile] Stripe subscription {user.stripe_subscription_id} not found for user {user.id}. Downgrading to free."
                    )
                    user.subscription_tier = "free"
                    user.subscription_status = "canceled"
                    user.stripe_subscription_id = None
                    db.add(user)
                    reconciled_count += 1
            except Exception as e:
                log.warning(f"[reconcile] Failed to reconcile user {user.id} subscription: {e}")

        # Case B: User has a customer ID but no subscription ID recorded in DB
        elif user.stripe_customer_id:
            try:
                subs = await asyncio.to_thread(stripe.Subscription.list, customer=user.stripe_customer_id)
                stripe_subs = subs.get("data", [])

                # Look for first active or past_due subscription
                valid_sub = None
                for sub in stripe_subs:
                    if sub.get("status") in ("active", "trialing", "past_due"):
                        valid_sub = sub
                        break

                if valid_sub:
                    sub_status = "active" if valid_sub.get("status") in ("active", "trialing") else "past_due"
                    log.info(
                        f"[reconcile] Found active/past_due Stripe subscription {valid_sub.get('id')} for user {user.id} missing in DB."
                    )
                    user.stripe_subscription_id = valid_sub.get("id")
                    user.subscription_status = sub_status

                    tier = "basic"
                    price_id = valid_sub.get("items", {}).get("data", [{}])[0].get("price", {}).get("id", "")
                    if price_id == s.stripe_price_pro:
                        tier = "pro"

                    if sub_status == "active":
                        user.subscription_tier = tier
                    else:
                        user.subscription_tier = user.subscription_tier if user.subscription_tier != "free" else tier

                    period_end = valid_sub.get("current_period_end")
                    if period_end:
                        user.subscription_period_end = datetime.fromtimestamp(period_end, tz=_tz.utc).replace(
                            tzinfo=None
                        )

                    db.add(user)
                    reconciled_count += 1
                elif user.subscription_tier != "free" and user.subscription_status in ("active", "past_due"):
                    log.info(
                        f"[reconcile] DB says active/past_due for user {user.id} but Stripe has no active subscriptions. Downgrading."
                    )
                    user.subscription_tier = "free"
                    user.subscription_status = "canceled"
                    db.add(user)
                    reconciled_count += 1
            except Exception as e:
                log.warning(f"[reconcile] Failed to check customer subscriptions for user {user.id}: {e}")

    if reconciled_count > 0:
        await db.commit()
    log.info(f"[reconcile] Completed. Reconciled {reconciled_count} users.")
