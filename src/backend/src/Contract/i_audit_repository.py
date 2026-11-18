# ===== AI GENERATED: IAuditRepository =====
# Purpose: Port for the append-only audit log
# Inputs: audit values
# Returns: AuditRecord entities
# Flow:
# 1. append only (no update or delete exists)
# 2. list newest first with a page cap

from typing import Protocol
from uuid import UUID

from ..Entity.employee import AuditRecord


class IAuditRepository(Protocol):
    def append(
        self,
        actor_employee_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: str | None,
        details: dict[str, object],
        trace_id: str | None,
    ) -> AuditRecord: ...

    def list_page(self, limit: int, offset: int) -> list[AuditRecord]: ...
