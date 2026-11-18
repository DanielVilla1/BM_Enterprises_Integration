# ===== AI GENERATED: reconcile_clerk =====
# Purpose: Entry point for the periodic Clerk <-> employee reconciliation
# Inputs: CLERK_SECRET_KEY (and optional CLERK_API_BASE_URL) from the environment
# Returns: exit code 0 on success, 1 when aborted or unavailable
# Flow:
# 1. Build the service around one session
# 2. Run it, print counts only (no personal data)
# Schedule it hourly with the host scheduler or cron.

from backend.src.config import get_settings
from backend.src.database import SessionLocal
from backend.src.Entity.business_rule_error import BusinessRuleError
from backend.src.Infrastructure.Clerk.clerk_identity_directory import ClerkIdentityDirectory
from backend.src.Repository.audit_repository import AuditRepository
from backend.src.Repository.employee_repository import EmployeeRepository
from backend.src.Repository.unit_of_work import SqlAlchemyUnitOfWork
from backend.src.Service.reconciliation_service import ReconciliationService


def main() -> int:
    settings = get_settings()
    directory = ClerkIdentityDirectory(settings.clerk_secret_key, settings.clerk_api_base_url)
    with SessionLocal() as session:
        service = ReconciliationService(
            directory,
            EmployeeRepository(session),
            AuditRepository(session),
            SqlAlchemyUnitOfWork(session),
        )
        try:
            report = service.run()
        except BusinessRuleError as rule_error:
            print(f"Aborted: {rule_error.error_code} - {rule_error.detail}")
            return 1
    print(
        f"Reconciled: deactivated={report.deactivated_count} linked={report.linked_count} "
        f"clerk_users_without_employee={report.clerk_users_without_employee}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
