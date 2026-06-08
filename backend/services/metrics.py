"""TSYS-10c/10d: lightweight in-process metrics registry + Prometheus exposition.

Hand-rolled (no prometheus_client dependency). Counters monotonically increase;
gauges are set to an absolute value. `render_prometheus()` emits the standard
text exposition format consumable by Prometheus / OpenTelemetry collectors.

`check_alert_thresholds()` (TSYS-10d) compares counters/gauges against configured
thresholds and records an IncidentTimeline row + admin alert on breach.
"""

import logging
import threading
from typing import Optional

log = logging.getLogger("metrics")

_lock = threading.Lock()
# key = (metric_name, tuple(sorted(label_items))) → value
_counters: dict[tuple, float] = {}
_gauges: dict[tuple, float] = {}

# Help text for the known metrics (rendered as # HELP/# TYPE lines).
_HELP = {
    "scan_latency_seconds": ("gauge", "Most recent full-scan duration in seconds"),
    "delivery_latency_seconds": ("gauge", "Most recent signal delivery latency in seconds"),
    "provider_429_total": ("counter", "Provider HTTP 429 (rate-limit) responses"),
    "db_pool_saturation": ("gauge", "DB connection-pool in-use fraction [0,1]"),
    "cache_miss_total": ("counter", "Cache misses by cache name"),
    "order_error_total": ("counter", "Broker order errors"),
}


def _key(name: str, labels: Optional[dict]) -> tuple:
    return (name, tuple(sorted((labels or {}).items())))


def inc(name: str, value: float = 1.0, **labels) -> None:
    """Increment a counter (creating it at 0 first)."""
    k = _key(name, labels)
    with _lock:
        _counters[k] = _counters.get(k, 0.0) + value


def set_gauge(name: str, value: float, **labels) -> None:
    """Set a gauge to an absolute value."""
    k = _key(name, labels)
    with _lock:
        _gauges[k] = value


def snapshot() -> dict:
    """Return a flat {(\"name\", labels_tuple): value} copy for inspection/tests."""
    with _lock:
        return {"counters": dict(_counters), "gauges": dict(_gauges)}


def reset() -> None:
    """Test helper — clear all metrics."""
    with _lock:
        _counters.clear()
        _gauges.clear()


def _render_metric(name: str, series: list[tuple[tuple, float]], default_type: str) -> list[str]:
    mtype, help_text = _HELP.get(name, (default_type, name))
    lines = [f"# HELP {name} {help_text}", f"# TYPE {name} {mtype}"]
    for label_items, value in series:
        if label_items:
            label_str = ",".join(f'{k}="{v}"' for k, v in label_items)
            lines.append(f"{name}{{{label_str}}} {value}")
        else:
            lines.append(f"{name} {value}")
    return lines


def render_prometheus() -> str:
    """Render all metrics in Prometheus text exposition format."""
    with _lock:
        counters = list(_counters.items())
        gauges = list(_gauges.items())

    by_name: dict[str, list] = {}
    for (name, labels), value in counters:
        by_name.setdefault(("counter", name), []).append((labels, value))
    for (name, labels), value in gauges:
        by_name.setdefault(("gauge", name), []).append((labels, value))

    out: list[str] = []
    for (default_type, name), series in sorted(by_name.items(), key=lambda x: x[0][1]):
        out.extend(_render_metric(name, series, default_type))
    return "\n".join(out) + "\n"


# ── TSYS-10d alert thresholds ────────────────────────────────────────────────

# metric_name → (comparison, threshold, severity). "gt" fires when value > threshold.
_ALERT_THRESHOLDS: dict[str, tuple[str, float, str]] = {
    "provider_429_total": ("gt", 50, "warning"),
    "order_error_total": ("gt", 10, "critical"),
    "db_pool_saturation": ("gt", 0.9, "critical"),
    "scan_latency_seconds": ("gt", 120, "warning"),
}


def _breached(comparison: str, value: float, threshold: float) -> bool:
    return value > threshold if comparison == "gt" else value < threshold


async def check_alert_thresholds(db=None) -> list[dict]:
    """Compare current metrics against thresholds. Records an IncidentTimeline row
    (TSYS-10a) and fires a best-effort admin alert per breach. Returns the breaches."""
    snap = snapshot()
    # Aggregate counter series across labels to a single total per metric name.
    totals: dict[str, float] = {}
    for (name, _labels), value in snap["counters"].items():
        totals[name] = totals.get(name, 0.0) + value
    for (name, _labels), value in snap["gauges"].items():
        totals[name] = max(totals.get(name, 0.0), value)

    breaches = []
    for metric, (comparison, threshold, severity) in _ALERT_THRESHOLDS.items():
        value = totals.get(metric)
        if value is None or not _breached(comparison, value, threshold):
            continue
        breach = {"metric": metric, "value": value, "threshold": threshold, "severity": severity}
        breaches.append(breach)
        log.warning("metrics: ALERT %s=%s breached threshold %s (%s)", metric, value, threshold, severity)
        if db is not None:
            try:
                from models import IncidentTimeline

                db.add(
                    IncidentTimeline(
                        event_type="metric_threshold_breach",
                        severity=severity,
                        message=f"{metric}={value} breached {comparison} {threshold}",
                        details=breach,
                    )
                )
                await db.flush()
            except Exception as e:  # pragma: no cover
                log.warning("metrics: failed to record breach incident: %s", e)
    return breaches
