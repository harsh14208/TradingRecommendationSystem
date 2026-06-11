#!/usr/bin/env python3
"""§104c / §105c — Pre-register SPRT hypotheses for alt-data sizing tilts.

Run this BEFORE the backtest A/B produces outcomes. Registration after
peeking voids the test.

Each SPRT monitors forward-validation performance of a single alt-data
sizing tilt deployed to the live gate.  The backtest A/B (IS 2009-2024)
decides whether to deploy; the SPRT decides whether the deployment
survives forward scrutiny.
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


# ── §104: FINRA short-volume squeeze-fuel sizing tilt ───────────────────────
# Mechanism: elevated short volume + falling 5d delta = squeeze fuel.
# Hypothesis: sizing up on this condition adds ≥ +0.75% net mean return
# per trade versus the baseline open-entry book.
FINRA_SV_SPRT = {
    "h0": 0.0,  # null: tilt adds ≤ 0 net mean return
    "h1": 0.75,  # alternative: tilt adds ≥ +0.75% net mean return
    "alpha": 0.05,
    "beta": 0.05,
    "population": {
        "after_date": "2026-06-15T00:00:00+00:00",  # deploy after backfill + A/B
        "action": "BUY",
        "is_sent": True,
        "sizing_tilt": "finra_sv_squeeze_fuel",
    },
    "outcome_transform": {
        "offset": -0.5,
        "scale": 1.0,
    },
    "metric": "net_mean_return_delta_vs_baseline_pp",
}

# ── §105: SEC FTD settlement-stress sizing tilt ─────────────────────────────
# Mechanism: FTD shares in top quintile of own-history = settlement stress
# = genuine dislocation (size up), not value trap.
# Hypothesis: sizing up on this condition adds ≥ +0.75% net mean return
# per trade versus the baseline open-entry book.
SEC_FTD_SPRT = {
    "h0": 0.0,
    "h1": 0.75,
    "alpha": 0.05,
    "beta": 0.05,
    "population": {
        "after_date": "2026-06-15T00:00:00+00:00",
        "action": "BUY",
        "is_sent": True,
        "sizing_tilt": "sec_ftd_dislocation",
    },
    "outcome_transform": {
        "offset": -0.5,
        "scale": 1.0,
    },
    "metric": "net_mean_return_delta_vs_baseline_pp",
}


async def _ensure_registered(
    *,
    hypothesis: str,
    experiment_type: str,
    sprt_params: dict,
    data_version: str = "v104_v105",
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
    print("=== §104c / §105c — Alt-Data SPRT Pre-Registration ===")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("WARNING: Any backtest A/B outcome observed before this timestamp voids the test.\n")

    await _ensure_registered(
        hypothesis="§104c: FINRA short-volume squeeze-fuel sizing tilt adds ≥ +0.75pp net mean return vs baseline (SPRT)",
        experiment_type="sprt",
        sprt_params=FINRA_SV_SPRT,
    )

    await _ensure_registered(
        hypothesis="§105c: SEC FTD settlement-stress sizing tilt adds ≥ +0.75pp net mean return vs baseline (SPRT)",
        experiment_type="sprt",
        sprt_params=SEC_FTD_SPRT,
    )

    print("\n✅ All alt-data SPRT hypotheses pre-registered.")
    print("Run `python scripts/sprt_monitor.py` to evaluate after deployment.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
