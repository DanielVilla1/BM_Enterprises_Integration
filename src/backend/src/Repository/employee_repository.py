# ===== AI GENERATED: EmployeeRepository =====
# Purpose: SQLAlchemy implementation of IEmployeeRepository
# Inputs: Session
# Returns: Employee entities (never ORM rows)
# Flow:
# 1. Query rows plus role codes
# 2. Map rows to Employee entities
# 3. Flush writes; the service commits

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from ..Entity.access import RoleCode
from ..Entity.employee import Employee, EmployeeDirectoryEntry
from .orm_models import EmployeeRoleRow, EmployeeRow


class EmployeeRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _role_codes_for(self, employee_id: UUID) -> tuple[RoleCode, ...]:
        statement = select(EmployeeRoleRow.role_code).where(EmployeeRoleRow.employee_id == employee_id)
        codes = self._session.scalars(statement).all()
        return tuple(sorted((RoleCode(code) for code in codes), key=lambda role: role.value))

    def _to_entity(self, row: EmployeeRow) -> Employee:
        return Employee(
            employee_id=row.employee_id,
            full_name=row.full_name,
            email=row.email,
            phone=row.phone,
            clerk_user_id=row.clerk_user_id,
            is_active=row.is_active,
            role_codes=self._role_codes_for(row.employee_id),
            created_at=row.created_at,
        )

    def _entity_or_none(self, row: EmployeeRow | None) -> Employee | None:
        return self._to_entity(row) if row is not None else None

    def get_by_id(self, employee_id: UUID) -> Employee | None:
        return self._entity_or_none(self._session.get(EmployeeRow, employee_id))

    def get_by_clerk_user_id(self, clerk_user_id: str) -> Employee | None:
        statement = select(EmployeeRow).where(EmployeeRow.clerk_user_id == clerk_user_id)
        return self._entity_or_none(self._session.scalars(statement).first())

    def get_by_email(self, email: str) -> Employee | None:
        statement = select(EmployeeRow).where(func.lower(EmployeeRow.email) == email.lower())
        return self._entity_or_none(self._session.scalars(statement).first())

    def list_page(self, limit: int, offset: int, only_active: bool | None) -> list[Employee]:
        statement = select(EmployeeRow).order_by(EmployeeRow.full_name, EmployeeRow.employee_id)
        if only_active is not None:
            statement = statement.where(EmployeeRow.is_active == only_active)
        rows = self._session.scalars(statement.limit(limit).offset(offset)).all()
        return [self._to_entity(row) for row in rows]

    # AI MODIFIED: Financial name lists do not load identities, contacts or per-person role queries.
    def list_directory(self) -> list[EmployeeDirectoryEntry]:
        statement = select(EmployeeRow.employee_id, EmployeeRow.full_name).order_by(
            EmployeeRow.full_name, EmployeeRow.employee_id
        )
        return [
            EmployeeDirectoryEntry(identifier, name) for identifier, name in self._session.execute(statement)
        ]

    def list_all(self) -> list[Employee]:
        statement = select(EmployeeRow).order_by(EmployeeRow.full_name, EmployeeRow.employee_id)
        return [self._to_entity(row) for row in self._session.scalars(statement).all()]

    def list_by_role(self, role_code: RoleCode, only_active: bool) -> list[Employee]:
        statement = (
            select(EmployeeRow)
            .join(EmployeeRoleRow, EmployeeRoleRow.employee_id == EmployeeRow.employee_id)
            .where(EmployeeRoleRow.role_code == role_code.value)
            .order_by(EmployeeRow.full_name, EmployeeRow.employee_id)
        )
        if only_active:
            statement = statement.where(EmployeeRow.is_active.is_(True))
        return [self._to_entity(row) for row in self._session.scalars(statement).all()]

    def create(self, full_name: str, email: str, phone: str | None) -> Employee:
        row = EmployeeRow(full_name=full_name, email=email, phone=phone, is_active=False)
        self._session.add(row)
        self._session.flush()
        self._session.refresh(row)
        return self._to_entity(row)

    def update_profile(
        self, employee_id: UUID, full_name: str | None, email: str | None, phone: str | None
    ) -> Employee | None:
        row = self._session.get(EmployeeRow, employee_id)
        if row is None:
            return None
        if full_name is not None:
            row.full_name = full_name
        if email is not None:
            row.email = email
        if phone is not None:
            row.phone = phone
        self._session.flush()
        return self._to_entity(row)

    def set_active(self, employee_id: UUID, is_active: bool) -> Employee | None:
        row = self._session.get(EmployeeRow, employee_id)
        if row is None:
            return None
        row.is_active = is_active
        self._session.flush()
        return self._to_entity(row)

    def set_clerk_user_id(self, employee_id: UUID, clerk_user_id: str | None) -> Employee | None:
        row = self._session.get(EmployeeRow, employee_id)
        if row is None:
            return None
        row.clerk_user_id = clerk_user_id
        self._session.flush()
        return self._to_entity(row)

    def replace_roles(
        self,
        employee_id: UUID,
        role_codes: set[RoleCode],
        assigned_by: UUID | None,
        exception_reason: str | None,
    ) -> Employee | None:
        row = self._session.get(EmployeeRow, employee_id)
        if row is None:
            return None
        self._session.execute(delete(EmployeeRoleRow).where(EmployeeRoleRow.employee_id == employee_id))
        for role_code in sorted(role_codes, key=lambda role: role.value):
            self._session.add(
                EmployeeRoleRow(
                    employee_id=employee_id,
                    role_code=role_code.value,
                    assigned_by=assigned_by,
                    exception_reason=exception_reason,
                )
            )
        self._session.flush()
        return self._to_entity(row)
