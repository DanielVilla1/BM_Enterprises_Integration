# ===== AI GENERATED: AuthorizationService =====
# Purpose: Single place that answers "what may this principal do?"
# Inputs: permission repository, conditional feature flags
# Returns: strongest AccessLevel per capability; 403 when none (deny by default)
# Flow:
# 1. Load matrix grants for the principal's roles from the database
# 2. Drop grants whose conditional setting is switched off
# 3. Keep the strongest level across combined roles

from collections.abc import Mapping

from ..Contract.i_permission_repository import IPermissionRepository
from ..Entity.access import AccessLevel, strongest_level
from ..Entity.business_rule_error import BusinessRuleError
from ..Entity.employee import PermissionGrant, Principal


class AuthorizationService:
    def __init__(self, permissions: IPermissionRepository, conditional_flags: Mapping[str, bool]) -> None:
        self._permissions = permissions
        self._conditional_flags = conditional_flags

    def _is_enabled(self, grant: PermissionGrant) -> bool:
        if grant.conditional_setting is None:
            return True
        return self._conditional_flags.get(grant.conditional_setting, False)

    def level_for(self, principal: Principal, capability: str) -> AccessLevel | None:
        grants = self._permissions.find_grants(capability, principal.role_codes)
        return strongest_level([grant.access_level for grant in grants if self._is_enabled(grant)])

    def require_level(self, principal: Principal, capability: str) -> AccessLevel:
        level = self.level_for(principal, capability)
        if level is None:
            raise BusinessRuleError(
                403, "PERMISSION_DENIED", "Forbidden", "Your role does not allow this action."
            )
        return level

    def capability_levels(self, principal: Principal) -> dict[str, AccessLevel]:
        grants = [
            grant
            for grant in self._permissions.list_for_roles(principal.role_codes)
            if self._is_enabled(grant)
        ]
        levels: dict[str, AccessLevel] = {}
        for capability in sorted({grant.capability for grant in grants}):
            strongest = strongest_level(
                [grant.access_level for grant in grants if grant.capability == capability]
            )
            if strongest is not None:
                levels[capability] = strongest
        return levels

    def list_matrix(self) -> list[PermissionGrant]:
        return self._permissions.list_all()
