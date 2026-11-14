# ===== AI GENERATED: AuditRepository =====
# Purpose: Append-only audit persistence
# Inputs: Session
# Returns: AuditRecord entities
# Flow:
# 1. append inserts one row (no update or delete methods exist)
# 2. list_page reads newest first

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..Entity.employee import AuditRecord
from .orm_models import AuditLogRow


class AuditRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_entity(row: AuditLogRow) -> AuditRecord:
        return AuditRecord(
            audit_id=row.audit_id,
            occurred_at=row.occurred_at,
            actor_employee_id=row.actor_employee_id,
            action=row.action,
            entity_type=row.entity_type,
            entity_id=row.entity_id,
            details=dict(row.details or {}),
            trace_id=row.trace_id,
        )

    def append(
        self,
        actor_employee_id: UUID | None,
        action: str,
        entity_type: str,
        entity_id: str | None,
        details: dict[str, object],
        trace_id: str | None,
    ) -> AuditRecord:
        row = AuditLogRow(
            actor_employee_id=actor_employee_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            trace_id=trace_id,
        )
        self._session.add(row)
        self._session.flush()
        self._session.refresh(row)
        return self._to_entity(row)

    def list_page(self, limit: int, offset: int) -> list[AuditRecord]:
        statement = (
            select(AuditLogRow)
            .order_by(AuditLogRow.occurred_at.desc(), AuditLogRow.audit_id)
            .limit(limit)
            .offset(offset)
        )
        return [self._to_entity(row) for row in self._session.scalars(statement).all()]
