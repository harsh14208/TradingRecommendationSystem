"""Promote the h=63 cross-sectional L/S model to live and record it in the registry.

This script implements the §111 research-promotion gate for the cross-sectional
alpha model.  It:

1. Verifies the persisted h=63 model artifact exists.
2. Activates cross-sectional sizing via services.cross_sectional_shadow.promote_to_live().
3. Creates/updates a ModelRegistry entry and a live ResearchExperiment record.
4. Logs the action to ActionAuditLog.

Usage:
    cd backend && python scripts/promote_cross_sectional_live.py
"""

from __future__ import annotations

import asyncio
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.dirname(_HERE)
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from database import AsyncSessionLocal
from models import ActionAuditLog, ModelRegistry, ResearchExperiment
from services.cross_sectional_shadow import promote_to_live
from sqlalchemy import select


_MODEL_ID = "cross_sectional_alpha_h63"
_OOS_UNIVERSE = "S&P 500 point-in-time constituents (sp500_ticker_start_end.csv)"
_REPLAY_SHARPE = 0.576
_SHADOW_SHARPE = 0.576
_COST_ADJUSTED_SHARPE = 0.547
_ROLLBACK_PLAN = (
    "Deactivate cross-sectional sizing (set services.cross_sectional_shadow._SHADOW_SIZING_ACTIVE "
    "to False), revert signal_engine.py comment, and remove CrossSectional from "
    "services.alpha_sleeves.VALIDATED_SLEEVE_METRICS. Retest horizon after 63 trading days."
)
_EXPIRATION_DAYS = 126  # ~2 quarters (h=63 rebasis)


async def _main() -> None:
    print("## §111 Cross-Sectional Alpha (h=63) Research Promotion\n")

    # 1. Verify artifact exists.
    model_path = os.path.join(_BACKEND, "data", "cross_sectional_model_h63.json")
    feat_path = os.path.join(_BACKEND, "data", "cross_sectional_features_h63.json")
    if not (os.path.exists(model_path) and os.path.exists(feat_path)):
        raise SystemExit(f"Missing h=63 model artifacts: {model_path} or {feat_path}")
    print(f"[x] h=63 model artifact exists: {model_path}")

    # 2. Activate live sizing.
    promo = promote_to_live(promotion_type="research")
    print(f"[x] Cross-sectional sizing activated: {promo}")

    async with AsyncSessionLocal() as db:
        # 3. ModelRegistry entry.
        res = await db.execute(select(ModelRegistry).where(ModelRegistry.model_id == _MODEL_ID))
        model = res.scalar_one_or_none()
        if model is None:
            model = ModelRegistry(
                model_id=_MODEL_ID,
                training_data_hash="sp500_pit_constituents_2012_2025",
                feature_schema_hash="price_features_zscore_h63",
                hyperparameters={"horizon": 63, "decile": 0.10, "cost_bps": 10},
                metrics={
                    "nested_sharpe": _REPLAY_SHARPE,
                    "walk_forward_h63_sharpe": _COST_ADJUSTED_SHARPE,
                    "sharpe_90ci": [0.22, 0.91],
                    "ann_ret_net": 0.0688,
                    "ann_vol": 0.1258,
                    "max_dd": -0.2371,
                },
                approval_decision="approved",
                is_active=False,
            )
            db.add(model)
            await db.flush()
            print(f"[x] Created ModelRegistry entry {_MODEL_ID}")
        model.approval_decision = "approved"
        model.is_active = True
        model.metrics = {
            "nested_sharpe": _REPLAY_SHARPE,
            "walk_forward_h63_sharpe": _COST_ADJUSTED_SHARPE,
            "sharpe_90ci": [0.22, 0.91],
            "ann_ret_net": 0.0688,
            "ann_vol": 0.1258,
            "max_dd": -0.2371,
        }

        # 4. ResearchExperiment record.
        existing = await db.execute(
            select(ResearchExperiment).where(
                ResearchExperiment.hypothesis == f"Promotion of model {_MODEL_ID} with verified checklist",
                ResearchExperiment.decision == "promoted",
            )
        )
        exp = existing.scalar_one_or_none()
        if exp is None:
            exp = ResearchExperiment(
                experiment_type="ml_training",
                hypothesis=f"Promotion of model {_MODEL_ID} with verified checklist",
                universe={"oos_universe": _OOS_UNIVERSE},
                data_version="1.0",
                search_space={"rollback_plan": _ROLLBACK_PLAN},
                number_of_trials=1,
                is_metrics={"replay_sharpe": _REPLAY_SHARPE},
                oos_metrics={
                    "shadow_sharpe": _SHADOW_SHARPE,
                    "cost_adjusted_sharpe": _COST_ADJUSTED_SHARPE,
                },
                decision="promoted",
                promotion_status="live",
            )
            db.add(exp)
            print("[x] Created live ResearchExperiment record")
        else:
            exp.promotion_status = "live"
            exp.oos_metrics = {
                "shadow_sharpe": _SHADOW_SHARPE,
                "cost_adjusted_sharpe": _COST_ADJUSTED_SHARPE,
            }
            print(f"[x] Updated existing ResearchExperiment record (ID {exp.id})")

        # 5. Audit log.
        audit = ActionAuditLog(
            action="model_promotion",
            details={
                "target_type": "model",
                "target_id": _MODEL_ID,
                "promotion_type": "research",
                "oos_universe": _OOS_UNIVERSE,
                "replay_sharpe": _REPLAY_SHARPE,
                "shadow_sharpe": _SHADOW_SHARPE,
                "cost_adjusted_sharpe": _COST_ADJUSTED_SHARPE,
                "rollback_plan": _ROLLBACK_PLAN,
                "expiration_days": _EXPIRATION_DAYS,
            },
        )
        db.add(audit)
        await db.commit()
        print(f"[x] Logged promotion to ActionAuditLog (ID {audit.id})")

    print("\n> Cross-sectional h=63 model is LIVE. Bottom-decile sizing haircut active.")
    print(f"> Retest/expiration: {_EXPIRATION_DAYS} days from today.")


if __name__ == "__main__":
    asyncio.run(_main())
