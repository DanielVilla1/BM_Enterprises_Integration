# ===== AI GENERATED: document_repository_contracts =====
# Purpose: Ports for OR document metadata and idempotency keys
# Inputs: domain values
# Returns: OrDocument and IdempotencyRecord entities
# Flow:
# 1. Documents: add, supersede the active one of a kind, list
# 2. Idempotency: remember which action a key already performed

from typing import Protocol
from uuid import UUID

from ..Entity.documents import IdempotencyRecord, OrDocument, OrDocumentKind


class IOrDocumentRepository(Protocol):
    def add(
        self,
        trip_id: UUID,
        kind: OrDocumentKind,
        storage_path: str,
        content_type: str,
        size_bytes: int,
        uploaded_by: UUID | None,
    ) -> OrDocument: ...

    def supersede_active(self, trip_id: UUID, kind: OrDocumentKind) -> None: ...

    def get(self, document_id: UUID) -> OrDocument | None: ...

    def list_for_trip(self, trip_id: UUID, include_superseded: bool) -> list[OrDocument]: ...

    def list_active_for_trips(self, trip_ids: list[UUID]) -> dict[UUID, list[OrDocument]]: ...


class IIdempotencyRepository(Protocol):
    def get(self, key: str, actor_id: UUID) -> IdempotencyRecord | None: ...

    def save(self, key: str, actor_id: UUID, scope: str) -> None: ...
