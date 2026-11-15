# ===== AI GENERATED: IEmployeeRepository =====
# Purpose: Port for employee and role-assignment persistence
# Inputs: domain values
# Returns: Employee entities
# Flow:
# 1. Read operations by id, clerk id, email, page
# 2. Write operations for create, update, active flag, roles

from typing import Protocol
from uuid import UUID

from ..Entity.access import RoleCode
from ..Entity.employee import Employee


class IEmployeeRepository(Protocol):
    def get_by_id(self, employee_id: UUID) -> Employee | None: ...

    def get_by_clerk_user_id(self, clerk_user_id: str) -> Employee | None: ...

    def get_by_email(self, email: str) -> Employee | None: ...

    def list_page(self, limit: int, offset: int, only_active: bool | None) -> list[Employee]: ...

    def list_all(self) -> list[Employee]: ...

    def create(self, full_name: str, email: str, phone: str | None) -> Employee: ...

    def update_profile(
        self, employee_id: UUID, full_name: str | None, email: str | None, phone: str | None
    ) -> Employee | None: ...

    def set_active(self, employee_id: UUID, is_active: bool) -> Employee | None: ...

    def set_clerk_user_id(self, employee_id: UUID, clerk_user_id: str | None) -> Employee | None: ...

    def replace_roles(
        self,
        employee_id: UUID,
        role_codes: set[RoleCode],
        assigned_by: UUID | None,
        exception_reason: str | None,
    ) -> Employee | None: ...
