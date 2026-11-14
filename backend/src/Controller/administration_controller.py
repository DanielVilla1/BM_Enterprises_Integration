# ===== AI GENERATED: administration_controller =====
# Purpose: Owner-only permission matrix and audit log views
# Inputs: page parameters
# Returns: PermissionMatrixResponse, AuditPageResponse
# Flow:
# 1. require_capability("audit_user.manage") gates both routes
# 2. Page size is capped at 100

from fastapi import APIRouter, Depends, Query

from ..DTO.account_dto import (
    AuditPageResponse,
    AuditRecordResponse,
    PermissionGrantResponse,
    PermissionMatrixResponse,
)
from ..providers import (
    AccessContext,
    get_audit_service,
    get_authorization_service,
    require_capability,
)
from ..Service.audit_service import AuditService
from ..Service.authorization_service import AuthorizationService

router = APIRouter(prefix="/api/v1", tags=["administration"])


@router.get("/permission-matrix", response_model=PermissionMatrixResponse)
def read_permission_matrix(
    _access: AccessContext = Depends(require_capability("audit_user.manage")),
    authorization: AuthorizationService = Depends(get_authorization_service),
) -> PermissionMatrixResponse:
    return PermissionMatrixResponse(
        grants=[PermissionGrantResponse.from_entity(grant) for grant in authorization.list_matrix()]
    )


@router.get("/audit-logs", response_model=AuditPageResponse)
def read_audit_log(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0, le=100000),
    _access: AccessContext = Depends(require_capability("audit_user.manage")),
    service: AuditService = Depends(get_audit_service),
) -> AuditPageResponse:
    records = service.list_records(limit, offset)
    return AuditPageResponse(
        items=[AuditRecordResponse.from_entity(record) for record in records],
        limit=limit,
        offset=offset,
    )
