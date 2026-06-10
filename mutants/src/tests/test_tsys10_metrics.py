"""TSYS-10c/10d: metrics registry, Prometheus rendering, alert thresholds."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from services import metrics


@pytest.fixture(autouse=True)
def _clean_metrics():
    metrics.reset()
    yield
    metrics.reset()


def test_counter_increments_and_accumulates():
    metrics.inc("provider_429_total", provider="polygon")
    metrics.inc("provider_429_total", provider="polygon", value=2)
    snap = metrics.snapshot()
    assert snap["counters"][("provider_429_total", (("provider", "polygon"),))] == 3


def test_gauge_sets_absolute_value():
    metrics.set_gauge("db_pool_saturation", 0.4)
    metrics.set_gauge("db_pool_saturation", 0.7)
    snap = metrics.snapshot()
    assert snap["gauges"][("db_pool_saturation", ())] == 0.7


def test_render_prometheus_format():
    metrics.inc("order_error_total", broker="alpaca")
    metrics.set_gauge("scan_latency_seconds", 12.5)
    out = metrics.render_prometheus()
    assert "# TYPE order_error_total counter" in out
    assert 'order_error_total{broker="alpaca"} 1.0' in out
    assert "# TYPE scan_latency_seconds gauge" in out
    assert "scan_latency_seconds 12.5" in out
    assert out.endswith("\n")


@pytest.mark.asyncio
async def test_check_alert_thresholds_fires_and_records_incident():
    # 11 order errors > threshold of 10 → critical breach.
    for _ in range(11):
        metrics.inc("order_error_total", broker="alpaca")

    db = AsyncMock()
    db.add = MagicMock()
    db.flush = AsyncMock()
    breaches = await metrics.check_alert_thresholds(db)

    assert any(b["metric"] == "order_error_total" and b["severity"] == "critical" for b in breaches)
    db.add.assert_called()  # IncidentTimeline recorded


@pytest.mark.asyncio
async def test_check_alert_thresholds_no_breach_when_under():
    metrics.inc("order_error_total", value=3)
    breaches = await metrics.check_alert_thresholds(db=None)
    assert breaches == []


@pytest.mark.asyncio
async def test_counter_totals_aggregate_across_labels_for_thresholds():
    # Two providers, 30 each = 60 total > 50 warning threshold.
    metrics.inc("provider_429_total", value=30, provider="polygon")
    metrics.inc("provider_429_total", value=30, provider="yfinance")
    breaches = await metrics.check_alert_thresholds(db=None)
    assert any(b["metric"] == "provider_429_total" for b in breaches)
