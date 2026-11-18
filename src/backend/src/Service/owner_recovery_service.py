"""Privileged operator-only recovery; never registered as an HTTP endpoint."""

from ..Contract.i_audit_repository import IAuditRepository
from ..Contract.i_employee_repository import IEmployeeRepository
from ..Contract.i_identity_directory import DirectoryUser
from ..Contract.i_unit_of_work import IUnitOfWork
from ..Entity.access import RoleCode
from ..Entity.business_rule_error import BusinessRuleError
from ..Entity.employee import Employee, Principal
from .employee_service import EmployeeService


class OwnerRecoveryService:
    """Repair an existing Owner using an identity verified by the Clerk directory.

    The caller must be a local database operator, not an authenticated web user.
    No employee or role is created; normal identity uniqueness and audit rules apply.
    """

    def __init__(
        self, employees: IEmployeeRepository, audit: IAuditRepository, unit_of_work: IUnitOfWork
    ) -> None:
        self._employees = employees
        self._service = EmployeeService(employees, audit, unit_of_work)

    def recover(self, email: str, verified_identity: DirectoryUser) -> Employee:
        if (
            not verified_identity.verified_email
            or verified_identity.verified_email.casefold() != email.casefold()
            or not verified_identity.user_id.startswith("user_")
        ):
            raise BusinessRuleError(
                409,
                "OWNER_RECOVERY_REFUSED",
                "Recovery refused",
                "A matching verified Clerk email is required.",
            )
        owner = self._employees.get_by_email(email)
        if owner is None or RoleCode.OWNER not in owner.role_codes:
            raise BusinessRuleError(
                409,
                "OWNER_RECOVERY_REFUSED",
                "Recovery refused",
                "This database has no existing Owner with that email. Check the hosted database and email.",
            )
        operator = Principal(
            owner.employee_id,
            owner.clerk_user_id or verified_identity.user_id,
            owner.full_name,
            owner.role_codes,
        )
        if owner.clerk_user_id != verified_identity.user_id:
            owner = self._service.link_identity(operator, owner.employee_id, verified_identity.user_id, None)
        if not owner.is_active:
            owner = self._service.activate_employee(operator, owner.employee_id, None)
        return owner
