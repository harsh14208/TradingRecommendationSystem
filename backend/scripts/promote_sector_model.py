"""
promote_sector_model.py

QENG-1c promotion checklist for sector-specific entry models (§117).

Activates a trained sector model in the database so that the blocked sector
(XLF/XLP/XLU/XLI) is unblocked in delivery gates and the engine MR floor.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from datetime import datetime, timedelta

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
sys.path.insert(0, _PARENT)

from database import AsyncSessionLocal
from models import ActionAuditLog, ModelRegistry, ResearchExperiment
from services.sector_ml_promotion import BLOCKED_SECTORS, cache_promoted_sectors
from sqlalchemy import select


async def promote_sector_model(args: argparse.Namespace) -> None:
    sector = args.sector.upper()
    if sector not in BLOCKED_SECTORS:
        print(f"Error: {sector} is not a blocked sector. Allowed: {sorted(BLOCKED_SECTORS)}")
        return

    if not args.model_id:
        print("Error: --model-id is required.")
        return
    if args.oos_auc is None:
        print("Error: --oos-auc is required.")
        return
    if args.cost_adjusted_sharpe is None:
        print("Error: --cost-adjusted-sharpe is required.")
        return
    if not args.rollback_plan:
        print("Error: --rollback-plan is required.")
        return
    if not args.expiration_days or args.expiration_days < 1:
        print("Error: --expiration-days must be ≥ 1.")
        return

    print(f"## QENG-1c: Sector Model Promotion Checklist for {sector}\n")

    async with AsyncSessionLocal() as db:
        res = await db.execute(select(ModelRegistry).where(ModelRegistry.model_id == args.model_id))
        model = res.scalar_one_or_none()

        if not model:
            print(f"Error: Model '{args.model_id}' not found in ModelRegistry. Train it first.")
            return

        if model.approval_decision == "approved" and model.is_active:
            print(f"Note: Model '{args.model_id}' is already active.")
        else:
            print(f"Verifying promotion checklist for model '{args.model_id}':")
            print("  [x] Registry entry exists")
            print(f"  [x] Sector: {sector}")
            print(f"  [x] OOS AUC: {args.oos_auc:.4f}")
            print(f"  [x] Cost-adjusted Sharpe: {args.cost_adjusted_sharpe:.4f}")
            print(f"  [x] Rollback plan: {args.rollback_plan}")

            if args.oos_auc < 0.55:
                print("\nError: Promotion REJECTED. Sector model OOS AUC must be ≥ 0.55.")
                return
            if args.cost_adjusted_sharpe <= 0:
                print("\nError: Promotion REJECTED. Cost-adjusted Sharpe must be positive.")
                return

            model.approval_decision = "approved"
            model.is_active = True
            print(f"\nModel '{args.model_id}' approved and activated.")

        retest_date = datetime.now() + timedelta(days=args.expiration_days)
        print(f"  [x] Retest date: {retest_date.strftime('%Y-%m-%d')} ({args.expiration_days} days)")

        # Idempotency check
        existing_exp = await db.execute(
            select(ResearchExperiment).where(
                ResearchExperiment.decision == "promoted",
                ResearchExperiment.promotion_status == "live",
                ResearchExperiment.search_space == {"model_id": args.model_id, "sector": sector},
            )
        )
        existing_exp = existing_exp.scalar_one_or_none()
        if existing_exp:
            print(f"\nNote: Live promotion experiment already exists (ID {existing_exp.id}).")
        else:
            exp = ResearchExperiment(
                experiment_type="ml_training",
                hypothesis=f"Sector model promotion: {args.model_id} for {sector}",
                universe={"sector": sector},
                data_version="1.0",
                search_space={"model_id": args.model_id, "sector": sector},
                number_of_trials=1,
                is_metrics={"oos_auc": args.oos_auc},
                oos_metrics={"cost_adjusted_sharpe": args.cost_adjusted_sharpe},
                dsr_pbo={"retest_date": retest_date.isoformat()},
                decision="promoted",
                promotion_status="live",
            )
            db.add(exp)
            print("\nCreated ResearchExperiment ID: pending commit")

        audit = ActionAuditLog(
            action="promote_sector_model",
            details={
                "model_id": args.model_id,
                "sector": sector,
                "oos_auc": args.oos_auc,
                "cost_adjusted_sharpe": args.cost_adjusted_sharpe,
                "rollback_plan": args.rollback_plan,
                "expiration_days": args.expiration_days,
                "retest_date": retest_date.isoformat(),
            },
        )
        db.add(audit)
        await db.commit()

        # Refresh in-memory cache so the next scan picks up the promotion immediately.
        from services.sector_ml_promotion import refresh_promoted_sectors

        promoted = await refresh_promoted_sectors(db)
        cache_promoted_sectors(promoted)
        print(f"\nSUCCESS: Sector {sector} is now promoted and unblocked.")
        print(f"Promoted sectors: {sorted(promoted)}")
        print(f"Audit Log ID: {audit.id}")


def main():
    parser = argparse.ArgumentParser(description="Promote a sector-specific entry model (§117).")
    parser.add_argument(
        "--sector", type=str, required=True, choices=sorted(BLOCKED_SECTORS), help="Sector ETF to promote"
    )
    parser.add_argument(
        "--model-id", type=str, required=True, help="ModelRegistry model_id (e.g. sector-entry-XLF-1234567890)"
    )
    parser.add_argument("--oos-auc", type=float, required=True, help="Out-of-sample AUC of the sector model")
    parser.add_argument(
        "--cost-adjusted-sharpe", type=float, required=True, help="Expected Sharpe ratio after transaction costs"
    )
    parser.add_argument(
        "--rollback-plan",
        type=str,
        required=True,
        help="How to roll back the sector block if live performance degrades",
    )
    parser.add_argument("--expiration-days", type=int, required=True, help="Days until retest/re-evaluation")
    args = parser.parse_args()
    asyncio.run(promote_sector_model(args))


if __name__ == "__main__":
    main()
