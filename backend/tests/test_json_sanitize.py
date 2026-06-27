"""Tests for services/json_sanitize.py — non-finite float sanitization."""

from __future__ import annotations

import json
import math

from services.json_sanitize import SafeJSONResponse, json_safe


def test_json_safe_replaces_non_finite_nested():
    payload = {
        "macro": {"t10y": 4.1, "vix": math.nan, "ratio": math.inf},
        "breadth": {"pct": -math.inf},
        "cot": [{"z": math.nan}, {"z": 1.5}],
        "ok": "string",
    }
    clean = json_safe(payload)
    assert clean["macro"]["t10y"] == 4.1
    assert clean["macro"]["vix"] is None
    assert clean["macro"]["ratio"] is None
    assert clean["breadth"]["pct"] is None
    assert clean["cot"][0]["z"] is None
    assert clean["cot"][1]["z"] == 1.5
    assert clean["ok"] == "string"
    # The whole point: serializes under Starlette's allow_nan=False.
    json.dumps(clean, allow_nan=False)


def test_safe_json_response_renders_non_finite():
    # Would raise "Out of range float values are not JSON compliant" without the
    # sanitizing render override.
    body = SafeJSONResponse(content={"vix": math.nan, "spy": [math.inf, 2.0]}).body
    assert b"null" in body
    assert b"2.0" in body
