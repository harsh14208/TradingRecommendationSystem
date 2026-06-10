#!/usr/bin/env python3
"""
Backfill calibration map with net-of-friction win labels.

Usage:
    cd backend && python scripts/backfill_calibration_net_of_friction.py

Recomputes every resolved signal's win label as (outcome_pct - 0.50%) so the
calibration map trains on net profitability, not gross positivity. Writes the
new map to data/calibration.json and archives the old one.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("signal.trade.calibration.backfill")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

_DATA_DIR = Path(__file__).parent.parent / "data"
_CAL_FILE = _DATA_DIR / "calibration.json"
_CAL_ARCHIVE = _DATA_DIR / f"calibration_pre_netoffriction_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"


def _load_signals_sync() -> list[tuple]:
    """Load resolved signals from the SQLite/PostgreSQL DB synchronously."""
    db_url = os.environ.get("DATABASE_URL", "sqlite:///./trading.db")
    if db_url.startswith("sqlite"):
        import sqlite3

        conn = sqlite3.connect(db_url.replace("sqlite:///", ""))
        cur = conn.cursor()
        cur.execute(
            "SELECT action, confidence, outcome_pct, outcome_14d, outcome_7d, created_at FROM signals WHERE outcome_pct IS NOT NULL"
        )
        rows = cur.fetchall()
        conn.close()
        return rows
    else:
        import sqlalchemy as sa

        engine = sa.create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(
                sa.text(
                    "SELECT action, confidence, outcome_pct, outcome_14d, outcome_3d, created_at FROM signals WHERE outcome_pct IS NOT NULL"
                )
            )
            return [tuple(r) for r in result.fetchall()]


def _build_calibration_map(rows: list[tuple]) -> dict:
    """Rebuild calibration map with net-of-friction labels."""
    # Import calibration helpers from the service module
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))

    # run_calibration expects async DB rows; we synthesize the same shape
    synthetic_rows = []
    for action, conf, outcome_pct, outcome_14d, outcome_7d, created_at in rows:
        net_pct = (outcome_pct or 0.0) - 0.50
        win = 1 if (action == "BUY" and net_pct > 0) or (action == "SELL" and net_pct < 0) else 0
        synthetic_rows.append(
            {
                "action": action,
                "confidence": conf,
                "outcome_pct": outcome_pct,
                "outcome_14d": outcome_14d,
                "outcome_7d": outcome_7d,
                "created_at": created_at,
                "win": win,
            }
        )

    # We can't easily call run_calibration because it does DB access internally.
    # Instead, inline the core Platt/isotonic logic here.
    from collections import defaultdict

    samples = []
    for r in synthetic_rows:
        action = (r.get("action") or "").upper()
        pct = r.get("outcome_14d") if r.get("outcome_14d") is not None else r.get("outcome_7d")
        if pct is None:
            pct = r.get("outcome_pct")
        if pct is None or action not in ("BUY", "SELL"):
            continue
        net_pct = pct - 0.50
        win = 1 if (net_pct > 0 if action == "BUY" else net_pct < 0) else 0
        samples.append({"conf": r["confidence"], "win": win, "action": action})

    if not samples:
        log.error("No resolved signals found — cannot backfill calibration.")
        return {}

    log.info("Rebuilding calibration on %d net-of-friction samples", len(samples))

    # Global Platt bins
    _BIN_SIZE = 5
    bins: dict[int, dict] = defaultdict(lambda: {"wins": 0, "total": 0})
    for s in samples:
        b = max(0, min(95, (int(s["conf"]) // _BIN_SIZE) * _BIN_SIZE))
        bins[b]["total"] += 1
        bins[b]["wins"] += s["win"]

    cal_map: dict[str, object] = {}
    for b, bstats in sorted(bins.items()):
        n = bstats["total"]
        wr = bstats["wins"] / n if n > 0 else 0.5
        cal_map[str(b)] = {
            "win_rate": round(wr, 4),
            "n": n,
            "blend": round(min(0.97, n / 15), 3),
        }

    log.info("Calibration map rebuilt: %d bins", len(cal_map))
    return cal_map


def main() -> None:
    if _CAL_FILE.exists():
        shutil.copy2(_CAL_FILE, _CAL_ARCHIVE)
        log.info("Archived old calibration to %s", _CAL_ARCHIVE.name)

    rows = _load_signals_sync()
    if not rows:
        log.error("No resolved signals in DB — aborting.")
        return

    cal_map = _build_calibration_map(rows)
    if not cal_map:
        return

    # Merge with existing regime-specific curves if they exist
    if _CAL_ARCHIVE.exists():
        try:
            old = json.loads(_CAL_ARCHIVE.read_text())
            if "_regime" in old:
                cal_map["_regime"] = old["_regime"]
                log.info("Preserved existing regime-specific curves from old map")
        except Exception:
            pass

    cal_map["_backfilled_at"] = datetime.now(timezone.utc).isoformat()
    cal_map["_label_version"] = "net_of_friction_v1"

    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    _CAL_FILE.write_text(json.dumps(cal_map, indent=2))
    log.info("Wrote net-of-friction calibration map to %s", _CAL_FILE)

    # Summary: compare gross vs net win rate
    gross_wins = sum(1 for _, _, pct, _, _, _ in rows if pct and pct > 0)
    net_wins = sum(1 for _, _, pct, _, _, _ in rows if pct and (pct - 0.50) > 0)
    log.info(
        "Gross-positive: %d/%d (%.1f%%) → Net-of-friction: %d/%d (%.1f%%)",
        gross_wins,
        len(rows),
        gross_wins / len(rows) * 100,
        net_wins,
        len(rows),
        net_wins / len(rows) * 100,
    )


if __name__ == "__main__":
    main()
