# ===== AI GENERATED: export_openapi =====
# Purpose: Regenerate the committed OpenAPI 3.1 contract snapshot
# Inputs: the FastAPI application
# Returns: writes backend/openapi.snapshot.json
# Flow:
# 1. Build the schema from the running app definition
# 2. Write stable, sorted JSON so diffs show real contract changes

import json
from pathlib import Path

from backend.main import app

SNAPSHOT_PATH = Path(__file__).resolve().parents[1] / "openapi.snapshot.json"


def render_schema() -> str:
    return json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"


def main() -> None:
    SNAPSHOT_PATH.write_text(render_schema(), encoding="utf-8")
    print(f"Wrote {SNAPSHOT_PATH}")


if __name__ == "__main__":
    main()
