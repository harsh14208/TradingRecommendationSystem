#!/usr/bin/env python3
"""§14 re-instatement — Pre-register the SPRT for the FRED macro-regime sizing dampener.

Context (LEARNINGS 2026-06-12): the 06-10 deletion of §14 delivery hard blocks
cited a −0.06 Sharpe A/B that ran while a FRED `realtime_start` bug had emptied
the panel. Two consistent working-panel reads (+0.02 pre-bug, +0.03 post-fix,
MaxDD −2.31%→−0.93%) support the gate. It returns to live as an L11 SIZING
dampener (0.75× extreme / 0.85× marginal+score<55, BUY only — never a block),
and this SPRT decides whether the deployment survives forward scrutiny.

Hypothesis direction: signals flagged by the dampener (fredRegimeDampener < 1.0)
should UNDERPERFORM clean-regime signals — that is what justifies sizing them
down. H1: flagged signals' net mean return is ≥ 0.5pp WORSE than the rest.

Run BEFORE reading any forward outcome data. Registration after peeking voids
the test.
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

FRED_REGIME_SPRT = {
    "h0": 0.0,  # null: flagged-regime signals perform no worse than the rest
    "h1": -0.5,  # alternative: flagged signals ≥ 0.5pp worse net mean return
    "alpha": 0.05,
    "beta": 0.05,
    "population": {
        "after_date": "2026-06-12T00:00:00+00:00",  # deploy date of the L11 dampener
        "action": "BUY",
        "is_sent": True,
        "sizing_tilt": "fred_regime_dampener",  # signals with fredRegimeDampener < 1.0
    },
    "outcome_transform": {
        "offset": 0.0,
        "scale": 1.0,
    },
    "metric": "net_mean_return_delta_flagged_vs_clean_pp",
    "evidence_basis": (
        "IS A/B with working panel: +0.03 Sharpe, MaxDD -2.31%->-0.93%, 22/217 blocked "
        "(2026-06-12, post realtime_start fix); consistent with pre-bug +0.02 read (2026-06-08). "
        "The intervening -0.06 'harmful' verdict (2026-06-10) is retracted: dead-panel measurement."
    ),
}


async def _ensure_registered(
    *,
    hypothesis: str,
    experiment_type: str,
    sprt_params: dict,
    data_version: str = "v14_fred_lagged",
) -> ResearchExperiment:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ResearchExperiment).where(
                ResearchExperiment.hypothesis == hypothesis,
                ResearchExperiment.experiment_type == experiment_type,
            )
        )
        exp = result.scalar_one_or_none()
        if exp is not None:
            print(f"[exists] ID={exp.id}  {hypothesis}")
            return exp

        exp = ResearchExperiment(
            experiment_type=experiment_type,
            hypothesis=hypothesis,
            data_version=data_version,
            sprt_params=sprt_params,
            sprt_state={"llr": 0.0, "n": 0, "decision": "continue"},
            decision="pending",
            git_sha=os.popen("git rev-parse HEAD").read().strip() or None,
        )
        db.add(exp)
        await db.commit()
        await db.refresh(exp)
        print(f"[registered] ID={exp.id}  {hypothesis}")
        return exp


async def main() -> None:
    print("=== §14 FRED Macro-Regime Dampener — SPRT Pre-Registration ===")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("WARNING: Any forward outcome observed before this timestamp voids the test.\n")

    await _ensure_registered(
        hypothesis=(
            "§14: BUY signals flagged by the FRED regime dampener (fredRegimeDampener<1.0) "
            "have net mean return ≥0.5pp WORSE than clean-regime BUYs (SPRT)"
        ),
        experiment_type="sprt",
        sprt_params=FRED_REGIME_SPRT,
    )

    print("\n✅ §14 SPRT hypothesis pre-registered.")
    print("Run `python scripts/sprt_monitor.py` to evaluate as forward signals resolve.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
