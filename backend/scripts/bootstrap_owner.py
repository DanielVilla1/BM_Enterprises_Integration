# ===== AI GENERATED: bootstrap_owner =====
# Purpose: Create the first Owner on an empty system (one-time, run by an operator)
# Inputs: --name, --email, --clerk-user-id
# Returns: prints the new employee id; refuses when employees already exist
# Flow:
# 1. Build the service around one session
# 2. Create active Owner linked to the Clerk user, audit logged

import argparse

from backend.src.database import SessionLocal
from backend.src.Entity.business_rule_error import BusinessRuleError
from backend.src.Repository.audit_repository import AuditRepository
from backend.src.Repository.employee_repository import EmployeeRepository
from backend.src.Repository.unit_of_work import SqlAlchemyUnitOfWork
from backend.src.Service.employee_service import EmployeeService


def main() -> int:
    parser = argparse.ArgumentParser(description="Create the first Owner/Manager account.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--clerk-user-id", required=True)
    arguments = parser.parse_args()
    with SessionLocal() as session:
        service = EmployeeService(
            EmployeeRepository(session), AuditRepository(session), SqlAlchemyUnitOfWork(session)
        )
        try:
            owner = service.bootstrap_owner(arguments.name, arguments.email, arguments.clerk_user_id)
        except BusinessRuleError as rule_error:
            print(f"Refused: {rule_error.detail}")
            return 1
    print(f"Owner created: {owner.employee_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
