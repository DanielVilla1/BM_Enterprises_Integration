"""CLI-only rolling mock data for the database behind the Cloudflare frontend."""

import argparse
import json

from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool

from backend.src.config import get_settings
from backend.src.Repository.orm_models import DeliveryOrderRow
from backend.src.Repository.recent_seed_repository import TODAY_COUNT, build_dataset, seed_recent


def validate_target(address: URL, confirmed_host: str | None) -> None:
    if address.get_backend_name() not in {"postgresql", "sqlite"}:
        raise ValueError("Only the project's PostgreSQL and SQLite databases are supported.")
    if address.get_backend_name() == "postgresql":
        if not address.host or confirmed_host != address.host:
            raise ValueError("Supply --confirm-host matching the DATABASE_URL hostname exactly.")
        if address.drivername not in {"postgresql", "postgresql+psycopg2"}:
            raise ValueError("Use the project's postgresql+psycopg2 driver.")
        if address.host not in {"db", "localhost", "127.0.0.1", "::1"}:
            if address.query.get("sslmode") not in {"require", "verify-ca", "verify-full"}:
                raise ValueError("Hosted DATABASE_URL must set sslmode=require or stricter.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Refresh 94 fictional rows across the last 30 Manila dates.")
    parser.add_argument(
        "--mock-data", action="store_true", help="Explicitly enable fictional database writes."
    )
    parser.add_argument("--confirm-host", help="Exact DATABASE_URL hostname; required for PostgreSQL.")
    parser.add_argument(
        "--renew", action="store_true", help="Remove and recreate only this seed's business rows atomically."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Generate counts without connecting to a database."
    )
    args = parser.parse_args(argv)
    if not args.dry_run and not args.mock_data:
        parser.error("Writes require --mock-data. Use --dry-run to inspect without connecting.")
    data = build_dataset()
    counts = {table.name: len(rows) for table, rows in data.items()}
    dates = [row["scheduled_date"] for row in data[DeliveryOrderRow.__table__]]
    summary = {
        "rows": counts,
        "total_rows": sum(counts.values()),
        "today_orders": TODAY_COUNT,
        "window_start": min(dates).isoformat(),
        "window_end": max(dates).isoformat(),
        "dry_run": args.dry_run,
        "renew": args.renew,
    }
    if args.dry_run:
        print(json.dumps(summary, sort_keys=True))
        return
    address = make_url(get_settings().database_url)
    try:
        validate_target(address, args.confirm_host)
    except ValueError as error:
        parser.error(str(error))
    connect_args = (
        {
            "connect_timeout": 5,
            "options": (
                "-c statement_timeout=5000 -c lock_timeout=2000 "
                "-c idle_in_transaction_session_timeout=15000"
            ),
        }
        if address.get_backend_name() == "postgresql"
        else {"timeout": 2}
    )
    engine = create_engine(
        address, poolclass=NullPool, connect_args=connect_args, echo=False, hide_parameters=True
    )
    if address.get_backend_name() == "sqlite":

        @event.listens_for(engine, "connect")
        def enable_foreign_keys(dbapi_connection: object, _record: object) -> None:
            cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    try:
        with engine.begin() as connection:
            seed_recent(connection, data, renew=args.renew)
    except (SQLAlchemyError, ValueError):
        # Driver exceptions can contain SQL, row data or credentials. Do not print them.
        raise SystemExit(
            "Mock seed failed; the transaction was rolled back. Check connectivity, migrations, "
            "permissions and whether seed rows have conflicting references or linked sign-in accounts. "
            "No partial seed was committed."
        ) from None
    finally:
        engine.dispose()
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
