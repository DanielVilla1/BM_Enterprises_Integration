# ===== AI GENERATED: ReconciliationService =====
# Purpose: Periodically align Clerk users with local employees (spec 3.2)
# Inputs: identity directory, employee repository, audit, unit of work
# Returns: ReconciliationReport; aborts without changes on unsafe input
# Flow:
# 1. Read all Clerk users; any failure aborts before touching data
# 2. Deactivate active employees whose Clerk user no longer exists
# 3. Link unlinked employees by verified email; audit each change

from ..Contract.i_audit_repository import IAuditRepository
from ..Contract.i_employee_repository import IEmployeeRepository
from ..Contract.i_identity_directory import IdentityDirectoryError, IIdentityDirectory
from ..Contract.i_unit_of_work import IUnitOfWork
from ..Entity.business_rule_error import BusinessRuleError
from ..Entity.reconciliation import ReconciliationReport

MASS_DEACTIVATION_MINIMUM = 3


class ReconciliationService:
    def __init__(
        self,
        directory: IIdentityDirectory,
        employees: IEmployeeRepository,
        audit: IAuditRepository,
        unit_of_work: IUnitOfWork,
    ) -> None:
        self._directory = directory
        self._employees = employees
        self._audit = audit
        self._unit_of_work = unit_of_work

    def run(self) -> ReconciliationReport:
        try:
            users = self._directory.list_users()
        except IdentityDirectoryError as directory_error:
            raise BusinessRuleError(
                503,
                "RECONCILIATION_DIRECTORY_UNAVAILABLE",
                "Service unavailable",
                "The identity provider could not be read; no changes were made.",
            ) from directory_error
        employees = self._employees.list_all()
        known_ids = {user.user_id for user in users}
        linked_active = [one for one in employees if one.is_active and one.clerk_user_id]
        missing = [one for one in linked_active if one.clerk_user_id not in known_ids]
        self._abort_if_unsafe(users_count=len(users), linked_count=len(linked_active), missing=len(missing))

        for employee in missing:
            self._employees.set_active(employee.employee_id, False)
            self._audit.append(
                None,
                "employee.deactivated",
                "employee",
                str(employee.employee_id),
                {"source": "reconciliation", "reason": "clerk_user_missing"},
                None,
            )

        taken_ids = {one.clerk_user_id for one in employees if one.clerk_user_id}
        email_to_user = {
            user.verified_email.lower(): user.user_id for user in users if user.verified_email is not None
        }
        linked_count = 0
        for employee in employees:
            if employee.clerk_user_id is not None:
                continue
            candidate = email_to_user.get(employee.email.lower())
            if candidate is None or candidate in taken_ids:
                continue
            self._employees.set_clerk_user_id(employee.employee_id, candidate)
            taken_ids.add(candidate)
            linked_count += 1
            self._audit.append(
                None,
                "employee.identity_linked",
                "employee",
                str(employee.employee_id),
                {"source": "reconciliation"},
                None,
            )

        orphan_count = len(known_ids - taken_ids)
        self._unit_of_work.commit()
        return ReconciliationReport(
            deactivated_count=len(missing),
            linked_count=linked_count,
            clerk_users_without_employee=orphan_count,
        )

    @staticmethod
    def _abort_if_unsafe(users_count: int, linked_count: int, missing: int) -> None:
        empty_directory = users_count == 0 and linked_count > 0
        mass_deactivation = missing >= MASS_DEACTIVATION_MINIMUM and missing * 2 > linked_count
        if empty_directory or mass_deactivation:
            raise BusinessRuleError(
                409,
                "RECONCILIATION_ABORTED",
                "Conflict",
                "Reconciliation would deactivate an unusually large share of employees; "
                "check the identity provider and run it manually.",
            )
