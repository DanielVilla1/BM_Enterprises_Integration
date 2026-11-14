# ===== AI GENERATED: or_controller =====
# Purpose: OR upload, signed document URLs, receipt confirmation and correction
# Inputs: multipart upload, validated DTOs, AccessContext
# Returns: document metadata, short-lived URLs, TripResponse
# Flow:
# 1. Upload: crew only (OWN); size capped at 5 MB; content validated in the service
# 2. confirm-receipt: assigned driver only; Idempotency-Key header is required
# 3. Signed URLs are issued only after the access check and expire quickly

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Header, UploadFile

from ..config import get_settings
from ..DTO.account_dto import ProblemDetailsResponse
from ..DTO.or_dto import (
    DocumentUrlResponse,
    OrDocumentResponse,
    ReceiptConfirmationRequest,
)
from ..DTO.trip_dto import TripReasonRequest, TripResponse
from ..Entity.access import AccessLevel
from ..Entity.business_rule_error import BusinessRuleError
from ..Entity.documents import OrDocumentKind
from ..providers import AccessContext, get_or_service, get_trace_id, require_capability
from ..Service.or_service import OrService

router = APIRouter(
    prefix="/api/v1/trips/{trip_id}",
    tags=["or-documents"],
    responses={
        401: {"model": ProblemDetailsResponse},
        403: {"model": ProblemDetailsResponse},
        409: {"model": ProblemDetailsResponse},
    },
)


@router.post(
    "/or-documents",
    response_model=OrDocumentResponse,
    status_code=201,
    responses={413: {"model": ProblemDetailsResponse}, 422: {"model": ProblemDetailsResponse}},
)
async def upload_or_document(
    trip_id: UUID,
    file: UploadFile = File(...),
    kind: OrDocumentKind = Form(OrDocumentKind.SIGNED_OR),
    access: AccessContext = Depends(require_capability("or.upload", only_levels=(AccessLevel.OWN,))),
    service: OrService = Depends(get_or_service),
    trace_id: str = Depends(get_trace_id),
) -> OrDocumentResponse:
    maximum_bytes = get_settings().max_upload_bytes
    raw_content = await file.read(maximum_bytes + 1)
    if len(raw_content) > maximum_bytes:
        raise BusinessRuleError(
            413, "PAYLOAD_TOO_LARGE", "Payload too large", "The file is larger than 5 MB."
        )
    document = service.upload_document(access.principal, access.level, trip_id, kind, raw_content, trace_id)
    return OrDocumentResponse.from_entity(document)


@router.get("/or-documents", response_model=list[OrDocumentResponse])
def list_or_documents(
    trip_id: UUID,
    access: AccessContext = Depends(require_capability("or.view_files")),
    service: OrService = Depends(get_or_service),
) -> list[OrDocumentResponse]:
    documents = service.list_documents(access.principal, access.level, trip_id)
    return [OrDocumentResponse.from_entity(document) for document in documents]


@router.get("/or-documents/{document_id}/url", response_model=DocumentUrlResponse)
def issue_or_document_url(
    trip_id: UUID,
    document_id: UUID,
    access: AccessContext = Depends(require_capability("or.view_files")),
    service: OrService = Depends(get_or_service),
    trace_id: str = Depends(get_trace_id),
) -> DocumentUrlResponse:
    url, expires_in = service.issue_document_url(
        access.principal, access.level, trip_id, document_id, trace_id
    )
    return DocumentUrlResponse(url=url, expires_in_seconds=expires_in)


@router.post("/confirm-receipt", response_model=TripResponse)
def confirm_receipt(
    trip_id: UUID,
    payload: ReceiptConfirmationRequest,
    idempotency_key: str = Header(
        alias="Idempotency-Key", min_length=8, max_length=128, pattern=r"^[A-Za-z0-9_-]+$"
    ),
    access: AccessContext = Depends(require_capability("or.confirm_receipt", only_levels=(AccessLevel.OWN,))),
    service: OrService = Depends(get_or_service),
    trace_id: str = Depends(get_trace_id),
) -> TripResponse:
    received_at: datetime = payload.received_at
    view = service.confirm_receipt(
        access.principal, access.level, trip_id, received_at, idempotency_key, trace_id
    )
    return TripResponse.from_view(view)


@router.post("/receipt-correction", response_model=TripResponse)
def correct_receipt_confirmation(
    trip_id: UUID,
    payload: TripReasonRequest,
    access: AccessContext = Depends(require_capability("or.correct_confirmation", AccessLevel.FULL)),
    service: OrService = Depends(get_or_service),
    trace_id: str = Depends(get_trace_id),
) -> TripResponse:
    view = service.correct_confirmation(access.principal, trip_id, payload.reason, trace_id)
    return TripResponse.from_view(view)
