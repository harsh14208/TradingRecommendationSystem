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
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, ".")
from models import Signal

import os as _os
from pathlib import Path as _Path
try:
    from dotenv import load_dotenv as _load_dotenv
    _load_dotenv(_Path(__file__).parent / ".env", override=False)
except ImportError:
    pass
_raw = _os.getenv("DATABASE_URL", "")
if _raw.startswith("postgresql://"):
    _raw = _raw.replace("postgresql://", "postgresql+asyncpg://", 1)
DB_URL = _raw or "sqlite+aiosqlite:///./data/trading.db"
BANDS  = [(0, 50), (50, 55), (55, 60), (60, 65), (65, 70), (70, 75), (75, 80), (80, 85), (85, 101)]

# Round-trip transaction cost estimate: bid-ask spread + entry/exit slippage.
# Conservative for liquid large-caps; higher for small/mid-caps.
# Any signal with outcome < FRICTION_PCT is a real-world loss even if mark-to-market positive.
FRICTION_PCT = 0.50   # 0.50% round-trip (0.25% each leg)


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
        rows = (await db.execute(
            select(Signal).where(Signal.is_sent == True)
        )).scalars().all()

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
    async with Session() as db:
        rows = (await db.execute(
            select(Signal).where(Signal.is_sent == True)
        )).scalars().all()

        for sig in rows:
            if not sig.entry or sig.entry <= 0:
                continue
            current = prices.get(sig.ticker)
            if not current:
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
                sig.outcome_at  = datetime.now(timezone.utc).replace(tzinfo=None)
                changed = True
            if age >= 14 and sig.outcome_14d is None:
                sig.outcome_14d = _pct(current, sig.entry, sig.action)
                changed = True

            if changed:
                updated += 1

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
    engine  = create_async_engine(DB_URL, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as db:
        rows = (await db.execute(
            select(Signal).where(
                Signal.is_sent == True,
                Signal.entry.isnot(None),
                Signal.stop.isnot(None),
                Signal.target.isnot(None),
                Signal.mae.is_(None),   # not yet computed
            )
        )).scalars().all()

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
                entry  = sig.entry
                stop   = sig.stop
                target = sig.target
                is_buy = sig.action == "BUY"

                # Slice bars to those after signal creation
                age     = int(_age_days(sig))
                n_bars  = min(age, len(bars))
                window  = bars[-n_bars:] if n_bars > 0 else bars

                worst_pct = 0.0   # adverse excursion (most negative)
                best_pct  = 0.0   # favorable excursion (most positive)
                _hit_stop   = False
                _hit_target = False

                for high, low in window:
                    if is_buy:
                        adv = (high - entry) / entry * 100   # upside = favorable
                        adrs = (low  - entry) / entry * 100   # downside = adverse
                    else:
                        adv = (entry - low)  / entry * 100   # downside = favorable for SELL
                        adrs = (entry - high) / entry * 100  # upside = adverse for SELL

                    best_pct  = max(best_pct,  adv)
                    worst_pct = min(worst_pct, adrs)

                    # Check stop/target hit
                    if is_buy:
                        if stop  and low  <= stop:   _hit_stop   = True
                        if target and high >= target: _hit_target = True
                    else:
                        if stop  and high >= stop:   _hit_stop   = True
                        if target and low  <= target: _hit_target = True

                # Determine exit type (chronological priority)
                if _hit_target:
                    exit_type = "target"
                elif _hit_stop:
                    exit_type = "stop"
                elif age >= 14:
                    exit_type = "time"
                else:
                    exit_type = "pending"

                sig_db = (await db.execute(select(Signal).where(Signal.id == sig.id))).scalar_one_or_none()
                if sig_db:
                    sig_db.mae        = round(worst_pct, 2)
                    sig_db.mfe        = round(best_pct,  2)
                    sig_db.hit_stop   = _hit_stop
                    sig_db.hit_target = _hit_target
                    sig_db.exit_type  = exit_type

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
                    _is_phantom_win = (
                        exit_type == "stop" and
                        sig_db.outcome_pct is not None and
                        sig_db.outcome_pct > 0
                    )
                    if exit_type == "stop" and sig.stop and entry > 0 and (
                        sig_db.outcome_pct is None or _is_phantom_win
                    ):
                        raw = (sig.stop - entry) / entry * 100
                        sig_db.outcome_pct = round(raw if is_buy else -raw, 2)
                        sig_db.outcome_at  = datetime.now(timezone.utc).replace(tzinfo=None)
                    elif exit_type == "target" and sig_db.outcome_pct is None and sig.target and entry > 0:
                        raw = (sig.target - entry) / entry * 100
                        sig_db.outcome_pct = round(raw if is_buy else -raw, 2)
                        sig_db.outcome_at  = datetime.now(timezone.utc).replace(tzinfo=None)

                    updated += 1

        await db.commit()

    await engine.dispose()
    print(f"  MAE/MFE computed for {updated} signals.")
    return updated


# ── step 2: calibration report ───────────────────────────────────────────────

async def calibration_report():
    engine = create_async_engine(DB_URL, echo=False)
    Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as db:
        rows = (await db.execute(
            select(Signal).where(Signal.is_sent == True)
        )).scalars().all()
    await engine.dispose()

    resolved = [s for s in rows if _best_outcome(s) is not None and s.action in ("BUY", "SELL")]
    eff_n    = _effective_n(resolved)   # unique ticker-date pairs

    print(f"\n{'='*62}")
    print(f"  PREDICTION VALIDATION REPORT")
    print(f"  Resolved signals : {len(resolved)} / {sum(1 for s in rows if s.action in ('BUY','SELL'))} sent BUY+SELL")
    print(f"  Effective unique : {eff_n}  (unique ticker-date pairs — real independent bets)")
    print(f"  Duplication rate : {(len(resolved)-eff_n)/len(resolved)*100:.1f}% of rows are same-ticker same-day repeats" if len(resolved) > eff_n else "  No same-ticker same-day duplicates.")
    print(f"{'='*62}")

    if not resolved:
        print("No resolved signals to analyse.")
        return

    # ── overall — raw (mark-to-market) ────────────────────────────────────────
    total    = len(resolved)
    wins_raw = sum(1 for s in resolved if _best_outcome(s) > 0)
    avg_ret  = sum(_best_outcome(s) for s in resolved) / total
    avg_conf = sum(s.confidence for s in resolved) / total
    brier    = sum(
        ((s.confidence / 100) - (1 if _best_outcome(s) > 0 else 0)) ** 2
        for s in resolved
    ) / total

    # ── overall — friction-adjusted (realistic P&L) ────────────────────────────
    wins_adj = sum(1 for s in resolved if _is_win(s))
    n_with_exit = sum(1 for s in resolved if getattr(s, "exit_type", None) not in (None, "pending"))
    n_target_hit = sum(1 for s in resolved if getattr(s, "exit_type", None) == "target")
    n_stop_hit   = sum(1 for s in resolved if getattr(s, "exit_type", None) == "stop")

    print(f"\n  OVERALL (RAW — mark-to-market at fixed horizon)")
    print(f"  {'Signals':<26} {total}  (effective: {eff_n} ticker-days)")
    print(f"  {'Win rate (raw)':<26} {wins_raw/total*100:.1f}%")
    print(f"  {'Avg confidence':<26} {avg_conf:.1f}%")
    print(f"  {'Avg return':<26} {avg_ret:+.2f}%")
    print(f"  {'Brier score':<26} {brier:.4f}  (0=perfect, 0.25=random, lower=better)")

    gap = avg_conf - wins_raw / total * 100
    direction = "OVERCONFIDENT" if gap > 0 else "UNDERCONFIDENT"
    print(f"  {'Confidence gap':<26} {gap:+.1f}pp  ({direction})")

    print(f"\n  OVERALL (FRICTION-ADJUSTED — {FRICTION_PCT:.2f}% round-trip cost)")
    print(f"  {'Win rate (after costs)':<26} {wins_adj/total*100:.1f}%")
    print(f"  {'Avg return (after costs)':<26} {avg_ret - FRICTION_PCT:+.2f}%")
    brier_adj = sum(
        ((s.confidence / 100) - (1 if _is_win(s) else 0)) ** 2
        for s in resolved
    ) / total
    print(f"  {'Brier score (adj)':<26} {brier_adj:.4f}")
    if n_with_exit > 0:
        print(f"\n  EXIT TYPE BREAKDOWN  ({n_with_exit}/{total} signals with stop/target data)")
        print(f"  {'Target hit':<26} {n_target_hit}  ({n_target_hit/n_with_exit*100:.0f}% of resolved)")
        print(f"  {'Stop hit':<26} {n_stop_hit}  ({n_stop_hit/n_with_exit*100:.0f}% of resolved)")
        print(f"  {'Time/pending':<26} {n_with_exit - n_target_hit - n_stop_hit}")

    gap_adj = avg_conf - wins_adj / total * 100
    direction_adj = "OVERCONFIDENT" if gap_adj > 0 else "UNDERCONFIDENT"
    print(f"  {'Confidence gap (adj)':<26} {gap_adj:+.1f}pp  ({direction_adj})")

    # ── by action ─────────────────────────────────────────────────────────────
    print(f"\n  BY ACTION  (raw win% | friction-adj win%)")
    print(f"  {'Action':<8} {'N':>5} {'Win%(raw)':>10} {'Win%(adj)':>10} {'Avg Ret':>9} {'Avg Conf':>10}")
    print(f"  {'-'*58}")
    for action in ("BUY", "SELL"):
        sigs = [s for s in resolved if s.action == action]
        if not sigs:
            continue
        w_raw = sum(1 for s in sigs if _best_outcome(s) > 0)
        w_adj = sum(1 for s in sigs if _is_win(s))
        n = len(sigs)
        ac = sum(s.confidence for s in sigs) / n
        ar = sum(_best_outcome(s) for s in sigs) / n
        flag = " ⚠" if w_raw/n*100 - w_adj/n*100 > 5 else ""
        print(f"  {action:<8} {n:>5} {w_raw/n*100:>9.1f}% {w_adj/n*100:>9.1f}% {ar:>+8.2f}% {ac:>9.1f}%{flag}")

    # ── by style ──────────────────────────────────────────────────────────────
    print(f"\n  BY TRADE STYLE  (raw win% | friction-adj win%)")
    print(f"  {'Style':<12} {'N':>5} {'Win%(raw)':>10} {'Win%(adj)':>10} {'Avg Ret':>9} {'Avg Conf':>10}")
    print(f"  {'-'*61}")
    for style in ("intraday", "swing", "position"):
        sigs = [s for s in resolved if (s.style or "swing") == style]
        if not sigs:
            continue
        w_raw = sum(1 for s in sigs if _best_outcome(s) > 0)
        w_adj = sum(1 for s in sigs if _is_win(s))
        n = len(sigs)
        ac = sum(s.confidence for s in sigs) / n
        ar = sum(_best_outcome(s) for s in sigs) / n
        cost_drag = w_raw/n*100 - w_adj/n*100
        flag = f" ({cost_drag:+.1f}pp friction drag)" if cost_drag > 3 else ""
        print(f"  {style:<12} {n:>5} {w_raw/n*100:>9.1f}% {w_adj/n*100:>9.1f}% {ar:>+8.2f}% {ac:>9.1f}%{flag}")

    # ── confidence band calibration ───────────────────────────────────────────
    print(f"\n  CONFIDENCE BAND CALIBRATION  (friction-adjusted win%)")
    print(f"  {'Band':<12} {'N':>5} {'Win%(adj)':>10} {'Avg Conf':>10} {'Avg Ret':>9} {'Gap':>8}  {'Calibrated?'}")
    print(f"  {'-'*75}")
    for lo, hi in BANDS:
        sigs = [s for s in resolved if lo <= s.confidence < hi]
        if not sigs:
            continue
        w  = sum(1 for s in sigs if _is_win(s))
        n  = len(sigs)
        wr = w / n * 100
        ac = sum(s.confidence for s in sigs) / n
        ar = sum(_best_outcome(s) for s in sigs) / n
        g  = ac - wr
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

    print(f"\n  PER-TICKER (min 3 signals, sorted by friction-adj win%)")
    print(f"  {'Ticker':<8} {'N':>4} {'Win%raw':>8} {'Win%adj':>8} {'Avg Ret':>9} {'Gap':>8}")
    print(f"  {'-'*58}")
    rows_out = sorted(
        [(t, d) for t, d in ticker_stats.items() if d["n"] >= 3],
        key=lambda x: x[1]["w_adj"] / x[1]["n"],
        reverse=True,
    )
    for t, d in rows_out:
        n      = d["n"]
        wr_raw = d["w"]     / n * 100
        wr_adj = d["w_adj"] / n * 100
        ac     = d["conf"]  / n
        ar     = d["ret"]   / n
        g      = ac - wr_adj
        flag   = " ⚠" if abs(g) > 15 else ""
        print(f"  {t:<8} {n:>4} {wr_raw:>7.1f}% {wr_adj:>7.1f}% {ar:>+8.2f}% {g:>+7.1f}pp{flag}")

    # ── horizon comparison ────────────────────────────────────────────────────
    print(f"\n  WIN RATE BY OUTCOME HORIZON (signals that have each)")
    print(f"  {'Horizon':<12} {'N':>5} {'Win%':>7} {'Avg Ret':>9}")
    print(f"  {'-'*40}")
    for label, field in [("1-day", "outcome_1d"), ("3-day", "outcome_3d"),
                          ("7-day", "outcome_pct"), ("14-day", "outcome_14d")]:
        sigs = [s for s in rows if s.action in ("BUY","SELL") and getattr(s, field) is not None]
        if not sigs:
            continue
        w  = sum(1 for s in sigs if getattr(s, field) > 0)
        n  = len(sigs)
        ar = sum(getattr(s, field) for s in sigs) / n
        print(f"  {label:<12} {n:>5} {w/n*100:>6.1f}% {ar:>+8.2f}%")

    # ── top losses ────────────────────────────────────────────────────────────
    worst = sorted(resolved, key=lambda s: _best_outcome(s))[:8]
    print(f"\n  WORST SIGNALS")
    print(f"  {'Ticker':<7} {'Action':<6} {'Conf':>6} {'Ret':>8}  {'Date':<12}  {'Horizon used'}")
    print(f"  {'-'*60}")
    for s in worst:
        ret = _best_outcome(s)
        h = "14d" if s.outcome_14d is not None else "7d" if s.outcome_pct is not None else "3d" if s.outcome_3d is not None else "1d"
        dt = s.created_at.strftime("%Y-%m-%d") if s.created_at else "?"
        print(f"  {s.ticker:<7} {s.action:<6} {s.confidence:>5.1f}% {ret:>+7.2f}%  {dt}  ({h})")

    # ── top wins ──────────────────────────────────────────────────────────────
    best = sorted(resolved, key=lambda s: _best_outcome(s), reverse=True)[:8]
    print(f"\n  BEST SIGNALS")
    print(f"  {'Ticker':<7} {'Action':<6} {'Conf':>6} {'Ret':>8}  {'Date':<12}  {'Horizon used'}")
    print(f"  {'-'*60}")
    for s in best:
        ret = _best_outcome(s)
        h = "14d" if s.outcome_14d is not None else "7d" if s.outcome_pct is not None else "3d" if s.outcome_3d is not None else "1d"
        dt = s.created_at.strftime("%Y-%m-%d") if s.created_at else "?"
        print(f"  {s.ticker:<7} {s.action:<6} {s.confidence:>5.1f}% {ret:>+7.2f}%  {dt}  ({h})")

    # ── MAE / MFE / stop-target summary ─────────────────────────────────────
    mae_sigs = [s for s in rows if s.action in ("BUY","SELL") and getattr(s, "mae", None) is not None]
    if mae_sigs:
        n_mae = len(mae_sigs)
        n_stop   = sum(1 for s in mae_sigs if s.hit_stop)
        n_target = sum(1 for s in mae_sigs if s.hit_target)
        n_time   = sum(1 for s in mae_sigs if s.exit_type == "time")
        avg_mae  = sum(s.mae for s in mae_sigs) / n_mae
        avg_mfe  = sum(s.mfe for s in mae_sigs) / n_mae
        mfe_mae_ratio = avg_mfe / abs(avg_mae) if avg_mae != 0 else float("inf")

        print(f"\n  MAE / MFE TRADE-PATH ANALYTICS (n={n_mae})")
        print(f"  {'Metric':<30} {'Value'}")
        print(f"  {'-'*45}")
        print(f"  {'Signals w/ stop hit':<30} {n_stop} ({n_stop/n_mae*100:.1f}%)")
        print(f"  {'Signals w/ target hit':<30} {n_target} ({n_target/n_mae*100:.1f}%)")
        print(f"  {'Signals exited by time':<30} {n_time} ({n_time/n_mae*100:.1f}%)")
        print(f"  {'Avg MAE (worst drawdown)':<30} {avg_mae:+.2f}%")
        print(f"  {'Avg MFE (best excursion)':<30} {avg_mfe:+.2f}%")
        print(f"  {'MFE/MAE ratio':<30} {mfe_mae_ratio:.2f}×  (>1 = signals move right first)")

        if mfe_mae_ratio < 1.0:
            print(f"\n  ⚠  MFE/MAE < 1.0: signals move AGAINST position before recovering.")
            print(f"     Entries may be too early — consider waiting for confirmation.")
        elif mfe_mae_ratio > 2.5:
            print(f"\n  ✓  MFE/MAE > 2.5: signals strongly move right before any adverse excursion.")
            print(f"     Entry timing is good; ensure stops aren't too tight.")

        if n_stop / n_mae > 0.40:
            print(f"\n  ⚠  Stop hit rate {n_stop/n_mae*100:.0f}% > 40%. Stops may be too tight")
            print(f"     or entries are too aggressive. Consider ATR×3 stops.")
        if n_target / n_mae > 0.50:
            print(f"\n  ✓  Target hit rate {n_target/n_mae*100:.0f}% > 50%. Target placement is realistic.")

    print(f"\n{'='*62}\n")


# ── main ─────────────────────────────────────────────────────────────────────

async def main():
    print("\nStep 1 — Resolving pending outcomes…")
    updated = await resolve_outcomes()
    print(f"\nStep 1b — Computing MAE/MFE / stop-target tracking…")
    await resolve_mae_mfe()
    print(f"\nStep 2 — Running calibration report…")
    await calibration_report()


if __name__ == "__main__":
    asyncio.run(main())
