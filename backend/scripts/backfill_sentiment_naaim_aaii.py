#!/usr/bin/env python3
"""§106a — Backfill sentiment panels (FRED UMCSENT primary + optional NAAIM/AAII).

Usage:
    cd backend && python scripts/backfill_sentiment_naaim_aaii.py
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from services.sentiment_naaim_aaii import (
    download_umcsent_panel,
    download_naaim_panel,
    download_aaii_panel,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("backfill_sentiment_naaim_aaii")


async def main() -> None:
    log.info("Downloading UMCSENT panel (FRED primary)...")
    umcsent = await download_umcsent_panel()
    if umcsent is not None:
        log.info(f"UMCSENT: {len(umcsent)} rows  ({umcsent['date'].min()} to {umcsent['date'].max()})")
    else:
        log.warning("UMCSENT: download failed (FRED_API_KEY set?)")

    log.info("Downloading NAAIM panel (optional)...")
    naaim = await download_naaim_panel()
    if naaim is not None:
        log.info(f"NAAIM: {len(naaim)} rows")
    else:
        log.info("NAAIM: unavailable (endpoint may be blocked)")

    log.info("Downloading AAII panel (optional)...")
    aaii = await download_aaii_panel()
    if aaii is not None:
        log.info(f"AAII: {len(aaii)} rows")
    else:
        log.info("AAII: unavailable (endpoint may be blocked)")

    log.info("Done.")


if __name__ == "__main__":
    asyncio.run(main())
