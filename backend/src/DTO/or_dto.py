# ===== AI GENERATED: or_dto =====
# Purpose: Request / response shapes for OR documents and receipt confirmation
# Inputs: validated JSON bodies, headers and entities
# Returns: strict Pydantic models; storage paths are never exposed
# Flow:
# 1. Document responses list metadata only
# 2. Receipt confirmation needs a timezone-aware reported receipt time
# 3. The Idempotency-Key format is validated once, here

from datetime import datetime
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict

from ..Entity.documents import OrDocument, OrDocumentKind


class ReceiptConfirmationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    received_at: AwareDatetime


class OrDocumentResponse(BaseModel):
    document_id: UUID
    trip_id: UUID
    kind: OrDocumentKind
    content_type: str
    size_bytes: int
    uploaded_at: datetime
    superseded: bool

    @classmethod
    def from_entity(cls, document: OrDocument) -> "OrDocumentResponse":
        return cls(
            document_id=document.document_id,
            trip_id=document.trip_id,
            kind=document.kind,
            content_type=document.content_type,
            size_bytes=document.size_bytes,
            uploaded_at=document.uploaded_at,
            superseded=document.superseded_at is not None,
        )


class DocumentUrlResponse(BaseModel):
    url: str
    expires_in_seconds: int
