"""Recursively replace non-finite floats (NaN / ±Inf) with None.

Starlette's JSONResponse serializes with ``allow_nan=False``, so a single NaN/Inf
anywhere in a response payload raises
"Out of range float values are not JSON compliant" and 500s the endpoint. Any
endpoint that returns numbers computed from external feeds (market context, signal
rows, …) should run its payload through ``json_safe`` first.
"""

from __future__ import annotations

import math
from typing import Any

from starlette.responses import JSONResponse


def json_safe(obj: Any) -> Any:
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_safe(v) for v in obj]
    return obj


class SafeJSONResponse(JSONResponse):
    """JSONResponse that sanitizes non-finite floats before serializing.

    Use as a router/app ``default_response_class`` for endpoints whose payloads
    come from external feeds (market data, etc.) so a stray NaN/Inf can't 500 the
    request via Starlette's ``allow_nan=False`` encoder.
    """

    def render(self, content: Any) -> bytes:
        return super().render(json_safe(content))
