#!/usr/bin/env python3
"""Build a per-ticker daily IV panel from Massive (Polygon) options flat files.

Same output schema as build_orats_panel.py — writes to the same `orats_daily_features`
table, so get_vol_view / the recommendation engine consume it unchanged. Uses the
Options-Starter day-agg flat files you already pay for (IV computed locally via BS).

Setup (one-time): get Flat-Files S3 keys at massive.com/dashboard/flat-files, then
    export MASSIVE_S3_KEY=...    MASSIVE_S3_SECRET=...

Examples:
    # 1) download the Aug-2024 vol-spike window (options + underlyings)
    python scripts/build_massive_options_panel.py --download --start 2024-07-15 --end 2024-09-15

    # 2) build the panel for your watchlist and persist to Postgres
    python scripts/build_massive_options_panel.py --build --universe-from-watchlist --save-to-db

    # download + build + save in one shot, full 2y:
    python scripts/build_massive_options_panel.py --download --build --save-to-db \
        --start 2024-06-18 --end 2026-06-17
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import date
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from services.massive_options_data import append_to_massive_panel, build_massive_panel, download_day_aggs  # noqa: E402
from services.orats_data import save_orats_panel_to_db  # noqa: E402

log = logging.getLogger("signal.build_massive_options_panel")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def _d(s: str) -> date:
    return date.fromisoformat(s)


def _watchlist_universe() -> set[str]:
    """The edge-bearing tickers — reuse the backtest universe so we only crunch names
    the VRP model actually scores (the raw flat files are whole-market)."""
    try:
        from scripts.backtest_technicals import TICKERS  # type: ignore

        return set(TICKERS)
    except Exception:
        log.warning("could not import backtest TICKERS — building whole-market (slow)")
        return set()


def main() -> None:
    ap = argparse.ArgumentParser(description="Build ORATS-compatible panel from Massive options flat files")
    ap.add_argument("--download", action="store_true", help="Download day-agg flat files from S3 first")
    ap.add_argument("--build", action="store_true", help="Build the panel from local flat files")
    ap.add_argument("--start", type=_d, help="Start date YYYY-MM-DD (for --download and as default build window)")
    ap.add_argument("--end", type=_d, help="End date YYYY-MM-DD (for --download and as default build window)")
    ap.add_argument("--build-start", type=_d, help="Override start date for building only (defaults to --start)")
    ap.add_argument("--build-end", type=_d, help="Override end date for building only (defaults to --end)")
    ap.add_argument(
        "--incremental",
        action="store_true",
        help="Merge new build dates into existing parquet instead of rebuilding everything",
    )
    ap.add_argument("--cache-dir", default="data/cache_massive", help="Where flat files live")
    ap.add_argument("--output", default="data/cache_massive/massive_panel.parquet")
    ap.add_argument("--universe-from-watchlist", action="store_true", help="Limit to backtest TICKERS")
    ap.add_argument("--save-to-db", action="store_true", help="Persist panel to orats_daily_features")
    args = ap.parse_args()

    cache = Path(args.cache_dir)

    if args.download:
        if not (args.start and args.end):
            ap.error("--download requires --start and --end")
        log.info("Downloading options + stock day-aggs %s → %s", args.start, args.end)
        opt = download_day_aggs(args.start, args.end, cache, kind="options")
        stk = download_day_aggs(args.start, args.end, cache, kind="stocks")
        log.info("Downloaded %d option files, %d stock files", len(opt), len(stk))

    if args.build:
        universe = _watchlist_universe() if args.universe_from_watchlist else None
        build_start = args.build_start or args.start
        build_end = args.build_end or args.end
        if args.incremental:
            panel = append_to_massive_panel(
                options_dir=cache / "options",
                stocks_dir=cache / "stocks",
                output_path=Path(args.output),
                universe=universe or None,
                start_date=build_start,
                end_date=build_end,
            )
        else:
            panel = build_massive_panel(
                options_dir=cache / "options",
                stocks_dir=cache / "stocks",
                output_path=Path(args.output),
                universe=universe or None,
                start_date=build_start,
                end_date=build_end,
            )
        print(
            f"Built panel: {len(panel):,} rows, {panel['ticker'].nunique():,} tickers, {panel['date'].nunique():,} dates"
        )
        if args.save_to_db:
            inserted = asyncio.run(save_orats_panel_to_db(panel))
            print(f"Persisted {inserted:,} rows to orats_daily_features")

    if not (args.download or args.build):
        ap.error("specify --download and/or --build")


if __name__ == "__main__":
    main()
