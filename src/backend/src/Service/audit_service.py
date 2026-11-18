# ===== AI GENERATED: AuditService =====
# Purpose: Read-only access to the audit log
# Inputs: audit repository, page bounds
# Returns: AuditRecord list newest first
# Flow:
# 1. Clamp the page size, then read

from ..Contract.i_audit_repository import IAuditRepository
from ..Entity.employee import AuditRecord

MAXIMUM_PAGE_SIZE = 100


class AuditService:
    def __init__(self, audit: IAuditRepository) -> None:
        self._audit = audit

    def list_records(self, limit: int, offset: int) -> list[AuditRecord]:
        return self._audit.list_page(min(max(limit, 1), MAXIMUM_PAGE_SIZE), max(offset, 0))
