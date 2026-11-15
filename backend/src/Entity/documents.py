# ===== AI GENERATED: document_entities =====
# Purpose: Stored OR documents and idempotency records
# Inputs: values mapped by repositories
# Returns: frozen dataclasses and the document kind enum
# Flow:
# 1. SIGNED_OR is required for completion; STAMPED_COPY is optional evidence
# 2. A new upload of the same kind supersedes the previous one (history kept)

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class OrDocumentKind(StrEnum):
    SIGNED_OR = "SIGNED_OR"
    STAMPED_COPY = "STAMPED_COPY"


@dataclass(frozen=True)
class OrDocument:
    document_id: UUID
    trip_id: UUID
    kind: OrDocumentKind
    storage_path: str
    content_type: str
    size_bytes: int
    uploaded_by: UUID | None
    uploaded_at: datetime
    superseded_at: datetime | None


@dataclass(frozen=True)
class IdempotencyRecord:
    key: str
    actor_id: UUID
    scope: str
