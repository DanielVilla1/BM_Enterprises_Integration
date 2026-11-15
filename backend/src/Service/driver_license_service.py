# ===== AI GENERATED: DriverLicenseService =====
# Purpose: Driver license details with level-aware visibility
# Inputs: employee + license repositories, audit, unit of work, date provider
# Returns: LicenseSummary or BusinessRuleError
# Flow:
# 1. OWN level sees only the caller's license (404 otherwise)
# 2. Only FULL may save; only employees with the DRIVER role have licenses
# 3. Audit never contains the license number

from collections.abc import Callable
from datetime import date, timedelta
from uuid import UUID

from ..Contract.i_audit_repository import IAuditRepository
from ..Contract.i_employee_repository import IEmployeeRepository
from ..Contract.i_fleet_repositories import IDriverLicenseRepository
from ..Contract.i_unit_of_work import IUnitOfWork
from ..Entity.access import AccessLevel, RoleCode
from ..Entity.business_rule_error import BusinessRuleError
from ..Entity.clock import manila_today
from ..Entity.employee import Principal
from ..Entity.fleet import LicenseSummary, license_validity

MAXIMUM_YEARS_AHEAD = 20


def _not_found(code: str = "LICENSE_NOT_FOUND") -> BusinessRuleError:
    return BusinessRuleError(404, code, "Not found", "The driver license was not found.")


class DriverLicenseService:
    def __init__(
        self,
        employees: IEmployeeRepository,
        licenses: IDriverLicenseRepository,
        audit: IAuditRepository,
        unit_of_work: IUnitOfWork,
        today_provider: Callable[[], date] = manila_today,
    ) -> None:
        self._employees = employees
        self._licenses = licenses
        self._audit = audit
        self._unit_of_work = unit_of_work
        self._today_provider = today_provider

    def get_license(self, principal: Principal, level: AccessLevel, employee_id: UUID) -> LicenseSummary:
        if level is AccessLevel.OWN and employee_id != principal.employee_id:
            raise _not_found()
        stored = self._licenses.get_by_employee(employee_id)
        if stored is None:
            raise _not_found()
        return LicenseSummary(stored, license_validity(stored.expiry_date, self._today_provider()))

    def save_license(
        self,
        principal: Principal,
        level: AccessLevel,
        employee_id: UUID,
        license_number: str,
        expiry_date: date,
        trace_id: str | None,
    ) -> LicenseSummary:
        if level is not AccessLevel.FULL:
            raise BusinessRuleError(
                403, "PERMISSION_DENIED", "Forbidden", "Your role does not allow this action."
            )
        employee = self._employees.get_by_id(employee_id)
        if employee is None:
            raise _not_found("EMPLOYEE_NOT_FOUND")
        if RoleCode.DRIVER not in employee.role_codes:
            raise BusinessRuleError(
                409, "NOT_A_DRIVER", "Conflict", "Only employees with the Driver role have a license."
            )
        today = self._today_provider()
        if expiry_date > today + timedelta(days=365 * MAXIMUM_YEARS_AHEAD):
            raise BusinessRuleError(
                422, "INVALID_EXPIRY_DATE", "Validation failed", "The expiry date is too far in the future."
            )
        number = license_number.upper()
        holder = self._licenses.get_by_number(number)
        if holder is not None and holder.employee_id != employee_id:
            raise BusinessRuleError(
                409, "LICENSE_NUMBER_EXISTS", "Conflict", "That license number is already recorded."
            )
        saved = self._licenses.upsert(employee_id, number, expiry_date)
        validity = license_validity(saved.expiry_date, today)
        self._audit.append(
            principal.employee_id,
            "driver_license.saved",
            "employee",
            str(employee_id),
            {"validity": validity.value},
            trace_id,
        )
        self._unit_of_work.commit()
        return LicenseSummary(saved, validity)
