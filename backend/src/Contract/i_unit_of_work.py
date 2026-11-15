# ===== AI GENERATED: IUnitOfWork =====
# Purpose: Port for transaction control used by services
# Inputs: none
# Returns: commit / rollback signatures
# Flow:
# 1. Services call commit once their rule checks pass
# 2. Any failure rolls back every repository write

from typing import Protocol


class IUnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...
