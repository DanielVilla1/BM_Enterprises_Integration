# ===== AI GENERATED: document_repositories =====
# Purpose: SQLAlchemy implementations for OR documents and idempotency keys
# Inputs: Session
# Returns: entities (never ORM rows)
# Flow:
# 1. Documents are never deleted: a new upload supersedes the previous one
# 2. Idempotency rows are written in the same transaction as the action

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..Entity.documents import IdempotencyRecord, OrDocument, OrDocumentKind
from .orm_models import IdempotencyKeyRow, OrDocumentRow, utc_now


def _document(row: OrDocumentRow) -> OrDocument:
    return OrDocument(
        document_id=row.document_id,
        trip_id=row.trip_id,
        kind=OrDocumentKind(row.kind),
        storage_path=row.storage_path,
        content_type=row.content_type,
        size_bytes=row.size_bytes,
        uploaded_by=row.uploaded_by,
        uploaded_at=row.uploaded_at,
        superseded_at=row.superseded_at,
    )


class OrDocumentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(
        self,
        trip_id: UUID,
        kind: OrDocumentKind,
        storage_path: str,
        content_type: str,
        size_bytes: int,
        uploaded_by: UUID | None,
    ) -> OrDocument:
        row = OrDocumentRow(
            trip_id=trip_id,
            kind=kind.value,
            storage_path=storage_path,
            content_type=content_type,
            size_bytes=size_bytes,
            uploaded_by=uploaded_by,
        )
        self._session.add(row)
        self._session.flush()
        self._session.refresh(row)
        return _document(row)

    def supersede_active(self, trip_id: UUID, kind: OrDocumentKind) -> None:
        self._session.execute(
            update(OrDocumentRow)
            .where(
                OrDocumentRow.trip_id == trip_id,
                OrDocumentRow.kind == kind.value,
                OrDocumentRow.superseded_at.is_(None),
            )
            .values(superseded_at=utc_now())
        )

    def get(self, document_id: UUID) -> OrDocument | None:
        row = self._session.get(OrDocumentRow, document_id)
        return _document(row) if row is not None else None

    def list_for_trip(self, trip_id: UUID, include_superseded: bool) -> list[OrDocument]:
        statement = select(OrDocumentRow).where(OrDocumentRow.trip_id == trip_id)
        if not include_superseded:
            statement = statement.where(OrDocumentRow.superseded_at.is_(None))
        statement = statement.order_by(OrDocumentRow.uploaded_at, OrDocumentRow.document_id)
        return [_document(row) for row in self._session.scalars(statement).all()]

    def list_active_for_trips(self, trip_ids: list[UUID]) -> dict[UUID, list[OrDocument]]:
        grouped: dict[UUID, list[OrDocument]] = {trip_id: [] for trip_id in trip_ids}
        if not trip_ids:
            return grouped
        statement = (
            select(OrDocumentRow)
            .where(OrDocumentRow.trip_id.in_(trip_ids), OrDocumentRow.superseded_at.is_(None))
            .order_by(OrDocumentRow.uploaded_at, OrDocumentRow.document_id)
        )
        for row in self._session.scalars(statement).all():
            grouped[row.trip_id].append(_document(row))
        return grouped


class IdempotencyRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, key: str, actor_id: UUID) -> IdempotencyRecord | None:
        row = self._session.get(IdempotencyKeyRow, (key, actor_id))
        if row is None:
            return None
        return IdempotencyRecord(key=row.key, actor_id=row.actor_id, scope=row.scope)

    def save(self, key: str, actor_id: UUID, scope: str) -> None:
        self._session.add(IdempotencyKeyRow(key=key, actor_id=actor_id, scope=scope))
        self._session.flush()
