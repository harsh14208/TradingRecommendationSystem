"""Daily options VRP scan hook for the live stock scanner.

Called by ``services.scanner._run_scan_impl`` after stock signals are persisted.
It fuses the freshly generated directional stock view with the Massive options
panel, runs the VRP scorer for each configured universe, and persists option
signals as separate rows in the ``signals`` table.

The scorer is CPU-bound (XGB/pandas) and uses its own async DB/Polygon calls, so
it runs in isolated subprocesses to avoid blocking the scanner loop and to avoid
asyncpg pool contamination.
"""

from __future__ import annotations

import asyncio
import json
import logging
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import update

from database import AsyncSessionLocal
from models import Signal
from services.options_chain_resolver import fetch_option_chain
from services.options_engine import (
    _OPTION_ACTIONS,
    _build_option_legs,
    _nearest_monthly_expiry,
    book_to_signal_dicts,
)
from services.options_universe import OPTIONS_UNIVERSE

log = logging.getLogger("signal.options_scanner")

# Run the options scan at most once per calendar day.  The Massive panel is EOD,
# so a single daily signal set is the right frequency; re-running every 15-minute
# stock scan would be wasteful and would perturb the book with identical rows.
_last_options_scan_date: date | None = None

_OPTIONS_UNIVERSES = ["companies", "etf", "index"]

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_BACKEND_DIR = _PROJECT_ROOT / "backend"
_PYTHON = _PROJECT_ROOT / ".venv311" / "bin" / "python"


def _build_direction_df(stock_signals: list[dict]) -> pd.DataFrame:
    """Map the stock scanner's signal dicts to the direction view the VRP engine expects."""
    rows: list[dict] = []
    for s in stock_signals:
        if s.get("action") not in {"BUY", "SELL"}:
            continue
        rows.append(
            {
                "ticker": s["ticker"],
                "dir_action": s["action"],
                "dir_confidence": s.get("confidence"),
                "dir_score": s.get("raw_score"),
                "dir_entry": s.get("entry"),
                "dir_stop": s.get("stop"),
                "dir_target": s.get("target"),
                "days_to_earnings": s.get("daysToEarnings"),
                "next_earnings_date": s.get("nextEarningsDate"),
            }
        )
    return pd.DataFrame(rows)


async def _score_one_universe(universe: str, direction_df: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    """Run the scorer for one universe in a clean subprocess."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        direction_path = tmp / "direction.parquet"
        summary_path = tmp / "summary.json"
        book_path = tmp / "book.parquet"
        direction_df.to_parquet(direction_path, index=False)

        cmd = [
            str(_PYTHON),
            "-m",
            "services.options_engine_worker",
            "--universe",
            universe,
            "--direction-parquet",
            str(direction_path),
            "--output-summary",
            str(summary_path),
            "--output-book",
            str(book_path),
        ]
        log.info("Starting options scorer subprocess: %s", " ".join(cmd))
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(_BACKEND_DIR),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=900)
        if proc.returncode != 0:
            raise RuntimeError(
                f"Options scorer for {universe} failed (rc={proc.returncode}):\n"
                f"{stderr.decode('utf-8', errors='replace')[-2000:]}"
            )
        log.info("Options scorer for %s finished\n%s", universe, stdout.decode("utf-8", errors="replace")[-1000:])

        summary = json.loads(summary_path.read_text())
        book = pd.read_parquet(book_path)
        return summary, book


async def _resolve_book_legs(book: pd.DataFrame, summary: dict) -> pd.DataFrame:
    """Rebuild option legs using real Polygon chain snapshots when available."""
    if book.empty:
        return book

    as_of = date.fromisoformat(summary.get("as_of", datetime.utcnow().date().isoformat()))
    expiry = _nearest_monthly_expiry(as_of, min_days=max(2 + 5, 14))

    action_mask = book["action"].isin(_OPTION_ACTIONS)
    tickers = book.loc[action_mask, "ticker"].unique().tolist()

    chain_map: dict[str, list] = {}

    async def _fetch(ticker: str) -> None:
        try:
            chain_map[ticker] = await fetch_option_chain(ticker, expiry=expiry)
        except Exception:
            log.exception("Failed to fetch option chain for %s", ticker)
            chain_map[ticker] = []

    await asyncio.gather(*(_fetch(t) for t in tickers))

    def _rebuild(row: pd.Series) -> list[dict[str, Any]]:
        if row["action"] not in _OPTION_ACTIONS:
            return row.get("option_legs", [])
        chain = chain_map.get(row["ticker"]) or []
        return _build_option_legs(row, expiry, chain=chain)

    book = book.copy()
    book["option_legs"] = book.apply(_rebuild, axis=1)
    return book


async def _persist_option_signals(
    option_signals: list[dict[str, Any]],
    today_start: datetime,
) -> list[tuple[dict, Signal, bool]]:
    """Persist option signals with one-active-signal-per-ticker deduplication.

    The options engine may emit the same ticker from multiple universes or with
    multiple strategies.  We keep the highest-ranked signal per ticker (the book
    is already sorted by reward/risk) and deactivate any prior active option
    signal for those tickers before inserting the new rows.
    """
    if not option_signals:
        return []

    # Keep the first (best-ranked) option signal per ticker.
    seen_tickers: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for sig in option_signals:
        tk = sig["ticker"]
        if tk in seen_tickers:
            continue
        seen_tickers.add(tk)
        deduped.append(sig)

    persisted: list[tuple[dict, Signal, bool]] = []
    async with AsyncSessionLocal() as db:
        # NOTE: option orders are NOT submitted here. The VRP scan runs after-hours
        # (EOD panel) and Alpaca rejects option market orders outside RTH, so
        # submission is decoupled to scanner._run_scan_impl (step 6c), which runs
        # during market hours against the active VRP signals.

        # Deactivate any existing active option signals for tickers we are about
        # to refresh.  Option VRP is a daily view — a ticker should only ever have
        # one active option signal at a time.
        if seen_tickers:
            await db.execute(
                update(Signal)
                .where(Signal.is_active.is_(True))
                .where(Signal.option_strategy.isnot(None))
                .where(Signal.ticker.in_(list(seen_tickers)))
                .values(is_active=False)
            )

        for sig in deduped:
            row = Signal(
                ticker=sig["ticker"],
                company=sig.get("company"),
                action=sig["action"],
                confidence=sig["confidence"],
                raw_confidence=sig.get("rawConfidence", sig.get("raw_confidence", sig["confidence"])),
                calibrated_probability=sig.get("calibratedProbability"),
                display_confidence=sig.get("displayConfidence", sig.get("confidence")),
                rank_score=sig.get("rankScore"),
                rank_percentile=sig.get("rankPercentile"),
                alpha_score=sig.get("alphaScore"),
                confidence_warning=bool(sig.get("confidence_warning", False)),
                price=sig["price"],
                change=sig.get("change", 0.0),
                change_pct=sig.get("changePct", 0.0),
                entry=sig.get("entry"),
                stop=sig.get("stop"),
                target=sig.get("target"),
                rr=sig.get("rr"),
                headline=sig["headline"],
                sentiment=sig.get("sentiment", 0),
                style=sig.get("style", "options_vrp"),
                sources=sig.get("sources", []),
                rationale=sig.get("rationale", []),
                plain_english=sig.get("plain_english"),
                session=sig.get("session", "afterhours"),
                days_to_earnings=sig.get("daysToEarnings"),
                next_earnings_date=sig.get("nextEarningsDate"),
                expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=7),
                option_strategy=sig["option_strategy"],
                option_legs=sig.get("option_legs"),
                option_underlying_action=sig.get("option_underlying_action"),
                option_richness=sig.get("option_richness"),
                option_impl_move=sig.get("option_impl_move"),
                option_forecast_move=sig.get("option_forecast_move"),
                option_exp_gain=sig.get("option_exp_gain"),
                option_max_loss=sig.get("option_max_loss"),
                option_days_to_earnings=sig.get("option_days_to_earnings"),
            )
            db.add(row)
            await db.flush()
            persisted.append((sig, row, False))
        await db.commit()

    log.info("Persisted %d option signals", len(persisted))
    return persisted


_options_scan_attempt_date: date | None = None
_options_scan_attempts = 0
_OPTIONS_SCAN_MAX_ATTEMPTS = 4


def _should_run_options_scan() -> bool:
    """Run at most once/day on success, but allow a few retries within the day if a
    run produced nothing (transient scorer/panel failure) so one bad run doesn't
    cost the whole day's option signals. The slot is marked done only after a
    productive run (see _mark_options_scan_complete)."""
    global _options_scan_attempt_date, _options_scan_attempts
    today = datetime.now(timezone.utc).date()
    if _last_options_scan_date == today:
        return False
    if _options_scan_attempt_date != today:
        _options_scan_attempt_date = today
        _options_scan_attempts = 0
    if _options_scan_attempts >= _OPTIONS_SCAN_MAX_ATTEMPTS:
        return False
    _options_scan_attempts += 1
    return True


def _mark_options_scan_complete() -> None:
    global _last_options_scan_date
    _last_options_scan_date = datetime.now(timezone.utc).date()


async def run_options_scan(
    stock_signals: list[dict],
    today_start: datetime,
) -> list[tuple[dict, Signal, bool]]:
    """Generate and persist option VRP signals for the current trading day.

    Parameters
    ----------
    stock_signals:
        The stock signal dicts produced by the regular scan, used for directional
        fusion and earnings data.
    today_start:
        Midnight UTC boundary for daily deduplication.

    Returns
    -------
    List of (sig_dict, Signal row, force_resend) tuples, suitable for appending
    to the scanner's ``new_signals`` and passing to ``_deliver_scan_signals``.
    """
    if not _should_run_options_scan():
        return []

    direction_df = _build_direction_df(stock_signals)
    log.info("Running daily options VRP scan (direction view: %d names)", len(direction_df))

    all_option_signals: list[dict] = []
    for universe in _OPTIONS_UNIVERSES:
        try:
            summary, book = await _score_one_universe(universe, direction_df)
            book = await _resolve_book_legs(book, summary)
            sigs = book_to_signal_dicts(book, summary)
            log.info("Options universe %s: %d book signals", universe, len(sigs))
            all_option_signals.extend(sigs)
        except Exception:
            log.exception("Options scan failed for universe %s", universe)
            continue

    # Restrict the VRP book to the dedicated options universe (top options-volume,
    # Alpaca-tradable names) — keeps signals in liquid, listed contracts.
    _before = len(all_option_signals)
    all_option_signals = [s for s in all_option_signals if s.get("ticker") in OPTIONS_UNIVERSE]
    log.info(
        "Options universe filter: %d -> %d signals (top-%d options-volume set)",
        _before,
        len(all_option_signals),
        len(OPTIONS_UNIVERSE),
    )

    persisted = await _persist_option_signals(all_option_signals, today_start)
    if persisted:
        # Only consume the daily slot once we've actually produced signals; an
        # empty/failed run is retried (up to the attempt cap) on the next scan.
        _mark_options_scan_complete()

    # Daily equity snapshot for the options paper account (rolling P&L curve).
    try:
        from config import get_settings

        async with AsyncSessionLocal() as db:
            from services.options_account import snapshot_options_pnl

            await snapshot_options_pnl(db, get_settings())
    except Exception:
        log.warning("options pnl snapshot failed", exc_info=True)

    return persisted
