# ===== AI GENERATED: role_rules =====
# Purpose: Static separation-of-duty rules for role assignment
# Inputs: a set of role codes
# Returns: the forbidden role pairs contained in the set
# Flow:
# 1. Define back-office roles and forbidden pairs (spec 3.2)
# 2. Report every violating pair for a proposed role set

from itertools import combinations

from .access import RoleCode

BACK_OFFICE_ROLES: frozenset[RoleCode] = frozenset(
    {
        RoleCode.OWNER,
        RoleCode.DISPATCHER,
        RoleCode.FLEET_MANAGER,
        RoleCode.HR_PAYROLL,
        RoleCode.ACCOUNTING,
    }
)
FIELD_ROLES: frozenset[RoleCode] = frozenset({RoleCode.DRIVER, RoleCode.HELPER})

_EXPLICIT_FORBIDDEN_PAIRS: frozenset[frozenset[RoleCode]] = frozenset(
    {
        frozenset({RoleCode.HR_PAYROLL, RoleCode.ACCOUNTING}),
        frozenset({RoleCode.DISPATCHER, RoleCode.HR_PAYROLL}),
        frozenset({RoleCode.DISPATCHER, RoleCode.ACCOUNTING}),
    }
)


def is_forbidden_pair(first_role: RoleCode, second_role: RoleCode) -> bool:
    """True when the two roles must not belong to one user without an exception."""
    if frozenset({first_role, second_role}) in _EXPLICIT_FORBIDDEN_PAIRS:
        return True
    roles = {first_role, second_role}
    return bool(roles & FIELD_ROLES) and bool(roles & BACK_OFFICE_ROLES)


def find_forbidden_pairs(role_codes: set[RoleCode]) -> list[tuple[RoleCode, RoleCode]]:
    """List every forbidden pair inside the proposed role set, in stable order."""
    ordered_roles = sorted(role_codes, key=lambda role: role.value)
    return [
        (first_role, second_role)
        for first_role, second_role in combinations(ordered_roles, 2)
        if is_forbidden_pair(first_role, second_role)
    ]
