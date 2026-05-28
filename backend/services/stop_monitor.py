"""
Intraday stop/target monitor.

Runs every 30 minutes during market hours (Mon–Fri 09:30–16:15 ET).
Checks every active sent BUY/SELL signal against the latest price:
  - If price breaches the stop  → mark hit_stop, exit_type='stop',  notify via Telegram
  - If price breaches the target → mark hit_target, exit_type='target', notify via Telegram

Deactivates the signal after either event so users aren't notified twice.
"""

import asyncio
import logging
import math
from datetime import datetime, timezone

import yfinance as yf
from sqlalchemy import select

log = logging.getLogger("signal.trade.stop_monitor")


def _fetch_current_prices(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" not in data.columns:
            return {}
        close = data["Close"]
        last = close.iloc[-1]
        if hasattr(last, "items"):
            for t, p in last.items():
                if p and not math.isnan(float(p)):
                    prices[str(t)] = float(p)
        else:
            if tickers and not math.isnan(float(last)):
                prices[tickers[0]] = float(last)
        return prices
    except Exception as e:
        log.warning(f"[stop_monitor] price fetch error: {e}")
        return {}


async def _send_stop_target_notification(
    ticker: str, action: str, event: str, price: float, level: float, ret_pct: float, signal_id: int
):
    """Send Telegram notification when stop or target is hit."""
    try:
        from config import get_settings

        from services.market_data import COMPANY_NAMES
        from services.telegram_svc import send_telegram_message

        settings = get_settings()
        emoji = "✅" if event == "target" else "⛔"
        color_word = "TARGET HIT" if event == "target" else "STOP HIT"
        sign = "+" if ret_pct >= 0 else ""
        company = COMPANY_NAMES.get(ticker, "")
        name_part = f" ({company})" if company and company != ticker else ""
        msg = (
            f"{emoji} <b>{color_word}: {action} {ticker}{name_part}</b>\n"
            f"Price: <b>${price:.2f}</b> → {'above' if event == 'target' else 'below'} "
            f"{'target' if event == 'target' else 'stop'} ${level:.2f}\n"
            f"Return: <b>{sign}{ret_pct:.2f}%</b>\n"
            f"Signal #{signal_id} closed."
        )
        await send_telegram_message(settings.telegram_chat_id, msg, parse_mode="HTML")
    except Exception as e:
        log.warning(f"[stop_monitor] notification error: {e}")


async def check_stop_targets_and_notify():
    """
    Main stop/target monitoring job.
    Called every 30 minutes during market hours from the scanner loop.
    """
    from database import AsyncSessionLocal
    from models import Signal

    log.info("[stop_monitor] checking active signals for stop/target hits…")

    async with AsyncSessionLocal() as db:
        # Only check active, sent BUY/SELL signals with defined stop/target and no exit yet
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.is_active == True,
                        Signal.action.in_(["BUY", "SELL"]),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.exit_type.is_(None),  # not yet resolved
                    )
                )
            )
            .scalars()
            .all()
        )

    if not rows:
        log.info("[stop_monitor] no active signals to check.")
        return

    tickers = list({s.ticker for s in rows})
    prices = _fetch_current_prices(tickers)
    log.info(f"[stop_monitor] got prices for {len(prices)}/{len(tickers)} tickers.")

    now_utc = datetime.now(timezone.utc)
    updated = 0

    async with AsyncSessionLocal() as db:
        for sig in rows:
            current = prices.get(sig.ticker)
            if not current:
                continue

            entry = sig.entry
            stop = sig.stop
            target = sig.target
            is_buy = sig.action == "BUY"

            hit_stop = (current <= stop) if is_buy else (current >= stop)
            hit_target = (current >= target) if is_buy else (current <= target)

            if not hit_stop and not hit_target:
                continue

            event = "target" if hit_target else "stop"
            level = target if hit_target else stop

            # Compute return at the exit level (stop or target price), not at `current`.
            # Using the level price ensures outcome_pct reflects what you'd receive if
            # filled at the order level, not at a potentially worse slippage price.
            # For a stop hit: level == stop < entry (BUY) → negative return (real loss).
            # Always overwrite outcome_pct — do NOT use `or` to preserve an earlier
            # calendar value. A closed position's P&L is locked at exit price, not 7d mark.
            if entry and entry > 0:
                raw_ret = (level - entry) / entry * 100
                ret_pct = round(raw_ret if is_buy else -raw_ret, 2)
            else:
                ret_pct = 0.0

            # Update DB
            sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
            if not sig_db:
                continue

            sig_db.hit_stop = hit_stop
            sig_db.hit_target = hit_target
            sig_db.exit_type = event
            sig_db.is_active = False  # position closed — deactivate signal
            sig_db.outcome_pct = ret_pct  # always lock to exit-level return
            updated += 1

            # Fire Telegram notification (async, non-blocking)
            asyncio.create_task(
                _send_stop_target_notification(sig.ticker, sig.action, event, current, level, ret_pct, sig.id)
            )
            log.info(
                f"[stop_monitor] {sig.ticker} {sig.action} {event.upper()} "
                f"@ ${current:.2f} (level ${level:.2f}) ret={ret_pct:+.2f}%"
            )

        await db.commit()

    log.info(f"[stop_monitor] resolved {updated} signals.")
