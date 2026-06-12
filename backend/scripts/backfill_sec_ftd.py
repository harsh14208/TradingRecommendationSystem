#!/usr/bin/env python3
"""§105a — Backfill SEC fails-to-deliver (FTD) panel.

Usage:
    cd backend && python scripts/backfill_sec_ftd.py [--start 2004-01-01] [--end 2026-06-11] [--tickers AAPL,MSFT,...]

Idempotent: skips already-downloaded month ZIPs in data/cache_sec_ftd/.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import date
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from services.sec_ftd import build_ftd_panel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("backfill_sec_ftd")


def _parse_date(s: str) -> date:
    return date.fromisoformat(s)


async def main() -> None:
    ap = argparse.ArgumentParser(description="Backfill SEC FTD panel")
    ap.add_argument("--start", type=_parse_date, default=date(2004, 1, 1))
    ap.add_argument("--end", type=_parse_date, default=date.today())
    ap.add_argument("--tickers", type=str, default="", help="Comma-separated tickers (default: IS universe)")
    ap.add_argument("--all-tickers", action="store_true", help="Backfill all symbols (slower)")
    args = ap.parse_args()

    if args.all_tickers:
        tickers = None
    elif args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()]
    else:
        # Default to IS universe for fast feature computation
        from scripts.backtest_technicals import TICKERS

        tickers = list(TICKERS)

    log.info(f"Starting backfill: {args.start} to {args.end}, tickers={len(tickers) if tickers else 'ALL'}")
    panel = await build_ftd_panel(tickers=tickers, start=args.start, end=args.end)
    log.info(f"Done: {len(panel)} rows")


if __name__ == "__main__":
    asyncio.run(main())
