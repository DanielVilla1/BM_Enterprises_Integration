# ===== AI GENERATED: EmployeeService =====
# Purpose: Employee records, activation, Clerk link and role assignment rules
# Inputs: repositories, unit of work, acting principal and access level
# Returns: Employee entities or BusinessRuleError
# Flow:
# 1. Enforce access level and object-level ownership
# 2. Apply rules (forbidden role pairs, no self lock-out, uniqueness)
# 3. Write an audit record in the same transaction, then commit

from uuid import UUID

from ..Contract.i_audit_repository import IAuditRepository
from ..Contract.i_employee_repository import IEmployeeRepository
from ..Contract.i_unit_of_work import IUnitOfWork
from ..Entity.access import AccessLevel, RoleCode
from ..Entity.business_rule_error import BusinessRuleError
from ..Entity.employee import Employee, Principal
from ..Entity.role_rules import find_forbidden_pairs


def _not_found() -> BusinessRuleError:
    return BusinessRuleError(404, "EMPLOYEE_NOT_FOUND", "Not found", "The employee was not found.")


def _require_full(level: AccessLevel) -> None:
    if level is not AccessLevel.FULL:
        raise BusinessRuleError(
            403, "PERMISSION_DENIED", "Forbidden", "Your role does not allow this action."
        )


class EmployeeService:
    def __init__(
        self,
        employees: IEmployeeRepository,
        audit: IAuditRepository,
        unit_of_work: IUnitOfWork,
    ) -> None:
        self._employees = employees
        self._audit = audit
        self._unit_of_work = unit_of_work

    def list_employees(
        self,
        principal: Principal,
        level: AccessLevel,
        limit: int,
        offset: int,
        only_active: bool | None,
    ) -> list[Employee]:
        if level is AccessLevel.OWN:
            own_record = self._employees.get_by_id(principal.employee_id)
            return [own_record] if own_record is not None and offset == 0 else []
        return self._employees.list_page(limit, offset, only_active)

    def get_employee(self, principal: Principal, level: AccessLevel, employee_id: UUID) -> Employee:
        if level is AccessLevel.OWN and employee_id != principal.employee_id:
            raise _not_found()
        employee = self._employees.get_by_id(employee_id)
        if employee is None:
            raise _not_found()
        return employee

    def create_employee(
        self,
        principal: Principal,
        level: AccessLevel,
        full_name: str,
        email: str,
        phone: str | None,
        trace_id: str | None,
    ) -> Employee:
        _require_full(level)
        self._ensure_email_free(email, owner_id=None)
        employee = self._employees.create(full_name, email, phone)
        self._record(principal, "employee.created", employee.employee_id, {}, trace_id)
        self._unit_of_work.commit()
        return employee

    def update_employee(
        self,
        principal: Principal,
        level: AccessLevel,
        employee_id: UUID,
        full_name: str | None,
        email: str | None,
        phone: str | None,
        trace_id: str | None,
    ) -> Employee:
        _require_full(level)
        if self._employees.get_by_id(employee_id) is None:
            raise _not_found()
        if email is not None:
            self._ensure_email_free(email, owner_id=employee_id)
        updated = self._employees.update_profile(employee_id, full_name, email, phone)
        if updated is None:
            raise _not_found()
        changed_fields = [
            field_name
            for field_name, value in (("full_name", full_name), ("email", email), ("phone", phone))
            if value is not None
        ]
        self._record(principal, "employee.updated", employee_id, {"fields": changed_fields}, trace_id)
        self._unit_of_work.commit()
        return updated

    def activate_employee(self, principal: Principal, employee_id: UUID, trace_id: str | None) -> Employee:
        existing = self._employees.get_by_id(employee_id)
        if existing is None:
            raise _not_found()
        if existing.is_active:
            return existing
        activated = self._employees.set_active(employee_id, True)
        if activated is None:
            raise _not_found()
        self._record(principal, "employee.activated", employee_id, {}, trace_id)
        self._unit_of_work.commit()
        return activated

    def deactivate_employee(self, principal: Principal, employee_id: UUID, trace_id: str | None) -> Employee:
        if employee_id == principal.employee_id:
            raise BusinessRuleError(
                409,
                "CANNOT_DEACTIVATE_SELF",
                "Conflict",
                "You cannot deactivate your own account.",
            )
        existing = self._employees.get_by_id(employee_id)
        if existing is None:
            raise _not_found()
        if not existing.is_active:
            return existing
        deactivated = self._employees.set_active(employee_id, False)
        if deactivated is None:
            raise _not_found()
        self._record(principal, "employee.deactivated", employee_id, {}, trace_id)
        self._unit_of_work.commit()
        return deactivated

    def link_identity(
        self, principal: Principal, employee_id: UUID, clerk_user_id: str, trace_id: str | None
    ) -> Employee:
        if self._employees.get_by_id(employee_id) is None:
            raise _not_found()
        holder = self._employees.get_by_clerk_user_id(clerk_user_id)
        if holder is not None and holder.employee_id != employee_id:
            raise BusinessRuleError(
                409,
                "IDENTITY_ALREADY_LINKED",
                "Conflict",
                "That sign-in account is already linked to another employee.",
            )
        linked = self._employees.set_clerk_user_id(employee_id, clerk_user_id)
        if linked is None:
            raise _not_found()
        self._record(principal, "employee.identity_linked", employee_id, {}, trace_id)
        self._unit_of_work.commit()
        return linked

    def assign_roles(
        self,
        principal: Principal,
        employee_id: UUID,
        role_codes: set[RoleCode],
        exception_reason: str | None,
        trace_id: str | None,
    ) -> Employee:
        existing = self._employees.get_by_id(employee_id)
        if existing is None:
            raise _not_found()
        if employee_id == principal.employee_id and RoleCode.OWNER not in role_codes:
            raise BusinessRuleError(
                409,
                "CANNOT_REMOVE_OWN_OWNER_ROLE",
                "Conflict",
                "You cannot remove your own Owner role.",
            )
        forbidden_pairs = find_forbidden_pairs(role_codes)
        if forbidden_pairs and not exception_reason:
            pair_text = ", ".join(f"{first}+{second}" for first, second in forbidden_pairs)
            raise BusinessRuleError(
                409,
                "ROLE_PAIR_FORBIDDEN",
                "Conflict",
                f"Forbidden role combination: {pair_text}. An Owner exception reason is required.",
            )
        updated = self._employees.replace_roles(
            employee_id,
            role_codes,
            principal.employee_id,
            exception_reason if forbidden_pairs else None,
        )
        if updated is None:
            raise _not_found()
        details: dict[str, object] = {
            "before": [role.value for role in existing.role_codes],
            "after": [role.value for role in updated.role_codes],
        }
        if forbidden_pairs:
            details["exception_reason"] = exception_reason
            details["forbidden_pairs"] = [f"{first}+{second}" for first, second in forbidden_pairs]
        self._record(principal, "employee.roles_changed", employee_id, details, trace_id)
        self._unit_of_work.commit()
        return updated

    def bootstrap_owner(self, full_name: str, email: str, clerk_user_id: str) -> Employee:
        if self._employees.list_page(1, 0, None):
            raise BusinessRuleError(
                409,
                "BOOTSTRAP_NOT_ALLOWED",
                "Conflict",
                "Employees already exist; bootstrap is only for an empty system.",
            )
        employee = self._employees.create(full_name, email, None)
        self._employees.set_clerk_user_id(employee.employee_id, clerk_user_id)
        self._employees.replace_roles(employee.employee_id, {RoleCode.OWNER}, None, None)
        activated = self._employees.set_active(employee.employee_id, True)
        if activated is None:
            raise _not_found()
        self._audit.append(None, "employee.bootstrap_owner", "employee", str(employee.employee_id), {}, None)
        self._unit_of_work.commit()
        return activated

    def _ensure_email_free(self, email: str, owner_id: UUID | None) -> None:
        holder = self._employees.get_by_email(email)
        if holder is not None and holder.employee_id != owner_id:
            raise BusinessRuleError(
                409,
                "EMAIL_ALREADY_EXISTS",
                "Conflict",
                "An employee with that email already exists.",
            )

    def _record(
        self,
        principal: Principal,
        action: str,
        employee_id: UUID,
        details: dict[str, object],
        trace_id: str | None,
    ) -> None:
        self._audit.append(principal.employee_id, action, "employee", str(employee_id), details, trace_id)
