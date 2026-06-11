#!/usr/bin/env python3
"""§104a — Backfill FINRA daily short-sale volume panel.

Usage:
    cd backend && python scripts/backfill_finra_short_volume.py [--start 2009-08-03] [--end 2026-06-11] [--tickers AAPL,MSFT,...]

Idempotent: skips already-downloaded date files in data/cache_finra_short_volume/.
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

from services.finra_short_volume import build_short_volume_panel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("backfill_finra_short_volume")


def _parse_date(s: str) -> date:
    return date.fromisoformat(s)


async def main() -> None:
    ap = argparse.ArgumentParser(description="Backfill FINRA short-sale volume panel")
    ap.add_argument("--start", type=_parse_date, default=date(2009, 8, 3))
    ap.add_argument("--end", type=_parse_date, default=date.today())
    ap.add_argument("--tickers", type=str, default="", help="Comma-separated tickers (default: all)")
    args = ap.parse_args()

    tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()] or None
    log.info(f"Starting backfill: {args.start} to {args.end}, tickers={tickers}")
    panel = await build_short_volume_panel(tickers=tickers, start=args.start, end=args.end)
    log.info(f"Done: {len(panel)} rows")


if __name__ == "__main__":
    asyncio.run(main())
