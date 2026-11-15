# ===== AI GENERATED: IPermissionRepository =====
# Purpose: Port for reading the permission matrix stored as data
# Inputs: capability and role codes
# Returns: PermissionGrant entities
# Flow:
# 1. Fetch the grants relevant to one capability and role set
# 2. Fetch the whole matrix for administration and tests

from typing import Protocol

from ..Entity.access import RoleCode
from ..Entity.employee import PermissionGrant


class IPermissionRepository(Protocol):
    def find_grants(self, capability: str, role_codes: tuple[RoleCode, ...]) -> list[PermissionGrant]: ...

    def list_all(self) -> list[PermissionGrant]: ...

    def list_for_roles(self, role_codes: tuple[RoleCode, ...]) -> list[PermissionGrant]: ...
