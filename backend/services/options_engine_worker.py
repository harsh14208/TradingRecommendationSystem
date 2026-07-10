"""Worker process for scoring one options universe.

Runs outside the main asyncio event loop so the heavy XGB/pandas work and its
ancillary async DB/Polygon calls do not pollute the main loop's asyncpg pool.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from services.options_engine import score_options_universe  # noqa: E402

log = logging.getLogger("signal.options_engine_worker")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--universe", required=True)
    ap.add_argument("--direction-parquet", required=True)
    ap.add_argument("--output-summary", required=True)
    ap.add_argument("--output-book", required=True)
    ap.add_argument(
        "--capital",
        type=float,
        default=0.0,
        help="account equity to size the book against; 0 → engine default (50k)",
    )
    args = ap.parse_args()

    direction_df = pd.read_parquet(args.direction_parquet)
    if direction_df.empty:
        direction_df = None

    score_kwargs = dict(
        universe=args.universe,
        direction_df=direction_df,
        fetch_missing_earnings=False,
    )
    if args.capital > 0:
        score_kwargs["capital"] = args.capital
    summary, _recs, book = score_options_universe(**score_kwargs)

    # Summary may contain numpy/pandas types; convert to plain JSON-serializable.
    clean_summary = {}
    for k, v in summary.items():
        if isinstance(v, (list, tuple)):
            clean_summary[k] = [float(x) if isinstance(x, (int, float)) else x for x in v]
        elif hasattr(v, "isoformat"):
            clean_summary[k] = v.isoformat()
        else:
            clean_summary[k] = v

    Path(args.output_summary).write_text(json.dumps(clean_summary))
    book.to_parquet(args.output_book, index=False)
    log.info("Worker wrote summary=%s book=%s rows=%d", args.output_summary, args.output_book, len(book))


if __name__ == "__main__":
    main()
