#!/usr/bin/env python3
"""Build a per-ticker daily ORATS feature panel from raw FTP files.

Example:
    python scripts/build_orats_panel.py \
        --raw-dir data/cache_orats/raw \
        --output data/cache_orats/orats_panel.parquet \
        --start 2020-01-01 \
        --end 2024-12-31
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

from services.orats_data import build_orats_panel, save_orats_panel_to_db  # noqa: E402

log = logging.getLogger("signal.build_orats_panel")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def _parse_date(s: str) -> date:
    return date.fromisoformat(s)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build ORATS per-ticker feature panel")
    parser.add_argument("--raw-dir", required=True, help="Directory with ORATS_SMV_Strikes_YYYYMMDD.csv/.zip files")
    parser.add_argument("--output", default="data/cache_orats/orats_panel.parquet", help="Output parquet path")
    parser.add_argument("--start", type=_parse_date, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=_parse_date, help="End date (YYYY-MM-DD)")
    parser.add_argument("--save-to-db", action="store_true", help="Persist panel to PostgreSQL")
    args = parser.parse_args()

    panel = build_orats_panel(
        raw_dir=Path(args.raw_dir),
        output_path=Path(args.output),
        start_date=args.start,
        end_date=args.end,
    )
    print(f"Built panel: {len(panel):,} rows, {panel['ticker'].nunique():,} tickers, {panel['date'].nunique():,} dates")

    if args.save_to_db:
        inserted = asyncio.run(save_orats_panel_to_db(panel))
        print(f"Persisted {inserted:,} rows to orats_daily_features")


if __name__ == "__main__":
    main()
