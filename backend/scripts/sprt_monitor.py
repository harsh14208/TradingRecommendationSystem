#!/usr/bin/env python3
"""§99b — SPRT monitor: sequential probability ratio test for forward validation.

Computes the log-likelihood ratio over registered SPRT populations each run,
prints state (continue / accept H1 / accept H0) + trajectory.
Unit tests against known Wald boundary cases.

Reference: Wald (1945) Sequential Analysis.
"""

from __future__ import annotations

import math
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

# Allow imports from backend/
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from sqlalchemy import select

from database import AsyncSessionLocal
from models import ResearchExperiment, Signal


@dataclass(frozen=True)
class SPRTConfig:
    """Immutable SPRT hypothesis constants."""

    h0: float  # null hypothesis mean (%)
    h1: float  # alternative hypothesis mean (%)
    alpha: float  # type-I error rate
    beta: float  # type-II error rate
    sigma: float | None = None  # known population std dev (%); estimated from data if None

    @property
    def lower_boundary(self) -> float:
        """Wald lower boundary: log(beta / (1 - alpha))."""
        return math.log(self.beta / (1.0 - self.alpha))

    @property
    def upper_boundary(self) -> float:
        """Wald upper boundary: log((1 - beta) / alpha)."""
        return math.log((1.0 - self.beta) / self.alpha)


def _sprt_llr(obs: list[float], cfg: SPRTConfig) -> tuple[float, float | None]:
    """Compute cumulative log-likelihood ratio for a sequence of observations.

    Returns (llr, sigma_used).  Uses Gaussian LLR:
        LLR_n = (mu1 - mu0) / sigma^2 * sum(x_i - (mu1+mu0)/2)
    """
    if not obs:
        return 0.0, cfg.sigma

    sigma = cfg.sigma
    if sigma is None:
        # Estimate sigma from observations (conservative: uses running std)
        if len(obs) >= 2:
            mean = sum(obs) / len(obs)
            var = sum((x - mean) ** 2 for x in obs) / (len(obs) - 1)
            sigma = math.sqrt(var) if var > 0 else 1.0
        else:
            sigma = 1.0  # placeholder until N>=2

    mu0, mu1 = cfg.h0, cfg.h1
    llr = (mu1 - mu0) / (sigma**2) * sum(x - (mu0 + mu1) / 2.0 for x in obs)
    return llr, sigma


def sprt_decision(llr: float, cfg: SPRTConfig) -> Literal["continue", "accept_h1", "accept_h0"]:
    if llr >= cfg.upper_boundary:
        return "accept_h1"
    if llr <= cfg.lower_boundary:
        return "accept_h0"
    return "continue"


def fmt_sprt_state(cfg: SPRTConfig, n: int, llr: float, sigma: float | None) -> str:
    decision = sprt_decision(llr, cfg)
    lo, hi = cfg.lower_boundary, cfg.upper_boundary
    pct = 100.0 * (llr - lo) / (hi - lo) if hi != lo else 0.0
    sigma_str = f"σ={sigma:.2f}" if sigma else "σ=est"
    return (
        f"SPRT  H0={cfg.h0:+.2f}%  H1={cfg.h1:+.2f}%  α={cfg.alpha}  β={cfg.beta}  "
        f"{sigma_str}  n={n}  LLR={llr:+.3f}  "
        f"bounds=[{lo:+.3f}, {hi:+.3f}]  ({pct:.0f}%)  →  {decision}"
    )


async def run_sprt_for_experiment(exp_id: int) -> dict | None:
    """Fetch outcomes for a registered SPRT experiment and compute current state."""
    async with AsyncSessionLocal() as db:
        exp = await db.get(ResearchExperiment, exp_id)
        if exp is None:
            print(f"[sprt] Experiment {exp_id} not found")
            return None

        sprt_params = exp.sprt_params or {}
        if not sprt_params:
            print(f"[sprt] Experiment {exp_id} has no sprt_params — not an SPRT experiment")
            return None

        cfg = SPRTConfig(
            h0=float(sprt_params["h0"]),
            h1=float(sprt_params["h1"]),
            alpha=float(sprt_params["alpha"]),
            beta=float(sprt_params["beta"]),
            sigma=sprt_params.get("sigma"),
        )

        # Build population filter from experiment metadata
        pop = sprt_params.get("population", {})
        after_date = pop.get("after_date")
        action_filter = pop.get("action", "BUY")
        is_sent = pop.get("is_sent", True)

        stmt = select(Signal.outcome_pct).where(Signal.outcome_pct.isnot(None))
        if after_date:
            stmt = stmt.where(Signal.created_at >= datetime.fromisoformat(after_date))
        if action_filter:
            stmt = stmt.where(Signal.action == action_filter)
        if is_sent:
            stmt = stmt.where(Signal.is_sent == True)

        result = await db.execute(stmt)
        outcomes = [row[0] for row in result.all() if row[0] is not None]

        # Apply outcome transform if specified
        transform = sprt_params.get("outcome_transform", {})
        offset = transform.get("offset", 0.0)
        scale = transform.get("scale", 1.0)
        outcomes = [(o + offset) * scale for o in outcomes]

        llr, sigma_est = _sprt_llr(outcomes, cfg)
        decision = sprt_decision(llr, cfg)

        state = {
            "n": len(outcomes),
            "llr": round(llr, 6),
            "sigma": round(sigma_est, 4) if sigma_est else None,
            "decision": decision,
            "lower_boundary": round(cfg.lower_boundary, 4),
            "upper_boundary": round(cfg.upper_boundary, 4),
            "pct_of_upper": round(100.0 * (llr - cfg.lower_boundary) / (cfg.upper_boundary - cfg.lower_boundary), 1)
            if cfg.upper_boundary != cfg.lower_boundary
            else 0.0,
            "computed_at": datetime.now(timezone.utc).isoformat(),
        }

        # Persist state back to experiment row
        exp.sprt_state = state
        await db.commit()

        return state


async def run_all_sprts() -> None:
    """Evaluate every registered SPRT experiment."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(ResearchExperiment).where(ResearchExperiment.sprt_params.isnot(None)))
        experiments = result.scalars().all()

    print(f"=== SPRT Monitor — {len(experiments)} registered experiment(s) ===\n")
    for exp in experiments:
        state = await run_sprt_for_experiment(exp.id)
        if state is None:
            continue
        params = exp.sprt_params or {}
        cfg = SPRTConfig(
            h0=float(params["h0"]),
            h1=float(params["h1"]),
            alpha=float(params["alpha"]),
            beta=float(params["beta"]),
            sigma=params.get("sigma"),
        )
        print(f"[{exp.id}] {exp.hypothesis}")
        print(f"  {fmt_sprt_state(cfg, state['n'], state['llr'], state.get('sigma'))}")
        print()


# ── CLI ──────────────────────────────────────────────────────────────────────


async def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        exp_id = int(sys.argv[1])
        state = await run_sprt_for_experiment(exp_id)
        if state:
            print(state)
    else:
        await run_all_sprts()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
