# ===== AI GENERATED: run_backend_module =====
# Purpose: Run a backend module from the repository's src layout.
# Inputs: Python module name and its command-line arguments.
# Returns: The module process exit status.
# Flow: Locate the workspace, add src to PYTHONPATH and run from the root.

"""Example: python tools/scripts/backend.py uvicorn backend.main:app --reload."""

import os
import subprocess
import sys
from pathlib import Path


def run_backend_module() -> int:
    """Preserve the caller's Python environment and root .env lookup."""
    if len(sys.argv) < 2:
        print("Usage: python tools/scripts/backend.py MODULE [ARGS...]")
        return 2
    workspace = Path(__file__).resolve().parents[2]
    environment = os.environ.copy()
    source_path = str(workspace / "src")
    existing_path = environment.get("PYTHONPATH", "")
    environment["PYTHONPATH"] = source_path + (os.pathsep + existing_path if existing_path else "")
    arguments = sys.argv[1:]
    if arguments[0] == "uvicorn" and not any(
        value in arguments for value in ("--proxy-headers", "--no-proxy-headers")
    ):
        # AI MODIFIED: Local Vite clients must not choose their apparent peer address.
        arguments = [*arguments, "--no-proxy-headers"]
    # Local operator CLI: arguments are intentionally supplied by the developer; no shell is used.
    return subprocess.call([sys.executable, "-m", *arguments], cwd=workspace, env=environment)  # noqa: S603


if __name__ == "__main__":
    raise SystemExit(run_backend_module())
