# ===== AI GENERATED: IIdentityDirectory =====
# Purpose: Port for listing identity-provider users (reconciliation)
# Inputs: none
# Returns: DirectoryUser list or IdentityDirectoryError
# Flow:
# 1. list_users returns every user the provider knows
# 2. Any transport or format failure raises IdentityDirectoryError

from dataclasses import dataclass
from typing import Protocol


class IdentityDirectoryError(Exception):
    """The directory could not be read completely; callers must not act on partial data."""


@dataclass(frozen=True)
class DirectoryUser:
    user_id: str
    verified_email: str | None


class IIdentityDirectory(Protocol):
    def list_users(self) -> list[DirectoryUser]: ...
