# ===== AI GENERATED: access_vocabulary =====
# Purpose: Role codes and access levels from the permission matrix
# Inputs: none
# Returns: RoleCode, AccessLevel enums with ranking helper
# Flow:
# 1. Enumerate the seven business roles
# 2. Enumerate matrix cell levels (Full, View, Ltd, Own)
# 3. Rank levels so combined roles keep the strongest

from enum import StrEnum


class RoleCode(StrEnum):
    """The seven business roles (spec section 3.1)."""

    OWNER = "OWNER"
    DISPATCHER = "DISPATCHER"
    FLEET_MANAGER = "FLEET_MANAGER"
    DRIVER = "DRIVER"
    HELPER = "HELPER"
    HR_PAYROLL = "HR_PAYROLL"
    ACCOUNTING = "ACCOUNTING"


class AccessLevel(StrEnum):
    """Matrix cell values. A missing cell means no access."""

    FULL = "FULL"
    VIEW = "VIEW"
    LTD = "LTD"
    OWN = "OWN"

    @property
    def rank(self) -> int:
        """Order used when a user holds several roles."""
        return {"FULL": 4, "VIEW": 3, "LTD": 2, "OWN": 1}[self.value]


def strongest_level(levels: list[AccessLevel]) -> AccessLevel | None:
    """Return the highest-ranked level, or None when the list is empty."""
    if not levels:
        return None
    return max(levels, key=lambda level: level.rank)
