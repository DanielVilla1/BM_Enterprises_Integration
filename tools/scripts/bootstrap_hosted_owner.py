"""Create the first hosted-demo Owner without saving database credentials.

Run with the backend virtual environment from a normal interactive terminal.
The existing bootstrap service refuses databases that already contain employees.
"""

import getpass
import os
import re
import sys
from pathlib import Path

from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError, SQLAlchemyError


def normalize_database_url(raw_value: str) -> str:
    """Accept an explicit hosted Supabase PostgreSQL destination and require TLS."""
    try:
        address = make_url(raw_value.strip())
    except (ArgumentError, ValueError):
        raise ValueError("Paste the complete DATABASE_URL from Render's Environment page.") from None
    host = address.host or ""
    if address.get_backend_name() != "postgresql" or not re.fullmatch(
        r"(?:[a-z0-9-]+\.)+pooler\.supabase\.com|db\.[a-z0-9]+\.supabase\.co", host
    ):
        raise ValueError("Use the hosted Supabase connection URL, with its password correctly URL-encoded.")
    if not address.username or not address.password or address.database != "postgres":
        raise ValueError("The URL must include the database username, password and /postgres database.")
    if address.query.get("sslmode", "require") not in {"require", "verify-ca", "verify-full"}:
        raise ValueError(
            "The hosted database connection must use sslmode=require or certificate verification."
        )
    return (
        address.set(drivername="postgresql+psycopg2")
        .update_query_dict({"sslmode": address.query.get("sslmode", "require"), "connect_timeout": "15"})
        .render_as_string(hide_password=False)
    )


def main() -> int:
    """Prompt locally, then delegate creation and auditing to the existing application."""
    if not sys.stdin.isatty():
        print("Run this command directly in PowerShell so credentials can be entered privately.")
        return 2
    print("Hosted demo: create the FIRST Owner in your Supabase database.")
    print("Existing employees cause a refusal. Local records and .env files are not changed.")
    try:
        database_url = normalize_database_url(
            getpass.getpass("Paste Render's DATABASE_URL (hidden), then press Enter: ")
        )
        full_name = input("Owner's full name: ").strip()
        email = input("Owner's sign-in email: ").strip()
        clerk_user_id = input("Clerk DEVELOPMENT user ID (user_...): ").strip()
        if not full_name or "@" not in email or not re.fullmatch(r"user_[A-Za-z0-9]+", clerk_user_id):
            raise ValueError("Enter your name, sign-in email and the user_ ID from Clerk's Users page.")
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled; no account was created.")
        return 2
    except ValueError as error:
        print(error)
        return 2

    # Only this process receives the URL; never print it or write it to a file.
    os.environ["DATABASE_URL"] = database_url
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
    sys.argv = ["bootstrap_owner", "--name", full_name, "--email", email, "--clerk-user-id", clerk_user_id]
    try:
        from backend.scripts.bootstrap_owner import main as bootstrap_owner

        result = bootstrap_owner()
    except SQLAlchemyError:
        print("Database setup failed. Check the hosted URL, password encoding and completed migrations.")
        print("Connection details were omitted to keep credentials private.")
        return 1
    if result == 0:
        print("Hosted Owner created. Refresh your Cloudflare website and try again.")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
