"""
Prediction validation script.

1. Fetches live prices for all sent signals that are old enough to resolve.
2. Writes missing outcome_1d / outcome_3d / outcome_pct / outcome_14d.
3. Runs a calibration report: confidence bands vs actual win rates, per action,
   per style, and a Brier score to quantify overconfidence/underconfidence.

Run from the backend/ directory:
    python validate_predictions.py
"""

import asyncio
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone

import yfinance as yf
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, ".")
import os as _os
from pathlib import Path as _Path

from models import OutcomePathSnapshot, OutcomeResolverAudit, Signal

try:
    from dotenv import load_dotenv as _load_dotenv

    _load_dotenv(_Path(__file__).parent / ".env", override=False)
except ImportError:
    pass
_raw = _os.getenv("DATABASE_URL", "")
if _raw.startswith("postgresql://"):
    _raw = _raw.replace("postgresql://", "postgresql+asyncpg://", 1)
DB_URL = _raw or "sqlite+aiosqlite:///./data/trading.db"
BANDS = [(0, 50), (50, 55), (55, 60), (60, 65), (65, 70), (70, 75), (75, 80), (80, 85), (85, 101)]

# Round-trip transaction cost estimate: bid-ask spread + entry/exit slippage.
# Conservative for liquid large-caps; higher for small/mid-caps.
# Any signal with outcome < FRICTION_PCT is a real-world loss even if mark-to-market positive.
FRICTION_PCT = 0.50  # 0.50% round-trip (0.25% each leg)


# ── helpers ──────────────────────────────────────────────────────────────────


def _pct(current: float, entry: float, action: str) -> float | None:
    if not current or not entry or entry <= 0:
        return None
    raw = (current - entry) / entry * 100
    return round(raw if action == "BUY" else -raw, 2)


def _age_days(sig: Signal) -> float:
    if not sig.created_at:
        return 0
    created = sig.created_at.replace(tzinfo=timezone.utc) if sig.created_at.tzinfo is None else sig.created_at
    return (datetime.now(timezone.utc) - created).total_seconds() / 86400


def _best_outcome(sig: Signal) -> float | None:
    """Return the most mature available outcome (14d preferred)."""
    for f in ("outcome_14d", "outcome_pct", "outcome_3d", "outcome_1d"):
        v = getattr(sig, f, None)
        if v is not None:
            return v
    return None


def _is_win(sig: Signal) -> bool:
    """
    Determine win/loss using the best available data in priority order:

    1. If MAE/MFE + exit_type are populated (from resolve_mae_mfe):
       - exit_type='target' → win regardless of calendar return
       - exit_type='stop'   → loss regardless of calendar return
       - exit_type='time'   → use friction-adjusted calendar return
       - exit_type='pending'→ use friction-adjusted calendar return
    2. Fallback: friction-adjusted _best_outcome > FRICTION_PCT

    This gives a more realistic picture than raw mark-to-market at day N.
    """
    exit_type = getattr(sig, "exit_type", None)
    if exit_type == "target":
        return True
    if exit_type == "stop":
        return False
    # time / pending / no exit data → friction-adjusted calendar return
    ret = _best_outcome(sig)
    if ret is None:
        return False
    return ret > FRICTION_PCT


def _effective_n(signals: list) -> int:
    """
    Count unique ticker-date pairs (effective independent bets).
    Multiple signals on the same ticker on the same calendar day are
    one market view counted multiple times — not independent observations.
    """
    seen: set[tuple] = set()
    for s in signals:
        date = s.created_at.date() if s.created_at else None
        seen.add((s.ticker, date))
    return len(seen)


def _fetch_prices(tickers: list[str]) -> dict[str, float]:
    if not tickers:
        return {}
    try:
        data = yf.download(tickers, period="1d", progress=False, auto_adjust=True)
        prices: dict[str, float] = {}
        if "Close" in data.columns:
            # Single ticker returns a Series; multiple returns a DataFrame
            close = data["Close"]
            if hasattr(close, "iloc"):
                last = close.iloc[-1]
                if hasattr(last, "items"):
                    for t, p in last.items():
                        if p and not math.isnan(float(p)):
                            prices[str(t)] = float(p)
                else:
                    # single ticker
                    ticker = tickers[0]
                    if not math.isnan(float(last)):
                        prices[ticker] = float(last)
        return prices
    except Exception as e:
        print(f"  [warn] price fetch error: {e}")
        return {}


# ── step 1: resolve pending outcomes ─────────────────────────────────────────


async def resolve_outcomes() -> int:
    engine = create_async_engine(DB_URL, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as db:
        rows = (await db.execute(select(Signal).where(Signal.is_sent == True))).scalars().all()

    # collect tickers that still need resolution
    need = [s for s in rows if s.entry and s.entry > 0]
    if not need:
        print("No resolvable signals found.")
        return 0

    tickers = list({s.ticker for s in need})
    print(f"Fetching live prices for {len(tickers)} tickers…")
    prices = _fetch_prices(tickers)
    print(f"  Got prices for {len(prices)} tickers.")

    updated = 0
    # TSYS-8a: track resolution-pass metrics for the audit row.
    processed = 0
    missing_price_tickers: set[str] = set()
    unresolved: dict[str, int] = defaultdict(int)
    async with Session() as db:
        rows = (await db.execute(select(Signal).where(Signal.is_sent == True))).scalars().all()

        for sig in rows:
            if not sig.entry or sig.entry <= 0:
                unresolved["no_entry"] += 1
                continue
            processed += 1
            current = prices.get(sig.ticker)
            if not current:
                unresolved["no_price"] += 1
                missing_price_tickers.add(sig.ticker)
                continue
            age = _age_days(sig)
            changed = False

            # Skip calendar fills for signals already closed at a hard exit price.
            # A stop or target exit locks outcome_pct at the exit level; overwriting
            # with a 7-day mark-to-market would produce phantom wins/losses.
            already_closed = sig.exit_type in ("stop", "target")

            if age >= 1 and sig.outcome_1d is None:
                sig.outcome_1d = _pct(current, sig.entry, sig.action)
                changed = True
            if age >= 3 and sig.outcome_3d is None:
                sig.outcome_3d = _pct(current, sig.entry, sig.action)
                changed = True
            if age >= 7 and sig.outcome_pct is None and not already_closed:
                sig.outcome_pct = _pct(current, sig.entry, sig.action)
                sig.outcome_at = datetime.now(timezone.utc).replace(tzinfo=None)
                changed = True
            if age >= 14 and sig.outcome_14d is None:
                sig.outcome_14d = _pct(current, sig.entry, sig.action)
                changed = True

            if changed:
                updated += 1

        # TSYS-8a: persist an audit record of this resolution pass so missing
        # bars, price source, and unresolved reasons are inspectable after the fact.
        db.add(
            OutcomeResolverAudit(
                signals_processed=processed,
                signals_resolved=updated,
                price_source="yfinance",
                missing_bars_count=len(missing_price_tickers),
                corrections_applied=None,
                unresolved_reasons=dict(unresolved) if unresolved else None,
            )
        )

        await db.commit()

    await engine.dispose()
    print(f"  Updated {updated} signals.")
    return updated


# ── step 1b: MAE / MFE / stop-target hit tracking ────────────────────────────


def _fetch_ohlcv(ticker: str, days: int = 20) -> list[tuple[float, float]]:
    """Return list of (high, low) for the last `days` trading days."""
    try:
        import yfinance as yf

        # Use Ticker.history — consistent non-MultiIndex columns across yfinance versions
        df = yf.Ticker(ticker).history(period=f"{days}d", auto_adjust=True)
        if df is None or df.empty:
            return []
        return [(float(row["High"]), float(row["Low"])) for _, row in df.iterrows()]
    except Exception:
        return []


async def resolve_mae_mfe() -> int:
    """
    For every sent signal that has an entry + stop + target but no MAE/MFE yet,
    fetch OHLCV since the signal date and compute:
      - hit_stop:   did the low ever breach the stop level (BUY) or high breach stop (SELL)?
      - hit_target: did the high ever breach the target (BUY) or low breach target (SELL)?
      - mae:        Maximum Adverse Excursion — worst % move against the position
      - mfe:        Maximum Favorable Excursion — best % move in favour of position
      - exit_type:  'target' | 'stop' | 'time' | 'pending'
    """
    engine = create_async_engine(DB_URL, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as db:
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.is_sent == True,
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                        Signal.mae.is_(None),  # not yet computed
                    )
                )
            )
            .scalars()
            .all()
        )

    # Only process signals old enough to have at least 1 day of OHLCV
    eligible = [s for s in rows if _age_days(s) >= 1 and s.entry and s.entry > 0]
    if not eligible:
        print("  No signals pending MAE/MFE computation.")
        return 0

    # Group by ticker to batch OHLCV fetches
    by_ticker: dict[str, list] = {}
    for s in eligible:
        by_ticker.setdefault(s.ticker, []).append(s)

    updated = 0
    async with Session() as db:
        for ticker, sigs in by_ticker.items():
            bars = _fetch_ohlcv(ticker, days=30)
            if not bars:
                continue
            for sig in sigs:
                entry = sig.entry
                stop = sig.stop
                target = sig.target
                is_buy = sig.action == "BUY"

                # Slice bars to those after signal creation
                age = int(_age_days(sig))
                n_bars = min(age, len(bars))
                window = bars[-n_bars:] if n_bars > 0 else bars

                worst_pct = 0.0  # adverse excursion (most negative)
                best_pct = 0.0  # favorable excursion (most positive)
                _stop_bar: int | None = None  # first bar index breaching the stop
                _tgt_bar: int | None = None  # first bar index breaching the target

                for _i, (high, low) in enumerate(window):
                    if is_buy:
                        adv = (high - entry) / entry * 100  # upside = favorable
                        adrs = (low - entry) / entry * 100  # downside = adverse
                    else:
                        adv = (entry - low) / entry * 100  # downside = favorable for SELL
                        adrs = (entry - high) / entry * 100  # upside = adverse for SELL

                    best_pct = max(best_pct, adv)
                    worst_pct = min(worst_pct, adrs)

                    # Record FIRST breach bar for stop/target (chronology matters:
                    # a live account exits at whichever level is touched first).
                    if is_buy:
                        if stop and low <= stop and _stop_bar is None:
                            _stop_bar = _i
                        if target and high >= target and _tgt_bar is None:
                            _tgt_bar = _i
                    else:
                        if stop and high >= stop and _stop_bar is None:
                            _stop_bar = _i
                        if target and low <= target and _tgt_bar is None:
                            _tgt_bar = _i

                # Determine exit type CHRONOLOGICALLY: first breach wins. If both
                # levels are touched on the SAME daily bar, intrabar order is
                # unknowable → assume stop-first (conservative). The old code
                # preferred 'target' whenever both were hit — even if the stop was
                # breached days earlier — and fix_phantom_wins then re-booked those
                # rows at the stop fill while the 'target' label survived (74 rows
                # mislabeled as of 2026-07-13).
                if _stop_bar is not None and (_tgt_bar is None or _stop_bar <= _tgt_bar):
                    exit_type = "stop"
                elif _tgt_bar is not None:
                    exit_type = "target"
                elif age >= 14:
                    exit_type = "time"
                else:
                    exit_type = "pending"

                # hit flags reflect what happened while the position was OPEN:
                # once the first level is hit, the trade is closed — a later breach
                # of the other level is counterfactual (and previously caused
                # fix_phantom_wins to clobber genuine target-first wins).
                _hit_stop = exit_type == "stop"
                _hit_target = exit_type == "target"

                sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
                if sig_db:
                    sig_db.mae = round(worst_pct, 2)
                    sig_db.mfe = round(best_pct, 2)
                    sig_db.hit_stop = _hit_stop
                    sig_db.hit_target = _hit_target
                    sig_db.exit_type = exit_type

                    # Lock outcome_pct at the exit level for stop/target hits.
                    #
                    # Root cause of phantom wins (88 of 529 trades, 16.6%):
                    #   1. Price dips below stop intraday; stop_monitor is not running
                    #      at that moment → hit_stop never set, outcome_pct never locked.
                    #   2. resolve_outcomes() runs 7 days later → price has recovered,
                    #      writes a POSITIVE outcome_pct.
                    #   3. resolve_mae_mfe() (this function) then retrospectively detects
                    #      the stop breach from OHLC history, sets hit_stop=True — but
                    #      the old check `outcome_pct is None` fails because step 2 already
                    #      wrote a positive value.  Phantom win is now permanent.
                    #
                    # Fix: also overwrite when the retrospective stop is detected AND
                    # the current outcome_pct is positive (the phantom condition).
                    # outcome_pct > 0 + hit_stop = True = phantom win by definition.
                    _is_phantom_win = exit_type == "stop" and sig_db.outcome_pct is not None and sig_db.outcome_pct > 0
                    if (
                        exit_type == "stop"
                        and sig.stop
                        and entry > 0
                        and (sig_db.outcome_pct is None or _is_phantom_win)
                    ):
                        raw = (sig.stop - entry) / entry * 100
                        sig_db.outcome_pct = round(raw if is_buy else -raw, 2)
                        sig_db.outcome_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    elif exit_type == "target" and sig.target and entry > 0:
                        # Symmetric to the stop path: a target-first exit realizes the
                        # TARGET fill, not a later calendar mark. The old `outcome_pct
                        # is None` guard let a day-7 mark-to-market survive (mean booked
                        # +4.06% vs +10.4% at fill — "phantom losses", the mirror image
                        # of phantom wins). Overwrite any calendar mark with the fill.
                        raw = (sig.target - entry) / entry * 100
                        _tgt_fill = round(raw if is_buy else -raw, 2)
                        if sig_db.outcome_pct is None or abs(sig_db.outcome_pct - _tgt_fill) > 0.01:
                            sig_db.outcome_pct = _tgt_fill
                            sig_db.outcome_at = datetime.now(timezone.utc).replace(tzinfo=None)

                    # TSYS-8b: snapshot the price path used to derive MAE/MFE/exit so
                    # the resolution can be replayed without re-fetching OHLCV. Runs
                    # once per signal (this pass only selects mae IS NULL rows).
                    db.add(
                        OutcomePathSnapshot(
                            signal_id=sig.id,
                            path_data={
                                "bars": [[round(h, 4), round(low, 4)] for h, low in window],
                                "entry": entry,
                                "stop": stop,
                                "target": target,
                                "action": sig.action,
                                "mae": round(worst_pct, 2),
                                "mfe": round(best_pct, 2),
                                "exit_type": exit_type,
                            },
                        )
                    )

                    updated += 1

        await db.commit()

    await engine.dispose()
    print(f"  MAE/MFE computed for {updated} signals.")
    return updated


async def fix_phantom_wins(apply: bool = False) -> int:
    """Retroactively correct phantom wins in the database.

    A phantom win occurs when:
      1. Price breaches the stop intraday (hit_stop=True in OHLC history).
      2. Price recovers above entry by the 7-day mark-to-market measurement.
      3. outcome_pct is therefore positive despite the stop being hit.

    The correct outcome_pct is: (stop - entry) / entry × 100 for BUY,
    (entry - stop) / entry × 100 for SELL — matching what the live account
    would have realised at the stop fill price.

    This function runs over all existing signals where hit_stop=True AND
    outcome_pct > 0, correcting the stored value.  It is idempotent: running
    it twice produces the same result.
    """
    engine = create_async_engine(DB_URL, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as db:
        phantoms = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.hit_stop == True,
                        Signal.outcome_pct > 0,
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        # Chronology guard (2026-07-13): if the target was ALSO hit,
                        # the stop breach may postdate a target-first exit — the
                        # position was already closed at the target, so the "phantom
                        # win" is genuine. resolve_mae_mfe now sets exactly one hit
                        # flag (first breach wins); this guard protects legacy rows
                        # with both flags set from being clobbered to a stop fill.
                        Signal.hit_target.isnot(True),
                    )
                )
            )
            .scalars()
            .all()
        )

    if not phantoms:
        print("  No phantom wins found — nothing to fix.")
        return 0

    print(f"  Found {len(phantoms)} phantom wins (hit_stop=True, outcome_pct > 0).")
    fixes = []
    for sig in phantoms:
        entry = float(sig.entry)
        stop = float(sig.stop)
        if entry <= 0:
            continue
        if sig.action == "BUY":
            corrected = round((stop - entry) / entry * 100, 2)
        else:
            corrected = round((entry - stop) / entry * 100, 2)
        fixes.append((sig.id, sig.ticker, float(sig.outcome_pct), corrected))

    if not apply:
        print(f"  DRY RUN — would correct {len(fixes)} signals.")
        sample = fixes[:5]
        for sid, tkr, old, new in sample:
            print(f"    {tkr} id={sid}: {old:+.2f}% → {new:+.2f}%")
        if len(fixes) > 5:
            print(f"    … and {len(fixes) - 5} more")
        print("  Re-run with apply=True (or --fix-phantoms --apply) to write changes.")
        await engine.dispose()
        return 0

    async with Session() as db:
        for sig_id, _, _, corrected in fixes:
            # Correct both 7d (outcome_pct) and 14d (outcome_14d) to stop-fill level.
            # run_calibration() prefers outcome_14d — if we only fix outcome_pct,
            # the calibration still sees the phantom win via the 14d field.
            # A stop-out trade has a realized P&L of (stop - entry); the 14d
            # mark-to-market is counterfactual and irrelevant for calibration.
            await db.execute(
                update(Signal).where(Signal.id == sig_id).values(outcome_pct=corrected, outcome_14d=corrected)
            )
        await db.commit()

    await engine.dispose()
    print(f"  Fixed {len(fixes)} phantom wins — outcome_pct corrected to stop-fill level.")
    return len(fixes)


async def fix_exit_chronology(apply: bool = False) -> int:
    """Re-book legacy rows where BOTH stop and target were hit (one-off backfill).

    Before 2026-07-13, resolve_mae_mfe labeled any both-hit trade 'target'
    (regardless of which level was touched first) and fix_phantom_wins then
    re-booked it at the STOP fill — leaving 74 rows labeled 'target' with
    stop-loss outcomes. This replays each ambiguous row's price path
    chronologically (first breach wins; same daily bar → stop, conservative)
    and re-books outcome_pct/outcome_14d at the true first-hit fill.

    Path source: outcome_path_snapshots (TSYS-8b) where available, else a
    date-ranged OHLCV refetch. Rows with neither are reported and skipped.
    Idempotent: corrected rows have exactly one hit flag set and no longer match.
    """
    import yfinance as yf

    engine = create_async_engine(DB_URL, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as db:
        rows = (
            (
                await db.execute(
                    select(Signal).where(
                        Signal.hit_stop == True,
                        Signal.hit_target == True,
                        Signal.outcome_pct.isnot(None),
                        Signal.entry.isnot(None),
                        Signal.stop.isnot(None),
                        Signal.target.isnot(None),
                    )
                )
            )
            .scalars()
            .all()
        )
        snap_rows = {}
        if rows:
            snaps = (
                (
                    await db.execute(
                        select(OutcomePathSnapshot).where(OutcomePathSnapshot.signal_id.in_([s.id for s in rows]))
                    )
                )
                .scalars()
                .all()
            )
            snap_rows = {s.signal_id: s.path_data for s in snaps}

    if not rows:
        print("  No both-hit (ambiguous chronology) rows found — nothing to re-book.")
        await engine.dispose()
        return 0

    print(f"  Found {len(rows)} rows with hit_stop AND hit_target both set.")
    ohlcv_cache: dict[str, object] = {}
    fixes = []  # (id, ticker, old_exit, new_exit, old_pct, new_pct)
    skipped = 0
    for sig in rows:
        entry, stop, target = float(sig.entry), float(sig.stop), float(sig.target)
        if entry <= 0:
            skipped += 1
            continue
        is_buy = sig.action == "BUY"

        # Price path: snapshot bars, else date-ranged refetch.
        bars = None
        snap = snap_rows.get(sig.id)
        if snap and snap.get("bars"):
            bars = [(float(h), float(low)) for h, low in snap["bars"]]
        else:
            try:
                if sig.ticker not in ohlcv_cache:
                    ohlcv_cache[sig.ticker] = yf.Ticker(sig.ticker).history(
                        start=sig.created_at.strftime("%Y-%m-%d"), auto_adjust=True
                    )
                df = ohlcv_cache[sig.ticker]
                if df is not None and not df.empty:
                    win = df[df.index >= sig.created_at.strftime("%Y-%m-%d")].head(14)
                    bars = [(float(r["High"]), float(r["Low"])) for _, r in win.iterrows()]
            except Exception:
                bars = None
        if not bars:
            skipped += 1
            continue

        stop_bar = tgt_bar = None
        for i, (high, low) in enumerate(bars):
            if is_buy:
                if low <= stop and stop_bar is None:
                    stop_bar = i
                if high >= target and tgt_bar is None:
                    tgt_bar = i
            else:
                if high >= stop and stop_bar is None:
                    stop_bar = i
                if low <= target and tgt_bar is None:
                    tgt_bar = i
        if stop_bar is None and tgt_bar is None:
            skipped += 1  # path window doesn't reproduce either breach — leave untouched
            continue

        if stop_bar is not None and (tgt_bar is None or stop_bar <= tgt_bar):
            new_exit, level = "stop", stop
        else:
            new_exit, level = "target", target
        raw = (level - entry) / entry * 100
        new_pct = round(raw if is_buy else -raw, 2)
        if sig.exit_type != new_exit or abs(float(sig.outcome_pct) - new_pct) > 0.01:
            fixes.append((sig.id, sig.ticker, sig.exit_type, new_exit, float(sig.outcome_pct), new_pct))

    print(f"  Re-bookable: {len(fixes)}  |  skipped (no path data / no breach in window): {skipped}")
    if not apply:
        print("  DRY RUN — sample:")
        for sid, tkr, oe, ne, op, np_ in fixes[:10]:
            print(f"    {tkr} id={sid}: {oe}→{ne}  {op:+.2f}% → {np_:+.2f}%")
        if len(fixes) > 10:
            print(f"    … and {len(fixes) - 10} more")
        print("  Re-run with --fix-exit-chronology --apply to write changes.")
        await engine.dispose()
        return 0

    async with Session() as db:
        for sid, _, _, new_exit, _, new_pct in fixes:
            await db.execute(
                update(Signal)
                .where(Signal.id == sid)
                .values(
                    exit_type=new_exit,
                    hit_stop=(new_exit == "stop"),
                    hit_target=(new_exit == "target"),
                    outcome_pct=new_pct,
                    outcome_14d=new_pct,  # calibration prefers 14d — keep consistent (see fix_phantom_wins)
                )
            )
        await db.commit()
    await engine.dispose()
    print(f"  Re-booked {len(fixes)} rows at chronological first-hit fills.")
    return len(fixes)


# ── step 2: calibration report ───────────────────────────────────────────────


async def calibration_report():
    engine = create_async_engine(DB_URL, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as db:
        rows = (await db.execute(select(Signal).where(Signal.is_sent == True))).scalars().all()
    await engine.dispose()

    resolved = [s for s in rows if _best_outcome(s) is not None and s.action in ("BUY", "SELL")]
    eff_n = _effective_n(resolved)  # unique ticker-date pairs

    print(f"\n{'=' * 62}")
    print("  PREDICTION VALIDATION REPORT")
    print(f"  Resolved signals : {len(resolved)} / {sum(1 for s in rows if s.action in ('BUY', 'SELL'))} sent BUY+SELL")
    print(f"  Effective unique : {eff_n}  (unique ticker-date pairs — real independent bets)")
    print(
        f"  Duplication rate : {(len(resolved) - eff_n) / len(resolved) * 100:.1f}% of rows are same-ticker same-day repeats"
        if len(resolved) > eff_n
        else "  No same-ticker same-day duplicates."
    )
    print(f"{'=' * 62}")

    if not resolved:
        print("No resolved signals to analyse.")
        return

    # ── overall — raw (mark-to-market) ────────────────────────────────────────
    total = len(resolved)
    wins_raw = sum(1 for s in resolved if _best_outcome(s) > 0)
    avg_ret = sum(_best_outcome(s) for s in resolved) / total
    avg_conf = sum(s.confidence for s in resolved) / total
    brier = sum(((s.confidence / 100) - (1 if _best_outcome(s) > 0 else 0)) ** 2 for s in resolved) / total

    # ── overall — friction-adjusted (realistic P&L) ────────────────────────────
    wins_adj = sum(1 for s in resolved if _is_win(s))
    n_with_exit = sum(1 for s in resolved if getattr(s, "exit_type", None) not in (None, "pending"))
    n_target_hit = sum(1 for s in resolved if getattr(s, "exit_type", None) == "target")
    n_stop_hit = sum(1 for s in resolved if getattr(s, "exit_type", None) == "stop")

    print("\n  OVERALL (RAW — mark-to-market at fixed horizon)")
    print(f"  {'Signals':<26} {total}  (effective: {eff_n} ticker-days)")
    print(f"  {'Win rate (raw)':<26} {wins_raw / total * 100:.1f}%")
    print(f"  {'Avg confidence':<26} {avg_conf:.1f}%")
    print(f"  {'Avg return':<26} {avg_ret:+.2f}%")
    print(f"  {'Brier score':<26} {brier:.4f}  (0=perfect, 0.25=random, lower=better)")

    gap = avg_conf - wins_raw / total * 100
    direction = "OVERCONFIDENT" if gap > 0 else "UNDERCONFIDENT"
    print(f"  {'Confidence gap':<26} {gap:+.1f}pp  ({direction})")

    print(f"\n  OVERALL (FRICTION-ADJUSTED — {FRICTION_PCT:.2f}% round-trip cost)")
    print(f"  {'Win rate (after costs)':<26} {wins_adj / total * 100:.1f}%")
    print(f"  {'Avg return (after costs)':<26} {avg_ret - FRICTION_PCT:+.2f}%")
    brier_adj = sum(((s.confidence / 100) - (1 if _is_win(s) else 0)) ** 2 for s in resolved) / total
    print(f"  {'Brier score (adj)':<26} {brier_adj:.4f}")
    if n_with_exit > 0:
        print(f"\n  EXIT TYPE BREAKDOWN  ({n_with_exit}/{total} signals with stop/target data)")
        print(f"  {'Target hit':<26} {n_target_hit}  ({n_target_hit / n_with_exit * 100:.0f}% of resolved)")
        print(f"  {'Stop hit':<26} {n_stop_hit}  ({n_stop_hit / n_with_exit * 100:.0f}% of resolved)")
        print(f"  {'Time/pending':<26} {n_with_exit - n_target_hit - n_stop_hit}")

    gap_adj = avg_conf - wins_adj / total * 100
    direction_adj = "OVERCONFIDENT" if gap_adj > 0 else "UNDERCONFIDENT"
    print(f"  {'Confidence gap (adj)':<26} {gap_adj:+.1f}pp  ({direction_adj})")

    # ── by action ─────────────────────────────────────────────────────────────
    print("\n  BY ACTION  (raw win% | friction-adj win%)")
    print(f"  {'Action':<8} {'N':>5} {'Win%(raw)':>10} {'Win%(adj)':>10} {'Avg Ret':>9} {'Avg Conf':>10}")
    print(f"  {'-' * 58}")
    for action in ("BUY", "SELL"):
        sigs = [s for s in resolved if s.action == action]
        if not sigs:
            continue
        w_raw = sum(1 for s in sigs if _best_outcome(s) > 0)
        w_adj = sum(1 for s in sigs if _is_win(s))
        n = len(sigs)
        ac = sum(s.confidence for s in sigs) / n
        ar = sum(_best_outcome(s) for s in sigs) / n
        flag = " ⚠" if w_raw / n * 100 - w_adj / n * 100 > 5 else ""
        print(f"  {action:<8} {n:>5} {w_raw / n * 100:>9.1f}% {w_adj / n * 100:>9.1f}% {ar:>+8.2f}% {ac:>9.1f}%{flag}")

    # ── by style ──────────────────────────────────────────────────────────────
    print("\n  BY TRADE STYLE  (raw win% | friction-adj win%)")
    print(f"  {'Style':<12} {'N':>5} {'Win%(raw)':>10} {'Win%(adj)':>10} {'Avg Ret':>9} {'Avg Conf':>10}")
    print(f"  {'-' * 61}")
    for style in ("intraday", "swing", "position"):
        sigs = [s for s in resolved if (s.style or "swing") == style]
        if not sigs:
            continue
        w_raw = sum(1 for s in sigs if _best_outcome(s) > 0)
        w_adj = sum(1 for s in sigs if _is_win(s))
        n = len(sigs)
        ac = sum(s.confidence for s in sigs) / n
        ar = sum(_best_outcome(s) for s in sigs) / n
        cost_drag = w_raw / n * 100 - w_adj / n * 100
        flag = f" ({cost_drag:+.1f}pp friction drag)" if cost_drag > 3 else ""
        print(f"  {style:<12} {n:>5} {w_raw / n * 100:>9.1f}% {w_adj / n * 100:>9.1f}% {ar:>+8.2f}% {ac:>9.1f}%{flag}")

    # ── confidence band calibration ───────────────────────────────────────────
    print("\n  CONFIDENCE BAND CALIBRATION  (friction-adjusted win%)")
    print(f"  {'Band':<12} {'N':>5} {'Win%(adj)':>10} {'Avg Conf':>10} {'Avg Ret':>9} {'Gap':>8}  {'Calibrated?'}")
    print(f"  {'-' * 75}")
    for lo, hi in BANDS:
        sigs = [s for s in resolved if lo <= s.confidence < hi]
        if not sigs:
            continue
        w = sum(1 for s in sigs if _is_win(s))
        n = len(sigs)
        wr = w / n * 100
        ac = sum(s.confidence for s in sigs) / n
        ar = sum(_best_outcome(s) for s in sigs) / n
        g = ac - wr
        ok = "OK" if abs(g) <= 10 else ("OVER ⚠" if g > 0 else "UNDER ⚠")
        print(f"  {lo}-{hi}%{'':<6} {n:>5} {wr:>9.1f}% {ac:>9.1f}% {ar:>+8.2f}% {g:>+7.1f}pp  {ok}")

    # ── per-ticker performance ────────────────────────────────────────────────
    ticker_stats: dict[str, dict] = defaultdict(lambda: {"w": 0, "w_adj": 0, "n": 0, "ret": 0.0, "conf": 0.0})
    for s in resolved:
        ts = ticker_stats[s.ticker]
        ts["n"] += 1
        ts["conf"] += s.confidence
        ret = _best_outcome(s)
        ts["ret"] += ret
        if ret > 0:
            ts["w"] += 1
        if _is_win(s):
            ts["w_adj"] += 1

    print("\n  PER-TICKER (min 3 signals, sorted by friction-adj win%)")
    print(f"  {'Ticker':<8} {'N':>4} {'Win%raw':>8} {'Win%adj':>8} {'Avg Ret':>9} {'Gap':>8}")
    print(f"  {'-' * 58}")
    rows_out = sorted(
        [(t, d) for t, d in ticker_stats.items() if d["n"] >= 3],
        key=lambda x: x[1]["w_adj"] / x[1]["n"],
        reverse=True,
    )
    for t, d in rows_out:
        n = d["n"]
        wr_raw = d["w"] / n * 100
        wr_adj = d["w_adj"] / n * 100
        ac = d["conf"] / n
        ar = d["ret"] / n
        g = ac - wr_adj
        flag = " ⚠" if abs(g) > 15 else ""
        print(f"  {t:<8} {n:>4} {wr_raw:>7.1f}% {wr_adj:>7.1f}% {ar:>+8.2f}% {g:>+7.1f}pp{flag}")

    # ── horizon comparison ────────────────────────────────────────────────────
    print("\n  WIN RATE BY OUTCOME HORIZON (signals that have each)")
    print(f"  {'Horizon':<12} {'N':>5} {'Win%':>7} {'Avg Ret':>9}")
    print(f"  {'-' * 40}")
    for label, field in [
        ("1-day", "outcome_1d"),
        ("3-day", "outcome_3d"),
        ("7-day", "outcome_pct"),
        ("14-day", "outcome_14d"),
    ]:
        sigs = [s for s in rows if s.action in ("BUY", "SELL") and getattr(s, field) is not None]
        if not sigs:
            continue
        w = sum(1 for s in sigs if getattr(s, field) > 0)
        n = len(sigs)
        ar = sum(getattr(s, field) for s in sigs) / n
        print(f"  {label:<12} {n:>5} {w / n * 100:>6.1f}% {ar:>+8.2f}%")

    # ── top losses ────────────────────────────────────────────────────────────
    worst = sorted(resolved, key=lambda s: _best_outcome(s))[:8]
    print("\n  WORST SIGNALS")
    print(f"  {'Ticker':<7} {'Action':<6} {'Conf':>6} {'Ret':>8}  {'Date':<12}  {'Horizon used'}")
    print(f"  {'-' * 60}")
    for s in worst:
        ret = _best_outcome(s)
        h = (
            "14d"
            if s.outcome_14d is not None
            else "7d"
            if s.outcome_pct is not None
            else "3d"
            if s.outcome_3d is not None
            else "1d"
        )
        dt = s.created_at.strftime("%Y-%m-%d") if s.created_at else "?"
        print(f"  {s.ticker:<7} {s.action:<6} {s.confidence:>5.1f}% {ret:>+7.2f}%  {dt}  ({h})")

    # ── top wins ──────────────────────────────────────────────────────────────
    best = sorted(resolved, key=lambda s: _best_outcome(s), reverse=True)[:8]
    print("\n  BEST SIGNALS")
    print(f"  {'Ticker':<7} {'Action':<6} {'Conf':>6} {'Ret':>8}  {'Date':<12}  {'Horizon used'}")
    print(f"  {'-' * 60}")
    for s in best:
        ret = _best_outcome(s)
        h = (
            "14d"
            if s.outcome_14d is not None
            else "7d"
            if s.outcome_pct is not None
            else "3d"
            if s.outcome_3d is not None
            else "1d"
        )
        dt = s.created_at.strftime("%Y-%m-%d") if s.created_at else "?"
        print(f"  {s.ticker:<7} {s.action:<6} {s.confidence:>5.1f}% {ret:>+7.2f}%  {dt}  ({h})")

    # ── MAE / MFE / stop-target summary ─────────────────────────────────────
    mae_sigs = [s for s in rows if s.action in ("BUY", "SELL") and getattr(s, "mae", None) is not None]
    if mae_sigs:
        n_mae = len(mae_sigs)
        n_stop = sum(1 for s in mae_sigs if s.hit_stop)
        n_target = sum(1 for s in mae_sigs if s.hit_target)
        n_time = sum(1 for s in mae_sigs if s.exit_type == "time")
        avg_mae = sum(s.mae for s in mae_sigs) / n_mae
        avg_mfe = sum(s.mfe for s in mae_sigs) / n_mae
        mfe_mae_ratio = avg_mfe / abs(avg_mae) if avg_mae != 0 else float("inf")

        print(f"\n  MAE / MFE TRADE-PATH ANALYTICS (n={n_mae})")
        print(f"  {'Metric':<30} {'Value'}")
        print(f"  {'-' * 45}")
        print(f"  {'Signals w/ stop hit':<30} {n_stop} ({n_stop / n_mae * 100:.1f}%)")
        print(f"  {'Signals w/ target hit':<30} {n_target} ({n_target / n_mae * 100:.1f}%)")
        print(f"  {'Signals exited by time':<30} {n_time} ({n_time / n_mae * 100:.1f}%)")
        print(f"  {'Avg MAE (worst drawdown)':<30} {avg_mae:+.2f}%")
        print(f"  {'Avg MFE (best excursion)':<30} {avg_mfe:+.2f}%")
        print(f"  {'MFE/MAE ratio':<30} {mfe_mae_ratio:.2f}×  (>1 = signals move right first)")

        if mfe_mae_ratio < 1.0:
            print("\n  ⚠  MFE/MAE < 1.0: signals move AGAINST position before recovering.")
            print("     Entries may be too early — consider waiting for confirmation.")
        elif mfe_mae_ratio > 2.5:
            print("\n  ✓  MFE/MAE > 2.5: signals strongly move right before any adverse excursion.")
            print("     Entry timing is good; ensure stops aren't too tight.")

        if n_stop / n_mae > 0.40:
            print(f"\n  ⚠  Stop hit rate {n_stop / n_mae * 100:.0f}% > 40%. Stops may be too tight")
            print("     or entries are too aggressive. Consider ATR×3 stops.")
        if n_target / n_mae > 0.50:
            print(f"\n  ✓  Target hit rate {n_target / n_mae * 100:.0f}% > 50%. Target placement is realistic.")

    print(f"\n{'=' * 62}\n")


# ── main ─────────────────────────────────────────────────────────────────────


async def main(fix_phantoms: bool = False, apply_phantoms: bool = False, fix_chronology: bool = False):
    if fix_chronology:
        print("\nStep 0 — Re-booking both-hit rows at chronological first-hit fills…")
        await fix_exit_chronology(apply=apply_phantoms)
        return
    if fix_phantoms:
        print("\nStep 0 — Fixing phantom wins (hit_stop=True but outcome_pct > 0)…")
        await fix_phantom_wins(apply=apply_phantoms)
        return
    print("\nStep 1 — Resolving pending outcomes…")
    updated = await resolve_outcomes()
    print("\nStep 1b — Computing MAE/MFE / stop-target tracking…")
    await resolve_mae_mfe()
    print("\nStep 1c — Correcting phantom wins…")
    await fix_phantom_wins(apply=True)
    print("\nStep 2 — Running calibration report…")
    await calibration_report()


def _annual_sharpe(returns: list[float]) -> float:
    if len(returns) < 2:
        return 0.0
    mean = sum(returns) / len(returns)
    var = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
    if var <= 0:
        return 0.0
    return (mean / (var**0.5)) * (len(returns) ** 0.5)


async def gate_stats() -> tuple[int, float, float]:
    """Return (n_resolved, raw_win_rate, annualized_sharpe) for gating."""
    engine = create_async_engine(DB_URL, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as db:
        rows = (await db.execute(select(Signal).where(Signal.is_sent == True))).scalars().all()
    await engine.dispose()

    resolved = [s for s in rows if _best_outcome(s) is not None and s.action in ("BUY", "SELL")]
    n = len(resolved)
    if n == 0:
        return 0, 0.0, 0.0
    wins = sum(1 for s in resolved if _best_outcome(s) > 0)
    returns = [_best_outcome(s) for s in resolved]
    return n, wins / n, _annual_sharpe(returns)


if __name__ == "__main__":
    import argparse as _ap

    _parser = _ap.ArgumentParser()
    _parser.add_argument("--fix-phantoms", action="store_true", help="Dry-run phantom win correction")
    _parser.add_argument(
        "--fix-exit-chronology", action="store_true", help="Dry-run re-booking of both-hit rows (first breach wins)"
    )
    _parser.add_argument("--apply", action="store_true", help="Write corrections to DB")
    _parser.add_argument("--gate-win-rate", type=float, default=None, help="Minimum raw win rate (0-1) to exit 0")
    _parser.add_argument("--gate-sharpe", type=float, default=None, help="Minimum annualized Sharpe to exit 0")
    _args = _parser.parse_args()

    asyncio.run(
        main(fix_phantoms=_args.fix_phantoms, apply_phantoms=_args.apply, fix_chronology=_args.fix_exit_chronology)
    )

    if _args.gate_win_rate is not None or _args.gate_sharpe is not None:
        n, wr, sharpe = asyncio.run(gate_stats())
        print(f"\nAccuracy gate: n={n} win_rate={wr:.2%} sharpe={sharpe:.2f}")
        ok = True
        if _args.gate_win_rate is not None and wr < _args.gate_win_rate:
            print(f"FAIL: win rate {wr:.2%} < {_args.gate_win_rate:.2%}")
            ok = False
        if _args.gate_sharpe is not None and sharpe < _args.gate_sharpe:
            print(f"FAIL: Sharpe {sharpe:.2f} < {_args.gate_sharpe:.2f}")
            ok = False
        if ok:
            print("PASS: accuracy gate")
        else:
            sys.exit(1)
