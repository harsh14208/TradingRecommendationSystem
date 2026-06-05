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

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger("broker_svc")

_FERNET_CACHE: Optional[Fernet] = None

# Portfolio drawdown circuit-breaker: if unrealised P&L drops below this
# fraction of account equity, new auto-executions are blocked for the session.
_DD_BLOCK_THRESHOLD = -0.05  # −5%


def _get_fernet() -> Fernet:
    global _FERNET_CACHE
    if _FERNET_CACHE is None:
        from config import get_settings

        jwt_secret = get_settings().jwt_secret_key
        # Derive a 32-byte key from JWT_SECRET; the ":broker-v1" suffix
        # domain-separates broker encryption from JWT signing.
        raw = hashlib.sha256((jwt_secret + ":broker-v1").encode()).digest()
        key = base64.urlsafe_b64encode(raw)
        _FERNET_CACHE = Fernet(key)
    return _FERNET_CACHE


def encrypt_credential(plaintext: str) -> str:
    """Encrypt a broker API key/secret for storage in the DB."""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt_credential(ciphertext: str) -> Optional[str]:
    """Decrypt a broker credential. Returns None if the token is invalid."""
    try:
        return _get_fernet().decrypt(ciphertext.encode()).decode()
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


async def check_portfolio_drawdown(user, key: str, secret: str, live: bool) -> bool:
    """
    RISK-2: Portfolio drawdown circuit-breaker.

    Returns True (block execution) if unrealised P&L / equity < −5%.
    Logs a WARNING and fires a Telegram admin alert on first breach.
    Returns False (allow execution) if below threshold or on any error.
    """
    from services import alpaca_rest

    try:
        account = await alpaca_rest.get_account(key, secret, live=live)
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


async def execute_signal_for_user(
    user,  # models.User
    sig: dict,
    signal_id: Optional[int],
    db: AsyncSession,
) -> None:
    """
    Auto-execute one signal for a user that has auto_execute=True and valid
    Alpaca credentials.

    - Checks portfolio drawdown before executing (RISK-2).
    - Places a notional market order for `auto_execute_qty_dollars` (default $100).
    - Scales the notional by `positionSizeScale` from the signal dict if present.
    - Submits a bracket stop order if `stopPrice` is present in the signal (RISK-1).
    - Records the order (success or error) in the broker_orders table.
    - Never raises: all errors are caught and logged so one bad user can't break
      the delivery loop.
    """
    from models import BrokerOrder

    if not user.alpaca_key_enc or not user.alpaca_secret_enc:
        return

    key = decrypt_credential(user.alpaca_key_enc)
    secret = decrypt_credential(user.alpaca_secret_enc)
    if not key or not secret:
        log.warning("broker_svc: user=%d — credential decryption failed, skipping", user.id)
        return

    live = user.alpaca_account_type == "live"

    # RISK-2: Portfolio drawdown circuit-breaker
    if await check_portfolio_drawdown(user, key, secret, live):
        return

    base_notional = user.auto_execute_qty_dollars or 100.0
    scale = float(sig.get("positionSizeScale") or 1.0)
    notional = round(base_notional * scale, 2)
    notional = max(notional, 1.0)  # Alpaca minimum

    ticker = sig.get("ticker", "")
    action = sig.get("action", "")
    if action not in ("BUY", "SELL"):
        return

    side = "buy" if action == "BUY" else "sell"

    from services import alpaca_rest

    order_record = BrokerOrder(
        signal_id=signal_id,
        user_id=user.id,
        broker="alpaca",
        account_type=user.alpaca_account_type or "paper",
        symbol=ticker,
        notional=notional,
        side=side,
        status="submitted",
    )

    try:
        # RISK-1: Use bracket stop order when stopPrice is available
        stop_price = sig.get("stopPrice") or sig.get("stop")
        target_price = sig.get("targetPrice") or sig.get("target")
        entry_price = sig.get("entry") or sig.get("price")

        if stop_price and float(stop_price) > 0:
            result = await alpaca_rest.submit_bracket_stop_order(
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
            result = await alpaca_rest.place_notional_order(
                key,
                secret,
                symbol=ticker,
                notional=notional,
                side=side,
                live=live,
            )

        alpaca_id = result.get("id", "")
        order_record.alpaca_order_id = alpaca_id
        order_record.status = result.get("status", "submitted")
        log.info(
            "broker_svc: user=%d %s %s $%.2f stop=%.2f → alpaca_id=%s status=%s",
            user.id,
            side.upper(),
            ticker,
            notional,
            float(stop_price) if stop_price else 0.0,
            alpaca_id,
            order_record.status,
        )
    except Exception as e:
        order_record.status = "error"
        order_record.error_msg = str(e)[:500]
        log.warning("broker_svc: user=%d order failed for %s: %s", user.id, ticker, e)

    db.add(order_record)
    # Caller is responsible for committing the session.
