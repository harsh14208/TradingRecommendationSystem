import logging
from datetime import date
from sqlalchemy import select
from database import AsyncSessionLocal
from models import ProviderResponseSample, ProviderHealthScorecard, CorporateActionValidation, IncidentTimeline

log = logging.getLogger("signal.trade.reliability")


async def record_endpoint_call(
    provider: str,
    endpoint: str,
    latency_ms: float,
    status_code: int,
    response_body: str = "",
    ticker: str = None,
    is_stale: bool = False,
    is_drifted: bool = False,
    drift_details: str = None,
):
    """TSYS-5a & TSYS-5b: Record API call and update health scorecard, sampling response if needed."""
    try:
        # Sample raw response under certain conditions:
        # 1. Status code is error (not 200)
        # 2. Schema is drifted
        # 3. Random sampling (5% of successful requests)
        import random

        should_sample = (status_code != 200) or is_drifted or (random.random() < 0.05)

        async with AsyncSessionLocal() as db:
            if should_sample and response_body:
                # Truncate response body if it's too long
                body_to_store = response_body[:5000] if len(response_body) > 5000 else response_body
                sample = ProviderResponseSample(
                    provider=provider,
                    endpoint=endpoint,
                    ticker=ticker,
                    status_code=status_code,
                    latency_ms=latency_ms,
                    response_body=body_to_store,
                    is_drifted=is_drifted,
                    drift_details=drift_details,
                )
                db.add(sample)

            # Update Health Scorecard
            stmt = select(ProviderHealthScorecard).where(
                ProviderHealthScorecard.provider == provider, ProviderHealthScorecard.endpoint == endpoint
            )
            res = await db.execute(stmt)
            scorecard = res.scalar_one_or_none()

            error_val = 1 if status_code != 200 else 0
            stale_val = 1 if is_stale else 0
            drift_val = 1 if is_drifted else 0

            if not scorecard:
                scorecard = ProviderHealthScorecard(
                    provider=provider,
                    endpoint=endpoint,
                    latency_avg_ms=latency_ms,
                    error_rate=float(error_val),
                    stale_data_rate=float(stale_val),
                    schema_drift_count=drift_val,
                    health_score=100.0 - (error_val * 20 + stale_val * 10 + drift_val * 30),
                    is_active=True,
                )
                db.add(scorecard)
            else:
                # Exponential moving average for metrics
                alpha = 0.1
                scorecard.latency_avg_ms = (1 - alpha) * scorecard.latency_avg_ms + alpha * latency_ms
                scorecard.error_rate = (1 - alpha) * scorecard.error_rate + alpha * error_val
                scorecard.stale_data_rate = (1 - alpha) * scorecard.stale_data_rate + alpha * stale_val
                if is_drifted:
                    scorecard.schema_drift_count += 1

                # Calculate health score (0-100)
                # Penalize errors, latency (if > 1000ms), stale data, and drift incidents
                latency_penalty = max(0.0, (scorecard.latency_avg_ms - 500.0) / 50.0)  # penalize above 500ms
                error_penalty = scorecard.error_rate * 100.0
                stale_penalty = scorecard.stale_data_rate * 50.0
                drift_penalty = min(50.0, scorecard.schema_drift_count * 10.0)

                scorecard.health_score = max(
                    0.0, 100.0 - (error_penalty + stale_penalty + drift_penalty + latency_penalty)
                )
                # Auto degradation/deactivation if score drops too low
                if scorecard.health_score < 30.0 and scorecard.is_active:
                    scorecard.is_active = False
                    # Log incident timeline (TSYS-10a)
                    incident = IncidentTimeline(
                        event_type="provider_degradation",
                        severity="critical",
                        message=f"Provider {provider} endpoint {endpoint} health score dropped to {scorecard.health_score:.1f}. Endpoint marked inactive.",
                        details={"provider": provider, "endpoint": endpoint, "health_score": scorecard.health_score},
                    )
                    db.add(incident)

            await db.commit()
    except Exception as e:
        log.error(f"Failed to record endpoint call: {e}")


async def select_best_provider(endpoint: str, fallback_provider: str = "yfinance") -> str:
    """TSYS-5a: Automatic priority selection based on health scorecards."""
    try:
        async with AsyncSessionLocal() as db:
            stmt = (
                select(ProviderHealthScorecard)
                .where(ProviderHealthScorecard.endpoint == endpoint, ProviderHealthScorecard.is_active == True)
                .order_by(ProviderHealthScorecard.health_score.desc())
            )
            res = await db.execute(stmt)
            best = res.scalars().first()
            if best and best.health_score >= 50.0:
                return best.provider
    except Exception as e:
        log.error(f"Error selecting best provider: {e}")
    return fallback_provider


async def validate_corporate_actions(
    ticker: str, execution_date: date, polygon_value: float, yfinance_value: float, action_type: str
) -> bool:
    """TSYS-5c: Compare splits/dividends across providers and record discrepancy details."""
    try:
        is_valid = True
        discrepancy_details = None

        # Check if values differ significantly (more than 1% relative difference)
        diff = abs(polygon_value - yfinance_value)
        if polygon_value != 0:
            rel_diff = diff / polygon_value
        else:
            rel_diff = diff

        if rel_diff > 0.01:
            is_valid = False
            discrepancy_details = (
                f"Discrepancy: Polygon={polygon_value}, yfinance={yfinance_value} (diff={diff:.4f}, rel={rel_diff:.2%})"
            )

        async with AsyncSessionLocal() as db:
            val = CorporateActionValidation(
                ticker=ticker,
                action_type=action_type,
                execution_date=execution_date,
                polygon_value=polygon_value,
                yfinance_value=yfinance_value,
                is_valid=is_valid,
                discrepancy_details=discrepancy_details,
            )
            db.add(val)

            if not is_valid:
                # Log incident
                incident = IncidentTimeline(
                    event_type="corporate_action_discrepancy",
                    severity="warning",
                    message=f"Corporate action validation failed for {ticker} on {execution_date}: {discrepancy_details}",
                    details={
                        "ticker": ticker,
                        "action_type": action_type,
                        "date": str(execution_date),
                        "polygon": polygon_value,
                        "yfinance": yfinance_value,
                    },
                )
                db.add(incident)

            await db.commit()
        return is_valid
    except Exception as e:
        log.error(f"Failed to validate corporate action: {e}")
        return True


def detect_schema_drift(provider: str, endpoint: str, data: dict) -> tuple[bool, str]:
    """Simple check on key expected fields in responses to detect schema drift."""
    if provider == "polygon":
        if "aggs" in endpoint:
            expected = ["results", "ticker", "status"]
            missing = [k for k in expected if k not in data]
            if missing:
                return True, f"Missing fields: {missing}"
            if not isinstance(data.get("results"), list):
                return True, f"results field is not a list, got {type(data.get('results'))}"
        elif "snapshot" in endpoint:
            expected = ["status", "tickers"]
            missing = [k for k in expected if k not in data]
            if missing:
                return True, f"Missing fields: {missing}"
    return False, None
