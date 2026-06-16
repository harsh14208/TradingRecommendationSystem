"""Universe-expansion screen — rank uncovered S&P 500 large-caps by their
standalone 10-day MR backtest edge, to find Sharpe-neutral additions to the
live watchlist.

Candidate pool = current S&P 500 members NOT already in:
  • the live watchlist        (services scan universe)
  • backtest_technicals.TICKERS (IS edge-bearing set)
  • HELD_OUT_TICKERS           (OOS v6/v7/v8)
  • BLOCKED_TICKERS            (no MR edge)

For each candidate we run the exact IS MR-only pipeline (process_ticker →
simulate_ticker) and report per-ticker stats + the aggregate Sharpe of the
top-K basket, so additions can be chosen to hold the live Sharpe.

Usage:
    python scripts/screen_universe_expansion.py            # full sweep
    python scripts/screen_universe_expansion.py --min-n 5  # stricter N floor
"""

from __future__ import annotations

import asyncio
import csv
import os
import sys

import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.abspath(os.path.join(_HERE, ".."))
sys.path.insert(0, _PARENT)
sys.path.insert(0, _HERE)

import yfinance as yf  # noqa: E402

from backtest_technicals import (  # noqa: E402
    END,
    START,
    TICKERS as IS_TICKERS,
    HELD_OUT_TICKERS,
    fetch_spy_trend,
    fetch_stlfsi4,
    process_ticker,
    simulate_ticker,
    stats,
)


def _min_n() -> int:
    for i, a in enumerate(sys.argv):
        if a == "--min-n" and i + 1 < len(sys.argv):
            return int(sys.argv[i + 1])
    return 3


def _candidates() -> list[str]:
    from sqlalchemy import select

    from database import AsyncSessionLocal
    from models import WatchlistItem
    from services.delivery_gates import BLOCKED_TICKERS

    cur: set[str] = set()
    with open(os.path.join(_PARENT, "data", "sp500_ticker_start_end.csv")) as f:
        for r in csv.DictReader(f):
            if not (r["end_date"] or "").strip():
                cur.add(r["ticker"].strip().upper())

    async def _wl() -> set[str]:
        async with AsyncSessionLocal() as db:
            return {r.ticker.upper() for r in (await db.execute(select(WatchlistItem))).scalars().all()}

    wl = asyncio.run(_wl())
    covered = wl | {t.upper() for t in IS_TICKERS} | {t.upper() for t in HELD_OUT_TICKERS} | set(BLOCKED_TICKERS)
    # yfinance/Polygon want dash share-class tickers (BRK.B -> BRK-B).
    return sorted({c.replace(".", "-") for c in (cur - covered)})


def main() -> None:
    min_n = _min_n()
    cands = _candidates()
    print(f"# Universe-Expansion Screen — {len(cands)} uncovered S&P 500 large-caps")
    print(f"> MR-only 10d backtest, {START}→{END}, min N={min_n} for ranking\n")

    print("Fetching VIX / SPY trend / STLFSI4…", flush=True)
    try:
        vdf = yf.download("^VIX", start=START, end=END, interval="1d", auto_adjust=False, progress=False)
        if isinstance(vdf.columns, pd.MultiIndex):
            vdf.columns = vdf.columns.get_level_values(0)
        vix = {pd.Timestamp(str(k)[:10]): float(v) for k, v in vdf["Close"].items() if pd.notna(v)}
    except Exception:
        vix = {}
    spy_trend = fetch_spy_trend(START, END)
    _fred = os.getenv("FRED_API_KEY", "")
    if not _fred:
        try:
            with open(os.path.join(_PARENT, ".env")) as ef:
                for line in ef:
                    if line.startswith("FRED_API_KEY="):
                        _fred = line.strip().split("=", 1)[1]
        except Exception:
            pass
    stlfsi4 = fetch_stlfsi4(START, END, _fred)

    # ── Pre-warm OHLCV cache in the MAIN process (CRITICAL on macOS) ──────────
    # macOS fork() + network deadlocks: the SystemConfiguration proxy lookup that
    # requests/yfinance trigger is NOT fork-safe, so a forked worker that does a
    # fresh download hangs forever at 0% CPU. All yfinance downloads must happen
    # here, before forking; the Pool workers then read CSV cache only (no network).
    from backtest_technicals import cached_yf_download

    print(f"Pre-warming OHLCV cache for {len(cands)} tickers (main process, sequential)…", flush=True)
    warmed = 0
    for i, t in enumerate(cands, 1):
        try:
            df = cached_yf_download(t, start=START, end=END, interval="1d", auto_adjust=True, progress=False)
            if df is not None and not df.empty:
                warmed += 1
        except Exception as e:
            print(f"  {t}: warm failed ({e})", flush=True)
        if i % 25 == 0:
            print(f"  …{i}/{len(cands)} warmed ({warmed} ok)", flush=True)
    print(f"Pre-warm done: {warmed}/{len(cands)} cached.\n", flush=True)

    # Run SEQUENTIALLY (no multiprocessing). process_ticker also fetches earnings
    # dates over the network, and macOS fork() + network deadlocks even with OHLCV
    # pre-cached — so a fork Pool hangs at 0% CPU. The OHLCV cache is warm now, so
    # the only per-ticker network is the earnings fetch, which is fine in the main
    # process. ~272 × ~1-2s is tractable and deterministic.
    args = [(t, vix, spy_trend, stlfsi4, True, False, {}, False, False) for t in cands]
    print(f"Simulating {len(cands)} candidates (sequential)…\n", flush=True)
    results = []
    for i, a in enumerate(args, 1):
        results.append(process_ticker(a))
        if i % 25 == 0:
            print(f"  …{i}/{len(args)} simulated", flush=True)

    rows: list[dict] = []
    all_trades: list[pd.DataFrame] = []
    for ticker, _bh, ind_df, _ed in results:
        if ind_df is None or ind_df.empty:
            continue
        t_df = simulate_ticker(ticker, ind_df, vix, spy_trend, stlfsi4, mr_only=True)
        if t_df is None or t_df.empty:
            continue
        sv = stats(t_df["net_pct"].tolist())
        try:
            yrs = round((ind_df.index[-1] - ind_df.index[0]).days / 365.25, 1)
        except Exception:
            yrs = float("nan")
        rows.append({"ticker": ticker, "years": yrs, **sv})
        all_trades.append(t_df.assign(_tk=ticker))

    if not rows:
        print("No candidate produced MR trades.")
        return

    df = pd.DataFrame(rows)
    # stats() returns None for sharpe/pf on degenerate samples (e.g. zero-variance
    # or no losing trades) — coerce to numeric so NaN sorts last / fails the
    # basket filter, and format defensively.
    for c in ("n", "wr", "avg", "sharpe", "pf", "years"):
        if c in df:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    def _f(x, spec):
        return "—" if pd.isna(x) else format(x, spec)

    def _print_table(frame):
        print("| Rank | Ticker | Hist (yr) | N | WR | Avg Ret | Sharpe | PF |")
        print("|---:|:---|---:|---:|---:|---:|---:|---:|")
        for i, (_, r) in enumerate(frame.iterrows(), 1):
            print(
                f"| {i} | **{r['ticker']}** | {_f(r['years'], '.1f')} | {int(r['n'])} | {_f(r['wr'], '.0f')}% | "
                f"{_f(r['avg'], '+.2f')}% | {_f(r['sharpe'], '.2f')} | {_f(r['pf'], '.2f')} |"
            )

    ranked = df[df["n"] >= min_n].sort_values(["sharpe", "avg"], ascending=False, na_position="last")
    print(f"## Ranked candidates (N ≥ {min_n}) — {len(ranked)} of {len(rows)} simulated\n")
    _print_table(ranked)

    # ── Short-history names (<5yr; recent IPOs) ──────────────────────────────
    # These were under-represented at the N≥4 bar (younger ⇒ fewer 10d MR trades).
    # Surfaced separately with a relaxed N≥2 floor; flagged as low-confidence —
    # 2-3 trades over <5yr is barely an estimate, treat as a watch list only.
    short = df[(df["years"] < 5.0) & (df["n"] >= 2)].sort_values(["avg", "wr"], ascending=False, na_position="last")
    print(f"\n## Short-history candidates (<5yr history, N ≥ 2) — {len(short)} names")
    print("> ⚠ Low confidence: <5yr + 2-4 trades is mostly noise. Watch-list, not backtest-validated.\n")
    if len(short):
        _print_table(short)
    else:
        print("_None — no <5yr member produced ≥2 MR trades._")

    # Aggregate Sharpe of the positive-edge basket. Per-ticker Sharpe is undefined
    # at N=4-8, so select on the robust per-ticker stats (positive avg, WR≥50%,
    # PF≥1.5) and report the POOLED Sharpe — pooling restores enough N to estimate
    # it, and that pooled value is what "adding these holds Sharpe" actually means.
    keep = ranked[(ranked["avg"] > 0) & (ranked["wr"] >= 50.0) & (ranked["pf"] >= 1.5)]
    if len(keep):
        basket = pd.concat([t for t in all_trades if t["_tk"].iloc[0] in set(keep["ticker"])], ignore_index=True)
        bs = stats(basket["net_pct"].tolist())
        print(
            f"\n### Sharpe-neutral basket ({len(keep)} names, Sharpe ≥ 0.10)\n"
            f"> Pooled N={bs['n']}  WR={_f(bs['wr'], '.1f')}%  Avg={_f(bs['avg'], '+.2f')}%  "
            f"**Sharpe={_f(bs['sharpe'], '.2f')}**  PF={_f(bs['pf'], '.2f')}\n"
            f"> IS canon Sharpe ≈ 0.24–0.27; basket ≥ that ⇒ additions are Sharpe-neutral-or-better.\n"
        )
        print("ADD_CANDIDATES = " + ",".join(sorted(keep["ticker"])))


if __name__ == "__main__":
    main()
