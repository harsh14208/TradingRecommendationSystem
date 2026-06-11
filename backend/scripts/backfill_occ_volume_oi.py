#!/usr/bin/env python3
"""§110a — Backfill OCC daily volume/OI panel (accumulate-forward).

Usage:
    cd backend && python scripts/backfill_occ_volume_oi.py [--start 2026-05-01] [--end 2026-06-11] [--tickers AAPL,MSFT,...]
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from datetime import date, timedelta
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from services.occ_volume_oi import build_occ_panel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("backfill_occ_volume_oi")


def _parse_date(s: str) -> date:
    return date.fromisoformat(s)


async def main() -> None:
    ap = argparse.ArgumentParser(description="Backfill OCC volume/OI panel")
    ap.add_argument("--start", type=_parse_date, default=date.today() - timedelta(days=30))
    ap.add_argument("--end", type=_parse_date, default=date.today())
    ap.add_argument("--tickers", type=str, default="", help="Comma-separated tickers (default: all)")
    args = ap.parse_args()

    tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()] or None
    log.info(f"Starting backfill: {args.start} to {args.end}, tickers={tickers}")
    panel = await build_occ_panel(tickers=tickers, start=args.start, end=args.end)
    log.info(f"Done: {len(panel)} rows")


if __name__ == "__main__":
    asyncio.run(main())
