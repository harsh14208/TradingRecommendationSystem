#!/usr/bin/env python3
"""§99a — Pre-register SPRT hypotheses before any post-fix outcome resolves.

Lock in constants: H0 net/trade ≤ 0 vs H1 ≥ +1.0%, α=β=0.05,
population = post-2026-06-10 resolved delivered BUYs,
outcome = outcome_pct − 0.5.

Persist to ResearchExperiment registry with frozen timestamp.
Registration after peeking voids the test — run this BEFORE the first
post-fix signal resolves.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from sqlalchemy import select

from database import AsyncSessionLocal
from models import ResearchExperiment


SPRIT_SPEC = {
    "h0": 0.0,  # null: net mean return ≤ 0%
    "h1": 1.0,  # alternative: net mean return ≥ +1.0%
    "alpha": 0.05,
    "beta": 0.05,
    "population": {
        "after_date": "2026-06-10T15:56:00+00:00",  # post-fix restart
        "action": "BUY",
        "is_sent": True,
    },
    "outcome_transform": {
        "offset": -0.5,  # outcome_pct − 0.5 (net of friction proxy)
        "scale": 1.0,
    },
}

SHADOW_PROMOTION_SPRT = {
    "h0": 0.0,
    "h1": 3.0,  # bottom-decile WR delta ≥ 3pp
    "alpha": 0.05,
    "beta": 0.05,
    "population": {
        "after_date": "2026-06-10T15:56:00+00:00",
        "action": "BUY",
        "is_sent": True,
    },
    "outcome_transform": {
        "offset": 0.0,
        "scale": 1.0,
    },
    "metric": "bottom_decile_wr_delta_pp",
}

OOS_V7_PROMOTION_SPRT = {
    "h0": 0.0,
    "h1": 0.10,  # OOS Sharpe ≥ 0.10
    "alpha": 0.05,
    "beta": 0.05,
    "population": {
        "after_date": "2026-06-10T15:56:00+00:00",
        "action": "BUY",
        "is_sent": True,
        "oos_universe": ["SYK", "RMD", "IDXX", "ZBH", "RL", "DECK", "POOL", "NDAQ", "CBOE", "BR"],
    },
    "outcome_transform": {
        "offset": 0.0,
        "scale": 1.0,
    },
    "metric": "oos_sharpe",
}

OOS_V8_PROMOTION_SPRT = {
    "h0": 0.0,
    "h1": 0.10,
    "alpha": 0.05,
    "beta": 0.05,
    "population": {
        "after_date": "2026-06-10T15:56:00+00:00",
        "action": "BUY",
        "is_sent": True,
        "oos_universe": ["LNC", "AMG", "PAYC", "SIG", "AEO"],
    },
    "outcome_transform": {
        "offset": 0.0,
        "scale": 1.0,
    },
    "metric": "oos_sharpe",
}


async def _ensure_registered(
    hypothesis: str,
    experiment_type: str,
    sprt_params: dict,
    data_version: str = "v10.9",
) -> ResearchExperiment | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ResearchExperiment).where(
                ResearchExperiment.hypothesis == hypothesis,
                ResearchExperiment.experiment_type == experiment_type,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            print(f"[skip] Already registered: {hypothesis}")
            return existing

        exp = ResearchExperiment(
            experiment_type=experiment_type,
            hypothesis=hypothesis,
            data_version=data_version,
            sprt_params=sprt_params,
            decision="pending",
            promotion_status="pending",
        )
        db.add(exp)
        await db.commit()
        await db.refresh(exp)
        print(f"[registered] ID={exp.id}  {hypothesis}")
        return exp


async def main() -> None:
    print("=== §99a SPRT Pre-Registration ===")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("WARNING: Any post-fix outcome observed before this timestamp voids the test.\n")

    # §99a — Main forward-validation SPRT
    await _ensure_registered(
        hypothesis="§99a: Forward validation of post-fix BUY net mean return (SPRT)",
        experiment_type="sprt",
        sprt_params=SPRIT_SPEC,
    )

    # §99c — Shadow promotion SPRT
    await _ensure_registered(
        hypothesis="§99c-1: Shadow promotion bottom-decile WR delta (SPRT)",
        experiment_type="sprt",
        sprt_params=SHADOW_PROMOTION_SPRT,
    )

    # §99c — OOS v7 promotion SPRT
    await _ensure_registered(
        hypothesis="§99c-2: OOS v7 ticker promotion Sharpe (SPRT)",
        experiment_type="sprt",
        sprt_params=OOS_V7_PROMOTION_SPRT,
    )

    # §99c — OOS v8 promotion SPRT
    await _ensure_registered(
        hypothesis="§99c-3: OOS v8 ticker promotion Sharpe (SPRT)",
        experiment_type="sprt",
        sprt_params=OOS_V8_PROMOTION_SPRT,
    )

    # §101 — TSMOM sleeve SPRT
    await _ensure_registered(
        hypothesis="TSMOM sleeve forward Sharpe >= 0.3 vs H0 <= 0",
        experiment_type="tsmom_sleeve",
        sprt_params={
            "h0": 0.0,
            "h1": round(0.3 / 12, 6),
            "alpha": 0.05,
            "beta": 0.05,
            "population": {"source": "tsmom_monthly_csv"},
        },
        data_version="v101",
    )

    print("\n✅ All SPRT hypotheses pre-registered.")
    print("Run `python scripts/sprt_monitor.py` to evaluate.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
