# ===== AI GENERATED: test_contract_snapshot =====
# Purpose: Provider-side contract test; the committed OpenAPI file must match the app
# Inputs: backend/openapi.snapshot.json and the live schema
# Returns: pass/fail
# Flow:
# 1. Render the live schema
# 2. Compare with the committed snapshot; drift fails the build

from backend.scripts.export_openapi import SNAPSHOT_PATH, render_schema


def test_committed_openapi_snapshot_matches_the_application() -> None:
    assert SNAPSHOT_PATH.exists(), "run: python -m backend.scripts.export_openapi"
    assert (
        SNAPSHOT_PATH.read_text(encoding="utf-8") == render_schema()
    ), "API contract changed; regenerate with: python -m backend.scripts.export_openapi"
