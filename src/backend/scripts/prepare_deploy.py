"""Apply backend migrations, then optionally refresh the main-branch demo dataset.

Run once during a Render build, after installing requirements. Never run per request
or from API startup: sleeping services and additional workers must not reset data.
"""

import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.engine import make_url

from backend.scripts import seed_recent
from backend.src.config import get_settings


def main() -> None:
    refresh = os.environ.get("MOCK_DATA_AUTO_REFRESH", "false").lower()
    if refresh not in {"true", "false"}:
        raise SystemExit("MOCK_DATA_AUTO_REFRESH must be true or false.")
    seed_args = None
    if refresh == "true":
        if os.environ.get("RENDER_GIT_BRANCH") != "main":
            raise SystemExit("Automatic mock refresh is restricted to Render deployments of main.")
        try:
            address = make_url(get_settings().database_url)
            if address.get_backend_name() != "postgresql":
                raise ValueError("Automatic mock refresh requires the hosted PostgreSQL database.")
            seed_recent.validate_target(address, address.host)
        except Exception:
            # Configuration/URL errors can include credentials; keep build logs safe.
            raise SystemExit(
                "Automatic mock refresh needs a valid PostgreSQL DATABASE_URL with TLS."
            ) from None
        seed_args = ["--mock-data", "--confirm-host", address.host]

    configuration = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    try:
        command.upgrade(configuration, "head")
    except Exception:
        raise SystemExit(
            "Database migration failed; deployment preparation stopped before mock refresh."
        ) from None
    if seed_args is not None:
        seed_recent.main(seed_args)
    else:
        print("Database migrations complete; automatic mock refresh is disabled.")


if __name__ == "__main__":
    main()
