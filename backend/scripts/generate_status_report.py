#!/usr/bin/env python3
"""
generate_status_report.py
Reads test-report.json (pytest-json-report) and coverage.json (coverage.py)
then writes INTEGRATION_STATUS.md to the repository root.

Usage:
    python scripts/generate_status_report.py [test-report.json] [coverage.json]
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent          # backend/scripts/
BACKEND_DIR = SCRIPT_DIR.parent                       # backend/
REPO_ROOT = BACKEND_DIR.parent                        # repo root
OUTPUT_FILE = REPO_ROOT / "INTEGRATION_STATUS.md"

DEFAULT_TEST_REPORT = BACKEND_DIR / "test-report.json"
DEFAULT_COVERAGE = BACKEND_DIR / "coverage.json"

# ---------------------------------------------------------------------------
# Feature grouping rules  (order matters — first match wins)
# ---------------------------------------------------------------------------

FEATURE_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("Authentication",      re.compile(r"test_routers_auth|test_auth", re.I)),
    ("Signal Engine",       re.compile(r"test_signal_engine|test_signal_scoring|test_signal_workers", re.I)),
    ("Scanner",             re.compile(r"test_scanner|test_services_scanner", re.I)),
    ("Telegram / Delivery", re.compile(r"test_telegram|test_delivery", re.I)),
    ("Billing",             re.compile(r"test_routers_billing", re.I)),
    ("Watchlist",           re.compile(r"test_routers_watchlist", re.I)),
    ("Quotes / Market",     re.compile(r"test_routers_quotes", re.I)),
    ("Technicals",          re.compile(r"test_technicals|test_services_technicals", re.I)),
    ("ML / Scoring",        re.compile(r"test_signal_ml|test_calibration", re.I)),
]

ALL_FEATURES = [name for name, _ in FEATURE_PATTERNS] + ["Other"]


def classify_nodeid(nodeid: str) -> str:
    """Return the feature bucket for a given pytest node id."""
    # nodeid looks like  tests/test_routers_auth.py::TestClass::test_foo
    filename = nodeid.split("::")[0].split("/")[-1]
    for feature, pattern in FEATURE_PATTERNS:
        if pattern.search(filename):
            return feature
    return "Other"


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def load_json(path: Path) -> Optional[dict]:
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def parse_test_report(data: dict) -> dict:
    """Extract summary and per-feature stats from pytest-json-report data."""
    summary = data.get("summary", {})
    total    = summary.get("total",   0)
    passed   = summary.get("passed",  0)
    failed   = summary.get("failed",  0)
    skipped  = summary.get("skipped", 0)
    duration = round(data.get("duration", 0.0), 2)

    # Per-feature accumulators: {feature: {tests, passed, failed, duration, errors}}
    features: dict[str, dict] = {
        f: {"tests": 0, "passed": 0, "failed": 0, "duration": 0.0, "errors": []}
        for f in ALL_FEATURES
    }

    for test in data.get("tests", []):
        feature = classify_nodeid(test.get("nodeid", ""))
        features[feature]["tests"] += 1
        features[feature]["duration"] += test.get("duration", 0.0)

        outcome = test.get("outcome", "")
        if outcome == "passed":
            features[feature]["passed"] += 1
        elif outcome in ("failed", "error"):
            features[feature]["failed"] += 1
            # Grab a short error message if present
            call = test.get("call", {})
            crash = call.get("crash", {})
            msg = crash.get("message", "")
            if msg:
                # Trim to one line
                features[feature]["errors"].append(msg.splitlines()[0][:120])
        # skipped counts don't affect feature status display

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "duration": duration,
        "features": features,
        "pipeline": "PASSED" if failed == 0 else "FAILED",
    }


def parse_coverage(data: dict) -> tuple[float, list[tuple[str, float, int]]]:
    """Return (overall_pct, [(module, pct, num_stmts), ...]) sorted by pct asc."""
    totals = data.get("totals", {})
    overall_pct = round(totals.get("percent_covered", 0.0), 1)

    files = data.get("files", {})
    modules: list[tuple[str, float, int]] = []
    for filepath, info in files.items():
        summary = info.get("summary", {})
        pct = round(summary.get("percent_covered", 0.0), 1)
        num_stmts = summary.get("num_statements", 0)
        # Use a clean module name
        name = Path(filepath).stem
        modules.append((name, pct, num_stmts))

    # Sort by coverage ascending (lowest first), take top 15 by line count
    modules.sort(key=lambda x: (-x[2], x[1]))   # largest files first
    top15 = modules[:15]
    top15.sort(key=lambda x: x[1])              # then sort by coverage ascending
    return overall_pct, top15


# ---------------------------------------------------------------------------
# Previous-run extraction
# ---------------------------------------------------------------------------

PREV_RE = re.compile(
    r"\|\s*Previous\s*\|\s*(?P<ts>[^|]+?)\s*\|\s*(?P<tests>\d+|N/A)\s*\|\s*(?P<cov>[\d.]+%?|N/A)\s*\|\s*(?P<status>PASSED|FAILED|N/A)\s*\|"
)
CURR_RE = re.compile(
    r"\|\s*Current\s*\|\s*(?P<ts>[^|]+?)\s*\|\s*(?P<tests>\d+|N/A)\s*\|\s*(?P<cov>[\d.]+%?|N/A)\s*\|\s*(?P<status>PASSED|FAILED|N/A)\s*\|"
)


def extract_previous_run(md_path: Path) -> Optional[dict]:
    """Read existing INTEGRATION_STATUS.md and pull out the current-run row
    so it becomes the 'previous' row on the next run."""
    try:
        text = md_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None

    m = CURR_RE.search(text)
    if not m:
        return None

    tests_str = m.group("tests").strip()
    cov_str   = m.group("cov").strip().rstrip("%")
    return {
        "timestamp": m.group("ts").strip(),
        "tests":     tests_str if tests_str != "N/A" else None,
        "coverage":  cov_str   if cov_str   != "N/A" else None,
        "status":    m.group("status").strip(),
    }


# ---------------------------------------------------------------------------
# Health delta
# ---------------------------------------------------------------------------

def health_delta(prev: Optional[dict], total: int, coverage: float, pipeline: str) -> tuple[str, str, str]:
    """Return (tests_delta, cov_delta, status_str)."""
    if prev is None:
        return "first run", "baseline", "—"

    # Tests delta
    try:
        prev_tests = int(prev["tests"])
        diff_tests = total - prev_tests
        tests_delta = f"+{diff_tests}" if diff_tests >= 0 else str(diff_tests)
    except (TypeError, ValueError):
        tests_delta = "N/A"

    # Coverage delta
    try:
        prev_cov = float(prev["coverage"])
        diff_cov = round(coverage - prev_cov, 1)
        cov_delta = f"+{diff_cov}%" if diff_cov >= 0 else f"{diff_cov}%"
    except (TypeError, ValueError):
        cov_delta = "N/A"

    # Status
    prev_status = prev.get("status", "N/A")
    if prev_status == "N/A":
        status_str = "—"
    elif prev_status == "FAILED" and pipeline == "PASSED":
        status_str = "Improved"
    elif prev_status == "PASSED" and pipeline == "FAILED":
        status_str = "Degraded"
    else:
        status_str = "Stable"

    return tests_delta, cov_delta, status_str


# ---------------------------------------------------------------------------
# Markdown generation
# ---------------------------------------------------------------------------

def feature_row(name: str, stats: dict) -> str:
    n        = stats["tests"]
    status   = "✅" if stats["failed"] == 0 else "❌"
    dur      = round(stats["duration"], 2)
    errors   = stats["errors"]
    err_str  = errors[0] if errors else "—"
    # Truncate long error strings in the cell
    if len(err_str) > 80:
        err_str = err_str[:77] + "..."
    return f"| {name} | {n} | {status} | {dur} | {err_str} |"


def generate_report(
    test_data: Optional[dict],
    cov_data:  Optional[dict],
    prev_run:  Optional[dict],
    now_str:   str,
    commit_sha: str,
) -> str:

    # ------------------------------------------------------------------
    # Build values — fall back to N/A when data is missing
    # ------------------------------------------------------------------
    if test_data is not None:
        stats    = parse_test_report(test_data)
        total    = stats["total"]
        passed   = stats["passed"]
        failed   = stats["failed"]
        skipped  = stats["skipped"]
        duration = stats["duration"]
        pipeline = stats["pipeline"]
        features = stats["features"]
    else:
        total = passed = failed = skipped = 0
        duration = 0.0
        pipeline = "FAILED"
        features = {f: {"tests": 0, "passed": 0, "failed": 0, "duration": 0.0, "errors": []} for f in ALL_FEATURES}

    if cov_data is not None:
        overall_cov, top15 = parse_coverage(cov_data)
    else:
        overall_cov = 0.0
        top15 = []

    tests_delta, cov_delta, status_str = health_delta(prev_run, total, overall_cov, pipeline)

    # Prev row values
    if prev_run:
        prev_ts     = prev_run["timestamp"]
        prev_tests  = prev_run["tests"]  or "N/A"
        prev_cov    = (prev_run["coverage"] + "%" if prev_run["coverage"] else "N/A")
        prev_status = prev_run["status"] or "N/A"
    else:
        prev_ts = prev_tests = prev_cov = prev_status = "N/A"

    # ------------------------------------------------------------------
    # Feature table rows
    # ------------------------------------------------------------------
    feature_rows = "\n".join(feature_row(name, features[name]) for name in ALL_FEATURES)

    # ------------------------------------------------------------------
    # Coverage table rows
    # ------------------------------------------------------------------
    if top15:
        cov_rows = "\n".join(f"| `{name}` | {pct}% |" for name, pct, _ in top15)
    else:
        cov_rows = "| *(no coverage data)* | N/A |"

    # ------------------------------------------------------------------
    # Assemble markdown
    # ------------------------------------------------------------------
    report = f"""\
# Integration Status Report

> Last updated: {now_str}
> Commit: `{commit_sha}`
> Pipeline: **{pipeline}**

## Summary
| Metric | Value |
|--------|-------|
| Total Tests | {total} |
| Passed | {passed} |
| Failed | {failed} |
| Skipped | {skipped} |
| Coverage | {overall_cov}% |
| Duration | {duration}s |

## Feature Breakdown
| Feature / Module | Tests | Status | Duration (s) | Errors |
|------------------|-------|--------|--------------|--------|
{feature_rows}

## Coverage Breakdown
| Module | Coverage |
|--------|----------|
{cov_rows}

## Trend
| Run | Timestamp | Tests | Coverage | Status |
|-----|-----------|-------|----------|--------|
| Current | {now_str} | {total} | {overall_cov}% | {pipeline} |
| Previous | {prev_ts} | {prev_tests} | {prev_cov} | {prev_status} |

### Health Delta
- Tests: {tests_delta} vs previous
- Coverage: {cov_delta} vs previous
- Status: {status_str}

---
*Generated automatically by `scripts/generate_status_report.py`*
"""
    return report


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    args = sys.argv[1:]
    test_report_path = Path(args[0]) if len(args) >= 1 else DEFAULT_TEST_REPORT
    coverage_path    = Path(args[1]) if len(args) >= 2 else DEFAULT_COVERAGE

    now_str    = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    commit_sha = os.environ.get("GITHUB_SHA", "local")

    # Load inputs (gracefully handle missing files)
    test_data = load_json(test_report_path)
    cov_data  = load_json(coverage_path)

    if test_data is None:
        print(f"[generate_status_report] WARNING: {test_report_path} not found or invalid — reporting N/A")
    if cov_data is None:
        print(f"[generate_status_report] WARNING: {coverage_path} not found or invalid — reporting N/A")

    # Extract previous run from existing report (for trend section)
    prev_run = extract_previous_run(OUTPUT_FILE)

    report = generate_report(test_data, cov_data, prev_run, now_str, commit_sha)

    OUTPUT_FILE.write_text(report, encoding="utf-8")
    print(f"[generate_status_report] Written → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
