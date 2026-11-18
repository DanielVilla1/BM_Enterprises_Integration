# ===== AI GENERATED: verify_isolated_postgres =====
# Purpose: Run the backend suite in a disposable database, leaving the app database untouched.
# Inputs: Local development connection settings and optional --load flag.
# Returns: Pytest exit status; the specifically created scratch database is removed afterward.
# Flow: Validate host/name; create scratch DB; run child tests; close and drop only that DB.

import argparse
import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify PostgreSQL using a new disposable local database.")
    parser.add_argument(
        "--load", action="store_true", help="Include the 30-second, 10 requests/second load check."
    )
    parser.add_argument("--tests", nargs="*", default=[], help="Optional affected pytest paths.")
    arguments = parser.parse_args()
    workspace = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(workspace / "src"))
    from backend.src.config import get_settings

    settings = get_settings()
    address = make_url(settings.database_url)
    if settings.environment.lower() not in {"development", "test", "presentation"}:
        raise SystemExit("This verification runner is restricted to development/test/presentation.")
    if address.get_backend_name() != "postgresql" or address.host not in {
        "db",
        "localhost",
        "127.0.0.1",
        "::1",
    }:
        raise SystemExit("Use a local PostgreSQL development server.")
    scratch_name = "bm_sprint56_verify_" + uuid4().hex[:12]
    if not scratch_name.startswith("bm_sprint56_verify_") or scratch_name == address.database:
        raise SystemExit("Scratch destination validation failed.")
    administration = create_engine(address.set(database="postgres"), isolation_level="AUTOCOMMIT")
    created = False
    try:
        with administration.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{scratch_name}"'))  # noqa: S608
        created = True
        environment = os.environ.copy()
        environment["TEST_DATABASE_URL"] = address.set(database=scratch_name).render_as_string(
            hide_password=False
        )
        environment["PYTHONPATH"] = str(workspace / "src")
        environment["RUN_LOAD_TESTS"] = "1" if arguments.load else "0"
        print(f"Running against isolated scratch database: {scratch_name}", flush=True)
        # Fixed interpreter/module; no shell or untrusted command interpolation.
        return subprocess.call(  # noqa: S603
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *arguments.tests],
            cwd=workspace / "src" / "backend",
            env=environment,
        )
    finally:
        if created:
            with administration.connect() as connection:
                connection.execute(
                    text(f'DROP DATABASE IF EXISTS "{scratch_name}" WITH (FORCE)')
                )  # noqa: S608
        administration.dispose()
        print("Isolated verification database removed.", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
