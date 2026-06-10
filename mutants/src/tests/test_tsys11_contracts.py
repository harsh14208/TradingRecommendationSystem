"""TSYS-11d: frontend↔backend API contract tests.

Two layers:
1. Inventory drift guard — every `/api/...` path the JSX frontend calls must map
   to a route registered on the FastAPI app. Catches a frontend calling a renamed
   or deleted endpoint (a class of bug invisible to per-router unit tests).
2. Shape checks — key endpoints the dashboard depends on return their expected
   top-level keys.

`main` is imported lazily inside the one test that needs the full app, and the
shape checks mount individual routers on a throwaway app — so this module has no
import-time side effects and does not trigger the main app lifespan.
"""

import re
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

_REPO = Path(__file__).resolve().parent.parent.parent
_JSX = list(_REPO.glob("*.jsx"))


def _frontend_api_paths() -> set[str]:
    paths: set[str] = set()
    pattern = re.compile(r"/api/[a-zA-Z0-9/_.-]+")
    for f in _JSX:
        for m in pattern.findall(f.read_text()):
            paths.add(m.rstrip("/"))
    return paths


@pytest.mark.skipif(not _JSX, reason="no JSX frontend files found")
def test_every_frontend_endpoint_is_registered():
    import main  # lazy: avoid import-time side effects during collection

    registered = {r.path.rstrip("/") for r in main.app.routes if hasattr(r, "path") and r.path.startswith("/api/")}
    registered_prefixes = set()
    for p in registered:
        registered_prefixes.add(p)
        registered_prefixes.add(re.sub(r"/\{[^}]+\}.*$", "", p))

    missing = []
    for fe in _frontend_api_paths():
        ok = any(fe == rp or fe.startswith(rp + "/") or rp.startswith(fe + "/") for rp in registered_prefixes)
        if not ok:
            missing.append(fe)
    assert not missing, f"frontend calls endpoints with no registered backend route: {sorted(missing)}"


# ── Shape checks (isolated mini-apps, no main lifespan) ──────────────────────


def _client_for(router) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_billing_plans_contract():
    from routers.billing import router

    resp = _client_for(router).get("/api/billing/plans")
    assert resp.status_code == 200
    plans = resp.json()
    assert isinstance(plans, list) and plans
    for plan in plans:
        assert {"id", "price"} <= set(plan.keys()), f"plan missing required keys: {plan}"


def test_version_info_contract():
    """TSYS-11c: version badge endpoint exposes the three explainability versions."""
    from routers.public import router

    resp = _client_for(router).get("/api/public/version-info")
    assert resp.status_code == 200
    data = resp.json()
    assert {"policy_version", "model_trained_at", "calibration_version"} == set(data.keys())


def test_metrics_endpoint_is_owner_gated():
    """/api/admin/metrics exists and rejects unauthenticated access (not 404)."""
    from routers.admin import router

    resp = _client_for(router).get("/api/admin/metrics")
    assert resp.status_code in (401, 403)
