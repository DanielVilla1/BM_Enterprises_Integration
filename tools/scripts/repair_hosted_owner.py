"""Repair the existing hosted-demo Owner using its verified Clerk email.

Requires private database credentials and Clerk Development API access locally.
It cannot provision users or assign Owner permissions, and exposes no web endpoint.
"""

import getpass
import os
import sys
from pathlib import Path

from bootstrap_hosted_owner import normalize_database_url
from sqlalchemy.exc import SQLAlchemyError


def main() -> int:
    if not sys.stdin.isatty():
        print("Run this command in an interactive PowerShell terminal.")
        return 2
    print("Repair an EXISTING hosted Owner's sign-in link using its verified Clerk email.")
    print("The Owner role must already exist. No users or roles are created.")
    try:
        database_url = normalize_database_url(
            getpass.getpass("Paste the working DATABASE_URL from Render (hidden): ")
        )
        email = input("Email of the existing hosted Owner: ").strip()
        if "@" not in email:
            raise ValueError("Enter the Owner's sign-in email.")
        # Use process-local credentials; root .env and hosted settings are never written.
        os.environ["DATABASE_URL"] = database_url
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
        secret = getpass.getpass("Paste Render's CLERK_SECRET_KEY (hidden): ")
        if not secret.startswith("sk_test_"):
            raise ValueError("Use the Clerk Development secret key for the hosted demo's login instance.")
        return recover_owner(email, secret)
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return 2
    except ValueError as error:
        print(error)
        return 2
    except SQLAlchemyError:
        print("Database operation failed. Check the exact hosted URL; connection details were omitted.")
        return 1


def recover_owner(email: str, secret: str) -> int:
    from backend.src.Contract.i_identity_directory import IdentityDirectoryError
    from backend.src.database import SessionLocal
    from backend.src.Entity.business_rule_error import BusinessRuleError
    from backend.src.Infrastructure.Clerk.clerk_identity_directory import ClerkIdentityDirectory
    from backend.src.Repository.audit_repository import AuditRepository
    from backend.src.Repository.employee_repository import EmployeeRepository
    from backend.src.Repository.unit_of_work import SqlAlchemyUnitOfWork
    from backend.src.Service.owner_recovery_service import OwnerRecoveryService

    try:
        identities = ClerkIdentityDirectory(secret, "https://api.clerk.com").list_users()
        matches = [
            identity
            for identity in identities
            if identity.verified_email and identity.verified_email.casefold() == email.casefold()
        ]
        if len(matches) != 1:
            print("No unique verified Clerk user matches. Check the email and Clerk Development instance.")
            return 1
        with SessionLocal() as session:
            owner = OwnerRecoveryService(
                EmployeeRepository(session), AuditRepository(session), SqlAlchemyUnitOfWork(session)
            ).recover(email, matches[0])
        print(f"Owner link checked/repaired: {owner.employee_id}. Sign in with that Owner email and refresh.")
        print(f"Verified sign-in account ID: {matches[0].user_id}")
        print("Other roles must be provisioned and activated through People in this hosted database.")
        return 0
    except IdentityDirectoryError:
        print("Clerk directory could not be verified. Check the Development secret key. No link was changed.")
        return 1
    except BusinessRuleError as error:
        print(f"Refused: {error.detail}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
