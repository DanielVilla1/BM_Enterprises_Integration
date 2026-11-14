# ===== AI GENERATED: PermissionRepository =====
# Purpose: Read the permission matrix stored in role_permissions
# Inputs: Session
# Returns: PermissionGrant entities
# Flow:
# 1. Query grants by capability / roles
# 2. Map rows to entities

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..Entity.access import AccessLevel, RoleCode
from ..Entity.employee import PermissionGrant
from .orm_models import RolePermissionRow


class PermissionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_entity(row: RolePermissionRow) -> PermissionGrant:
        return PermissionGrant(
            capability=row.capability,
            role_code=RoleCode(row.role_code),
            access_level=AccessLevel(row.access_level),
            conditional_setting=row.conditional_setting,
        )

    def find_grants(self, capability: str, role_codes: tuple[RoleCode, ...]) -> list[PermissionGrant]:
        if not role_codes:
            return []
        statement = select(RolePermissionRow).where(
            RolePermissionRow.capability == capability,
            RolePermissionRow.role_code.in_([role.value for role in role_codes]),
        )
        return [self._to_entity(row) for row in self._session.scalars(statement).all()]

    def list_all(self) -> list[PermissionGrant]:
        statement = select(RolePermissionRow).order_by(
            RolePermissionRow.capability, RolePermissionRow.role_code
        )
        return [self._to_entity(row) for row in self._session.scalars(statement).all()]

    def list_for_roles(self, role_codes: tuple[RoleCode, ...]) -> list[PermissionGrant]:
        if not role_codes:
            return []
        statement = select(RolePermissionRow).where(
            RolePermissionRow.role_code.in_([role.value for role in role_codes])
        )
        return [self._to_entity(row) for row in self._session.scalars(statement).all()]
