# ===== AI GENERATED: seed_presentation =====
# Purpose: Load explicitly fictional records into local development for presentations.
# Inputs: --presentation and the configured local development database.
# Returns: Insert counts; reruns are idempotent; production and remote databases are refused.
# Flow: Validate destination before opening a transaction, then delegate to the seed repository.

import argparse
import json

from sqlalchemy.engine import make_url

from backend.src.config import get_settings
from backend.src.database import SessionLocal
from backend.src.Repository.presentation_seed_repository import PresentationSeedRepository


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed fictional presentation records in local development only."
    )
    parser.add_argument("--presentation", action="store_true", required=True)
    parser.parse_args()
    settings = get_settings()
    address = make_url(settings.database_url)
    if settings.environment.lower() not in {"development", "test", "presentation"}:
        raise SystemExit("Presentation seeding is disabled outside development/test/presentation.")
    if address.get_backend_name() != "sqlite" and address.host not in {"db", "localhost", "127.0.0.1", "::1"}:
        raise SystemExit("Presentation seeding requires a local database; remote hosts are refused.")
    with SessionLocal() as session:
        print(json.dumps(PresentationSeedRepository(session).seed(), sort_keys=True))


if __name__ == "__main__":
    main()
