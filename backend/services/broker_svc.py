"""
Broker execution service — per-user Alpaca credential management and
auto-execution of signals.

Credentials are stored Fernet-encrypted in the users table. The
encryption key is derived from JWT_SECRET so no extra env var is needed;
if the JWT secret rotates, users will need to re-enter credentials.
"""

import base64
import hashlib
import logging
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger("broker_svc")

# TSYS-9d: credential encryption key versioning. The primary (current) version is
# used for new encryptions; all versions down to v1 remain valid for decryption,
# so a rotation re-encrypts ciphertexts under the new primary without forcing
# users to re-enter credentials. Bump this to rotate.
_BROKER_KEY_VERSION = 1
_FERNET_CACHE: Optional[MultiFernet] = None

# Portfolio drawdown circuit-breaker: if unrealised P&L drops below this
# fraction of account equity, new auto-executions are blocked for the session.
_DD_BLOCK_THRESHOLD = -0.05  # −5%


def _derive_key(jwt_secret: str, version: int) -> bytes:
    """Derive a Fernet key for a given version. v1 keeps the original
    ":broker-v1" domain separator so pre-versioning ciphertexts still decrypt."""
    raw = hashlib.sha256(f"{jwt_secret}:broker-v{version}".encode()).digest()
    return base64.urlsafe_b64encode(raw)


def _get_fernet() -> MultiFernet:
    """MultiFernet whose first key is the current version (used for encryption)
    and whose remaining keys (older versions) remain valid for decryption."""
    global _FERNET_CACHE
    if _FERNET_CACHE is None:
        from config import get_settings

        jwt_secret = get_settings().jwt_secret_key
        # Newest version first → MultiFernet encrypts with it; older versions
        # follow so existing ciphertexts keep decrypting after a rotation.
        keys = [Fernet(_derive_key(jwt_secret, v)) for v in range(_BROKER_KEY_VERSION, 0, -1)]
        _FERNET_CACHE = MultiFernet(keys)
    return _FERNET_CACHE


def current_key_version() -> int:
    """TSYS-9d: the key version new credentials are encrypted under."""
    return _BROKER_KEY_VERSION


def encrypt_credential(plaintext: str) -> str:
    """Encrypt a broker API key/secret for storage in the DB."""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt_credential(ciphertext: str) -> Optional[str]:
    """Decrypt a broker credential. Returns None if the token is invalid."""
    try:
        return _get_fernet().decrypt(ciphertext.encode()).decode()
    except (InvalidToken, Exception):
        return None


def rotate_credential(ciphertext: str) -> Optional[str]:
    """TSYS-9d: re-encrypt a ciphertext under the current primary key without
    decrypting to plaintext in the caller. Returns None if the token is invalid."""
    try:
        return _get_fernet().rotate(ciphertext.encode()).decode()
    except (InvalidToken, Exception):
        return None


async def verify_alpaca_connection(key: str, secret: str, live: bool) -> dict:
    """
    Verify Alpaca credentials by calling /v2/account.

    Returns the account dict on success, raises ValueError with a
    human-readable message on failure.
    """
    from services import alpaca_rest

    try:
        account = await alpaca_rest.get_account(key, secret, live=live)
    except Exception as e:
        raise ValueError(f"Could not connect to Alpaca: {e}") from e

    if account.get("status") not in ("ACTIVE", "ACCOUNT_UPDATED"):
        raise ValueError(f"Alpaca account status is '{account.get('status')}' — expected ACTIVE")

    return account


async def verify_ibkr_connection(key: str, secret: str, live: bool) -> dict:
    """
    Verify IBKR credentials by calling get_account.
    """
    from services import ibkr_rest

    try:
        account = await ibkr_rest.get_account(key, secret, live=live)
    except Exception as e:
        raise ValueError(f"Could not connect to IBKR: {e}") from e

    return account


async def check_portfolio_drawdown(user, key: str, secret: str, live: bool, broker: str = "alpaca") -> bool:
    """
    RISK-2: Portfolio drawdown circuit-breaker.

    Returns True (block execution) if unrealised P&L / equity < −5%.
    Logs a WARNING and fires a Telegram admin alert on first breach.
    Returns False (allow execution) if below threshold or on any error.
    """
    if broker == "ibkr":
        from services import ibkr_rest as broker_rest
    else:
        from services import alpaca_rest as broker_rest

    try:
        account = await broker_rest.get_account(key, secret, live=live)
        equity = float(account.get("equity") or 1.0)
        unreal_pl = float(account.get("unrealized_pl") or 0.0)
        if equity <= 0:
            return False
        dd_frac = unreal_pl / equity
        if dd_frac < _DD_BLOCK_THRESHOLD:
            log.warning(
                "broker_svc: RISK-2 portfolio DD %.1f%% < %.0f%% threshold — blocking user=%d auto-execute",
                dd_frac * 100,
                _DD_BLOCK_THRESHOLD * 100,
                user.id,
            )
            # Best-effort Telegram admin alert (non-blocking)
            try:
                from services.telegram_svc import send_admin_alert

                await send_admin_alert(
                    f"⚠️ Portfolio DD {dd_frac * 100:.1f}% for user {user.id} "
                    f"(equity ${equity:,.0f}, unreal PL ${unreal_pl:,.0f}) — "
                    "auto-execution paused until DD recovers."
                )
            except Exception:
                pass
            return True
    except Exception as e:
        log.debug("broker_svc: DD check failed for user=%d: %s", user.id, e)
    return False


# Alpaca/IBKR order states mapped onto our BrokerOrder.status vocabulary.
_BROKER_STATUS_MAP = {
    "filled": "filled",
    "partially_filled": "filled",
    "canceled": "canceled",
    "cancelled": "canceled",
    "expired": "canceled",
    "rejected": "rejected",
    "done_for_day": "canceled",
}
# A submitted order with no broker record after this long is flagged as an orphan.
_ORPHAN_AGE_HOURS = 24


async def reconcile_broker_orders(db: AsyncSession) -> dict:
    """TSYS-9a: poll the broker for every pending order, update its status, and
    flag orphans (submitted orders the broker has no record of).

    Returns a summary dict. Never raises: one bad user cannot break the pass.
    """
    from datetime import datetime, timezone

    from sqlalchemy import select

    from models import BrokerOrder, User

    pending = (await db.execute(select(BrokerOrder).where(BrokerOrder.status == "submitted"))).scalars().all()
    summary = {"checked": 0, "updated": 0, "orphaned": 0, "users": 0}
    if not pending:
        return summary

    by_user: dict[int, list] = {}
    for o in pending:
        by_user.setdefault(o.user_id, []).append(o)
    summary["users"] = len(by_user)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    for user_id, orders in by_user.items():
        user = await db.get(User, user_id)
        if user is None or not user.alpaca_key_enc:
            continue
        key = decrypt_credential(user.alpaca_key_enc)
        secret = decrypt_credential(user.alpaca_secret_enc) if user.alpaca_secret_enc else ""
        if not key:
            continue
        broker_type = user.auto_execute_broker or "alpaca"
        live = user.alpaca_account_type == "live"
        if broker_type == "ibkr":
            from services import ibkr_rest as client_rest
        else:
            from services import alpaca_rest as client_rest

        try:
            broker_orders = await client_rest.get_orders(key, secret, status="all", limit=200, live=live)
        except Exception as e:  # pragma: no cover - network failure path
            log.warning("reconcile: user=%d get_orders failed: %s", user_id, e)
            continue

        broker_by_id = {str(b.get("id")): b for b in (broker_orders or []) if b.get("id")}

        for o in orders:
            summary["checked"] += 1
            match = broker_by_id.get(str(o.alpaca_order_id)) if o.alpaca_order_id else None
            if match:
                mapped = _BROKER_STATUS_MAP.get(str(match.get("status", "")).lower())
                if mapped and mapped != o.status:
                    o.status = mapped
                    summary["updated"] += 1
            else:
                age_h = (now - o.created_at).total_seconds() / 3600 if o.created_at else 0
                if age_h >= _ORPHAN_AGE_HOURS:
                    o.status = "orphan"
                    o.error_msg = "reconciliation: no matching broker order found"
                    summary["orphaned"] += 1

    await db.commit()
    log.info("reconcile_broker_orders: %s", summary)
    return summary


async def check_runtime_risk_limits(user, ticker: str, notional: float, db: AsyncSession) -> Optional[str]:
    """TSYS-9b: enforce per-user runtime risk limits before placing an order.

    Returns a human-readable reason string if the order should be BLOCKED, or
    None if it is within limits. Only the limits computable from the local
    broker_orders ledger are enforced here (daily order count, per-ticker daily
    notional); position-count / sector-exposure limits require live broker state
    and are enforced via the drawdown/position path.
    """
    from datetime import datetime, timezone

    from sqlalchemy import func, select

    from models import BrokerOrder

    # Only same-day, non-rejected orders count toward the rolling daily limits.
    day_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    counted = ("submitted", "filled")

    if user.max_daily_orders is not None:
        order_count = (
            await db.execute(
                select(func.count(BrokerOrder.id)).where(
                    BrokerOrder.user_id == user.id,
                    BrokerOrder.created_at >= day_start,
                    BrokerOrder.status.in_(counted),
                )
            )
        ).scalar() or 0
        if order_count >= user.max_daily_orders:
            return f"max_daily_orders reached ({order_count}/{user.max_daily_orders})"

    if user.max_ticker_notional is not None:
        ticker_notional = (
            await db.execute(
                select(func.coalesce(func.sum(BrokerOrder.notional), 0.0)).where(
                    BrokerOrder.user_id == user.id,
                    BrokerOrder.symbol == ticker,
                    BrokerOrder.created_at >= day_start,
                    BrokerOrder.status.in_(counted),
                )
            )
        ).scalar() or 0.0
        if ticker_notional + notional > user.max_ticker_notional:
            return (
                f"max_ticker_notional exceeded for {ticker} "
                f"(${ticker_notional:.0f}+${notional:.0f} > ${user.max_ticker_notional:.0f})"
            )

    return None


async def execute_signal_for_user(
    user,  # models.User
    sig: dict,
    signal_id: Optional[int],
    db: AsyncSession,
) -> None:
    """
    Auto-execute one signal for a user that has auto_execute=True and valid
    broker credentials.

    - Checks portfolio drawdown before executing (RISK-2).
    - Places a notional market order for `auto_execute_qty_dollars` (default $100).
    - Scales the notional by `positionSizeScale` from the signal dict if present.
    - Submits a bracket stop order if `stopPrice` is present in the signal (RISK-1).
    - Records the order (success or error) in the broker_orders table.
    - Never raises: all errors are caught and logged so one bad user can't break
      the delivery loop.
    """
    from models import BrokerOrder

    broker_type = user.auto_execute_broker or "alpaca"

    # IBKR authenticates with a single bearer token (no secret); Alpaca needs both.
    # Mirror broker_connect/broker_status, which store/treat the secret as optional for IBKR.
    if not user.alpaca_key_enc:
        return
    if broker_type != "ibkr" and not user.alpaca_secret_enc:
        return

    key = decrypt_credential(user.alpaca_key_enc)
    secret = decrypt_credential(user.alpaca_secret_enc) if user.alpaca_secret_enc else ""
    if not key or (broker_type != "ibkr" and not secret):
        log.warning("broker_svc: user=%d — credential decryption failed, skipping", user.id)
        return

    live = user.alpaca_account_type == "live"

    # RISK-2: Portfolio drawdown circuit-breaker
    if await check_portfolio_drawdown(user, key, secret, live, broker=broker_type):
        return

    base_notional = user.auto_execute_qty_dollars or 100.0
    scale = float(sig.get("positionSizeScale") or 1.0)
    notional = round(base_notional * scale, 2)
    notional = max(notional, 1.0)  # minimum

    ticker = sig.get("ticker", "")
    action = sig.get("action", "")
    if action not in ("BUY", "SELL"):
        return

    side = "buy" if action == "BUY" else "sell"

    # TSYS-9b: per-user runtime risk limits (daily order count, per-ticker notional).
    _risk_block = await check_runtime_risk_limits(user, ticker, notional, db)
    if _risk_block:
        log.info("broker_svc: user=%d — order blocked by risk limit: %s", user.id, _risk_block)
        return

    if broker_type == "ibkr":
        from services import ibkr_rest as client_rest
    else:
        from services import alpaca_rest as client_rest

    from services.provider_telemetry import current_cycle_id

    order_record = BrokerOrder(
        signal_id=signal_id,
        user_id=user.id,
        broker=broker_type,
        account_type=user.alpaca_account_type or "paper",
        symbol=ticker,
        notional=notional,
        side=side,
        status="submitted",
        cycle_id=current_cycle_id.get(),
    )

    try:
        # RISK-1: Use bracket stop order when stopPrice is available
        stop_price = sig.get("stopPrice") or sig.get("stop")
        target_price = sig.get("targetPrice") or sig.get("target")
        entry_price = sig.get("entry") or sig.get("price")

        if stop_price and float(stop_price) > 0:
            result = await client_rest.submit_bracket_stop_order(
                key,
                secret,
                symbol=ticker,
                notional=notional,
                side=side,
                stop_price=float(stop_price),
                take_profit_price=float(target_price) if target_price else None,
                entry_price=float(entry_price) if entry_price else None,
                live=live,
            )
        else:
            if broker_type == "ibkr":
                result = await client_rest.place_notional_order(
                    key,
                    secret,
                    symbol=ticker,
                    notional=notional,
                    side=side,
                    live=live,
                    entry_price=float(entry_price) if entry_price else None,
                )
            else:
                result = await client_rest.place_notional_order(
                    key,
                    secret,
                    symbol=ticker,
                    notional=notional,
                    side=side,
                    live=live,
                )

        order_id = result.get("id") or result.get("orderId") or result.get("alpaca_order_id") or ""
        order_record.alpaca_order_id = order_id
        order_record.status = result.get("status", "submitted")
        log.info(
            "broker_svc: user=%d %s %s $%.2f stop=%.2f → order_id=%s status=%s",
            user.id,
            side.upper(),
            ticker,
            notional,
            float(stop_price) if stop_price else 0.0,
            order_id,
            order_record.status,
        )
    except Exception as e:
        order_record.status = "error"
        order_record.error_msg = str(e)[:500]
        log.warning("broker_svc: user=%d order failed for %s: %s", user.id, ticker, e)
        # TSYS-10c: broker order-error counter for Prometheus export.
        from services.metrics import inc

        inc("order_error_total", broker=broker_type)

    db.add(order_record)
    # Caller is responsible for committing the session.
