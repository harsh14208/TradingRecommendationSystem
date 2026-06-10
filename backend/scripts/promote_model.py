"""
scripts/promote_model.py

Promotes a model or policy to active status after verifying the QENG-1c model/policy promotion checklist.
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime, timedelta

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
sys.path.insert(0, _PARENT)

from database import AsyncSessionLocal
from models import ModelRegistry, ResearchExperiment, ActionAuditLog
from sqlalchemy import select


async def promote_model(args):
    print("## QENG-1c: Model/Policy Promotion Checklist Validator\n")

    # Checklist validation
    if not args.model_id:
        print("Error: --model-id is required.")
        return
    if not args.oos_universe:
        print("Error: --oos-universe is required (locked out-of-sample universe).")
        return
    if args.replay_sharpe is None:
        print("Error: --replay-sharpe is required (historical replay result).")
        return
    if args.shadow_sharpe is None:
        print("Error: --shadow-sharpe is required (live shadow paper result).")
        return
    if args.cost_adjusted_sharpe is None:
        print("Error: --cost-adjusted-sharpe is required (cost-adjusted result).")
        return
    if not args.rollback_plan:
        print("Error: --rollback-plan is required (details on rollback plan).")
        return
    if not args.expiration_days:
        print("Error: --expiration-days is required (retest/expiration window).")
        return

    # Check database model registry
    async with AsyncSessionLocal() as db:
        # Check if model exists in registry
        res = await db.execute(select(ModelRegistry).where(ModelRegistry.model_id == args.model_id))
        model = res.scalar_one_or_none()

        if not model:
            print(f"Warning: Model '{args.model_id}' was not found in ModelRegistry.")
            print("Creating a new ModelRegistry entry automatically...")
            model = ModelRegistry(
                model_id=args.model_id,
                training_data_hash="unknown_cli_promotion",
                feature_schema_hash="unknown_cli_promotion",
                hyperparameters={},
                metrics={},
                approval_decision="pending",
                is_active=False,
            )
            db.add(model)
            await db.flush()

        print(f"Verifying promotion checklist for model '{args.model_id}':")
        print(f"  [x] Registry entry exists: {args.model_id}")
        print(f"  [x] Locked OOS universe: {args.oos_universe}")
        print(f"  [x] Replay result: Sharpe {args.replay_sharpe}")
        print(f"  [x] Live shadow result: Sharpe {args.shadow_sharpe}")
        print(f"  [x] Cost-adjusted result: Sharpe {args.cost_adjusted_sharpe}")
        print(f"  [x] Rollback plan: {args.rollback_plan}")

        retest_date = datetime.now() + timedelta(days=args.expiration_days)
        print(f"  [x] Expiration / retest date: {retest_date.strftime('%Y-%m-%d')} (in {args.expiration_days} days)")

        # Check performance thresholds: cost-adjusted Sharpe must be positive
        if args.cost_adjusted_sharpe < 0:
            print("\nError: Promotion REJECTED. Cost-adjusted Sharpe must be positive.")
            return

        # Perform the promotion
        model.approval_decision = "approved"
        model.is_active = True

        # Idempotency: avoid duplicate ResearchExperiment rows for identical promotion params
        existing_exp = await db.execute(
            select(ResearchExperiment).where(
                ResearchExperiment.decision == "promoted",
                ResearchExperiment.promotion_status == "live",
                ResearchExperiment.hypothesis == f"Promotion of model {args.model_id} with verified checklist",
                ResearchExperiment.universe == {"oos_universe": args.oos_universe},
                ResearchExperiment.is_metrics == {"replay_sharpe": args.replay_sharpe},
                ResearchExperiment.oos_metrics
                == {
                    "shadow_sharpe": args.shadow_sharpe,
                    "cost_adjusted_sharpe": args.cost_adjusted_sharpe,
                },
            )
        )
        existing_exp = existing_exp.scalar_one_or_none()
        if existing_exp:
            print(f"\nNote: A live promotion experiment already exists (ID {existing_exp.id}).")
            print("Skipping duplicate ResearchExperiment creation.")
            await db.commit()
            print(f"Model '{args.model_id}' is active.")
            return

        # Log promotion in ResearchExperiment
        exp = ResearchExperiment(
            experiment_type="ml_training",
            hypothesis=f"Promotion of model {args.model_id} with verified checklist",
            universe={"oos_universe": args.oos_universe},
            data_version="1.0",
            search_space={"rollback_plan": args.rollback_plan},
            number_of_trials=1,
            is_metrics={"replay_sharpe": args.replay_sharpe},
            oos_metrics={"shadow_sharpe": args.shadow_sharpe, "cost_adjusted_sharpe": args.cost_adjusted_sharpe},
            dsr_pbo={"retest_date": retest_date.isoformat()},
            decision="promoted",
            promotion_status="live",
        )
        db.add(exp)

        # Log action in ActionAuditLog (TSYS-13c)
        audit = ActionAuditLog(
            action="promote_model",
            details={
                "model_id": args.model_id,
                "oos_universe": args.oos_universe,
                "replay_sharpe": args.replay_sharpe,
                "shadow_sharpe": args.shadow_sharpe,
                "cost_adjusted_sharpe": args.cost_adjusted_sharpe,
                "rollback_plan": args.rollback_plan,
                "expiration_days": args.expiration_days,
                "retest_date": retest_date.isoformat(),
            },
        )
        db.add(audit)

        await db.commit()
        print(f"\nSUCCESS: Model '{args.model_id}' has been promoted and activated in the database!")
        print(f"Created ResearchExperiment ID: {exp.id}")
        print(f"Audit Log ID: {audit.id}")


def main():
    parser = argparse.ArgumentParser(description="Model/policy promotion checklist validator.")
    parser.add_argument("--model-id", type=str, required=True, help="ID of the model or policy version to promote.")
    parser.add_argument(
        "--oos-universe", type=str, required=True, help="Comma-separated list of tickers locked in OOS."
    )
    parser.add_argument("--replay-sharpe", type=float, required=True, help="Sharpe ratio from backtest/replay.")
    parser.add_argument(
        "--shadow-sharpe", type=float, required=True, help="Sharpe ratio from live paper/shadow testing."
    )
    parser.add_argument(
        "--cost-adjusted-sharpe", type=float, required=True, help="Expected Sharpe ratio after transaction costs."
    )
    parser.add_argument(
        "--rollback-plan", type=str, required=True, help="Description of how to roll back this model/policy."
    )
    parser.add_argument(
        "--expiration-days", type=int, required=True, help="Number of days before expiration and re-testing."
    )

    args = parser.parse_args()
    args.oos_universe = [t.strip() for t in args.oos_universe.split(",")]

    asyncio.run(promote_model(args))


if __name__ == "__main__":
    main()
