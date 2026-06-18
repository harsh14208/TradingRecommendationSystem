import logging
from sqlalchemy import select
from config import get_settings
from database import AsyncSessionLocal
from models import GateRegistry, SignalPolicy

log = logging.getLogger("signal.trade.policy")

# Define active gates in the system (TSYS-6b)
ACTIVE_GATES = {
    "ChronicLoserExclusion": {
        "owner": "quant_research",
        "status": "active",
        "test_coverage": 0.85,
        "live_validation_status": "validated",
        "retirement_criteria": "Disable if win rate improves above 45% for 3+ months",
    },
    "TrueOrthogonalityMinimum": {
        "owner": "quant_research",
        "status": "active",
        "test_coverage": 0.90,
        "live_validation_status": "validated",
        "retirement_criteria": "Disable if correlation between families changes",
    },
    "RvolGate": {
        "owner": "execution_team",
        "status": "active",
        "test_coverage": 0.95,
        "live_validation_status": "validated",
        "retirement_criteria": "Disable if average fill slippage rises above 5bps",
    },
    "AdxGate": {
        "owner": "quant_research",
        "status": "active",
        "test_coverage": 0.88,
        "live_validation_status": "validated",
        "retirement_criteria": "Retire if trend strength prediction fails",
    },
    "OverboughtWeakTrendGate": {
        "owner": "quant_research",
        "status": "active",
        "test_coverage": 0.92,
        "live_validation_status": "validated",
        "retirement_criteria": "Retire if win rate of mean reversion increases",
    },
    "DollarVolumeGate": {
        "owner": "execution_team",
        "status": "active",
        "test_coverage": 0.96,
        "live_validation_status": "validated",
        "retirement_criteria": "Always required for liquidity checks",
    },
}


def get_current_policy_version() -> str:
    """TSYS-6c: Derive unique signal policy version from current configuration."""
    # Hardcoded or hash of configuration options
    return "v10.5-A16"


async def initialize_policy_and_registry():
    """TSYS-6b & TSYS-6c: Populate gate registry and policy table in the database."""
    try:
        async with AsyncSessionLocal() as db:
            # 1. Register policy
            policy_ver = get_current_policy_version()
            stmt = select(SignalPolicy).where(SignalPolicy.version == policy_ver)
            res = await db.execute(stmt)
            policy = res.scalar_one_or_none()
            _min_conf = get_settings().min_confidence
            if not policy:
                policy = SignalPolicy(
                    version=policy_ver,
                    config={
                        "version": policy_ver,
                        "description": "Quant Engine v10.5 Active Policy Stack",
                        "gates": list(ACTIVE_GATES.keys()),
                        "min_confidence": _min_conf,
                    },
                )
                db.add(policy)
            else:
                # Keep the policy snapshot in sync with the live floor.
                _cfg = dict(policy.config or {})
                if _cfg.get("min_confidence") != _min_conf:
                    _cfg["min_confidence"] = _min_conf
                    policy.config = _cfg

            # 2. Register gates
            for gate_id, info in ACTIVE_GATES.items():
                stmt = select(GateRegistry).where(GateRegistry.id == gate_id)
                res = await db.execute(stmt)
                reg = res.scalar_one_or_none()
                if not reg:
                    reg = GateRegistry(
                        id=gate_id,
                        owner=info["owner"],
                        status=info["status"],
                        test_coverage=info["test_coverage"],
                        live_validation_status=info["live_validation_status"],
                        retirement_criteria=info["retirement_criteria"],
                    )
                    db.add(reg)

            await db.commit()
    except Exception as e:
        log.error(f"Failed to initialize policy/registry: {e}")
