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
import os
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger("broker_svc")

# TSYS-9d: credential encryption key versioning. The primary (current) version is
# used for new encryptions; all versions down to v1 remain valid for decryption,
# so a rotation re-encrypts ciphertexts under the new primary without forcing
# users to re-enter credentials. Bump this to rotate.
_BROKER_KEY_VERSION = 2
_FERNET_CACHE: Optional[MultiFernet] = None

# Portfolio drawdown circuit-breaker: if unrealised P&L drops below this
# fraction of account equity, new auto-executions are blocked for the session.
_DD_BLOCK_THRESHOLD = -0.05  # −5%


def _derive_key_v1(jwt_secret: str) -> bytes:
    """Legacy v1 KDF (SHA-256) kept for decrypting existing credentials."""
    raw = hashlib.sha256(f"{jwt_secret}:broker-v1".encode()).digest()
    return base64.urlsafe_b64encode(raw)


def _derive_key_v2(jwt_secret: str, salt: bytes) -> bytes:
    """v2 KDF using scrypt with a random per-credential salt."""
    raw = hashlib.scrypt(
        jwt_secret.encode(),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        maxmem=64 * 1024 * 1024,
        dklen=32,
    )
    return base64.urlsafe_b64encode(raw)


def _get_fernet() -> MultiFernet:
    """MultiFernet holding only fixed-key legacy versions (v1) for decryption.
    New encryptions use v2 with a per-credential salt stored alongside the
    ciphertext, so they are not handled through this cache."""
    global _FERNET_CACHE
    if _FERNET_CACHE is None:
        from config import get_settings

        jwt_secret = get_settings().jwt_secret_key
        keys = [Fernet(_derive_key_v1(jwt_secret))]
        _FERNET_CACHE = MultiFernet(keys)
    return _FERNET_CACHE


def current_key_version() -> int:
    """TSYS-9d: the key version new credentials are encrypted under."""
    return _BROKER_KEY_VERSION


def encrypt_credential(plaintext: str) -> str:
    """Encrypt a broker API key/secret for storage in the DB using v2 scrypt KDF."""
    from config import get_settings

    jwt_secret = get_settings().jwt_secret_key
    salt = os.urandom(16)
    key = _derive_key_v2(jwt_secret, salt)
    ct = Fernet(key).encrypt(plaintext.encode())
    salt_b64 = base64.urlsafe_b64encode(salt).decode()
    return f"v2:{salt_b64}:{ct.decode()}"


def decrypt_credential(ciphertext: str) -> Optional[str]:
    """Decrypt a broker credential. Supports v2 (salt-prefixed) and v1 legacy
    tokens. Returns None if the token is invalid."""
    if not ciphertext:
        return None
    try:
        if ciphertext.startswith("v2:"):
            from config import get_settings

            jwt_secret = get_settings().jwt_secret_key
            _, salt_b64, ct = ciphertext.split(":", 2)
            salt = base64.urlsafe_b64decode(salt_b64.encode())
            key = _derive_key_v2(jwt_secret, salt)
            return Fernet(key).decrypt(ct.encode()).decode()
        return _get_fernet().decrypt(ciphertext.encode()).decode()
    except Exception:
        return None


def rotate_credential(ciphertext: str) -> Optional[str]:
    """TSYS-9d: re-encrypt a ciphertext under the current primary key.
    Returns the original ciphertext if it is already current; returns None if
    the token is invalid."""
    if ciphertext.startswith(f"v{current_key_version()}:"):
        return ciphertext
    plaintext = decrypt_credential(ciphertext)
    if plaintext is None:
        return None
    return encrypt_credential(plaintext)


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
    Returns True (fail closed) if equity cannot be fetched or is missing.
    Returns False (allow execution) only when equity is available and drawdown
    is below the threshold.
    """
    if broker == "ibkr":
        from services import ibkr_rest as broker_rest
    else:
        from services import alpaca_rest as broker_rest

    try:
        account = await broker_rest.get_account(key, secret, live=live)
    except Exception as e:
        log.debug("broker_svc: DD check failed for user=%d: %s", user.id, e)
        return True

    equity = account.get("equity")
    if equity is None:
        return True
    equity = float(equity)
    if equity <= 0:
        return True

    unreal_pl = float(account.get("unrealized_pl") or 0.0)
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
                    if mapped == "filled":
                        from services.tca_service import record_fill_tca
                        await record_fill_tca(db, o, match)
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
    scale_raw = sig.get("positionSizeScale")
    scale = float(scale_raw) if scale_raw is not None else 1.0
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

    # QENG-3c: Expected slippage & capacity check
    entry_price = float(sig.get("entry") or sig.get("price") or 1.0)
    from services.tca_service import check_capacity_limits
    blocked, suggested_notional, expected_slip = await check_capacity_limits(
        db, ticker, notional, entry_price
    )
    if blocked:
        log.info("broker_svc: user=%d — order blocked by capacity limits (expected slippage %.1f bps)", user.id, expected_slip)
        return
    if suggested_notional != notional:
        log.info("broker_svc: user=%d — order sized down from %.2f to %.2f due to capacity limits", user.id, notional, suggested_notional)
        notional = suggested_notional

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
        arrival_price=entry_price,
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


async def execute_portfolio_for_user(
    user,
    active_signals: list[dict],
    db: AsyncSession,
) -> None:
    """
    QENG-4a/b/c: Portfolio allocator integration.
    Calculates target allocation weights using HRP, applies risk/TCA limits, and executes orders.
    """
    from typing import List, Dict
    from models import BrokerOrder
    from services.portfolio_allocator import allocate_portfolio

    broker_type = user.auto_execute_broker or "alpaca"

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

    # Fetch total equity from broker to use as capital base
    try:
        if broker_type == "ibkr":
            from services import ibkr_rest as broker_rest
        else:
            from services import alpaca_rest as broker_rest
        account = await broker_rest.get_account(key, secret, live=live)
    except Exception as e:
        log.warning(
            "broker_svc: user=%d — could not fetch account equity, aborting portfolio execution: %s",
            user.id,
            e,
        )
        return

    equity_raw = account.get("equity")
    if equity_raw is None:
        log.warning("broker_svc: user=%d — account equity missing, aborting portfolio execution", user.id)
        return
    equity = float(equity_raw)
    if equity <= 0:
        log.warning(
            "broker_svc: user=%d — account equity non-positive (%.2f), aborting portfolio execution",
            user.id,
            equity,
        )
        return
    total_cash = equity

    # Persist daily equity/PL mark (TSYS-8a / RISK-2 / Drawdown Throttle)
    try:
        from models import PnlDaily
        from sqlalchemy import select
        import datetime

        today = datetime.date.today()
        stmt = select(PnlDaily).where(PnlDaily.user_id == user.id, PnlDaily.date == today)
        res = await db.execute(stmt)
        pnl_row = res.scalar_one_or_none()

        unrealized_pl = float(account.get("unrealized_pl") or 0.0)
        cash = float(account.get("cash") or 0.0)

        if pnl_row:
            pnl_row.equity = equity
            pnl_row.cash = cash
            pnl_row.unrealized_pnl = unrealized_pl
        else:
            pnl_row = PnlDaily(
                user_id=user.id,
                date=today,
                equity=equity,
                cash=cash,
                unrealized_pnl=unrealized_pl,
                realized_pnl=0.0,
                n_positions=len(active_signals),
            )
            db.add(pnl_row)
        await db.flush()
        log.info("broker_svc: user=%d — recorded daily PnL mark: equity=$%.2f", user.id, equity)
    except Exception as mark_err:
        log.warning("broker_svc: user=%d — failed to record daily PnL mark: %s", user.id, mark_err)

    # Call portfolio allocator to get sized orders
    try:
        orders_to_place = await allocate_portfolio(db, user.id, active_signals, total_cash)
    except Exception as e:
        log.error("broker_svc: portfolio allocation failed for user=%d: %s", user.id, e, exc_info=True)
        return

    if not orders_to_place:
        log.info("broker_svc: user=%d — no new orders to place after portfolio allocation", user.id)
        return

    # Map signals list by ticker for stop/target extraction
    sig_map = {s["ticker"]: s for s in active_signals}

    for order in orders_to_place:
        ticker = order["ticker"]
        action = order["action"]
        notional = order["notional"]
        target_weight = order["target_weight"]
        signal_id = order["signal_id"]
        
        side = "buy" if action == "BUY" else "sell"
        sig = sig_map.get(ticker)
        if not sig:
            continue

        # TSYS-9b: per-user risk limits
        _risk_block = await check_runtime_risk_limits(user, ticker, notional, db)
        if _risk_block:
            log.info("broker_svc: user=%d — order blocked by risk limit: %s", user.id, _risk_block)
            continue

        # QENG-3c: Capacity check
        entry_price = float(sig.get("entry") or sig.get("price") or 1.0)
        from services.tca_service import check_capacity_limits
        blocked, suggested_notional, expected_slip = await check_capacity_limits(
            db, ticker, notional, entry_price
        )
        if blocked:
            log.info("broker_svc: user=%d — order blocked by capacity limits (expected slippage %.1f bps)", user.id, expected_slip)
            continue
        if suggested_notional != notional:
            log.info("broker_svc: user=%d — order sized down from %.2f to %.2f due to capacity limits", user.id, notional, suggested_notional)
            notional = suggested_notional

        # Place order
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
            arrival_price=entry_price,
        )

        try:
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
                "broker_svc: user=%d (HRP target weight %s) %s %s $%.2f stop=%.2f → order_id=%s status=%s",
                user.id,
                target_weight,
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
            from services.metrics import inc
            inc("order_error_total", broker=broker_type)

        db.add(order_record)

