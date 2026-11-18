# ===== AI GENERATED: client_controller =====
# Purpose: Client endpoints (delivery_order.manage capability)
# Inputs: validated DTOs, AccessContext
# Returns: client DTOs
# Flow:
# 1. Reads need any grant; writes need FULL (Dispatcher)
# 2. Delegate to ClientService; map entities to DTOs

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from ..DTO.account_dto import ProblemDetailsResponse
from ..DTO.operations_dto import (
    ClientCreateRequest,
    ClientPageResponse,
    ClientResponse,
    ClientUpdateRequest,
)
from ..Entity.access import AccessLevel
from ..providers import AccessContext, get_client_service, get_trace_id, require_capability
from ..Service.client_service import ClientService

CAPABILITY = "delivery_order.manage"

router = APIRouter(
    prefix="/api/v1/clients",
    tags=["clients"],
    responses={401: {"model": ProblemDetailsResponse}, 403: {"model": ProblemDetailsResponse}},
)


@router.get("", response_model=ClientPageResponse)
def list_clients(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0, le=100000),
    active: bool | None = None,
    _access: AccessContext = Depends(require_capability(CAPABILITY)),
    service: ClientService = Depends(get_client_service),
) -> ClientPageResponse:
    clients = service.list_clients(limit, offset, active)
    return ClientPageResponse(
        items=[ClientResponse.from_entity(client) for client in clients], limit=limit, offset=offset
    )


@router.post("", response_model=ClientResponse, status_code=201)
def create_client(
    payload: ClientCreateRequest,
    access: AccessContext = Depends(require_capability(CAPABILITY, AccessLevel.FULL)),
    service: ClientService = Depends(get_client_service),
    trace_id: str = Depends(get_trace_id),
) -> ClientResponse:
    client = service.create_client(
        access.principal,
        payload.name,
        payload.address,
        payload.contact_person,
        payload.contact_phone,
        trace_id,
    )
    return ClientResponse.from_entity(client)


@router.get("/{client_id}", response_model=ClientResponse)
def read_client(
    client_id: UUID,
    _access: AccessContext = Depends(require_capability(CAPABILITY)),
    service: ClientService = Depends(get_client_service),
) -> ClientResponse:
    return ClientResponse.from_entity(service.get_client(client_id))


@router.patch("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: UUID,
    payload: ClientUpdateRequest,
    access: AccessContext = Depends(require_capability(CAPABILITY, AccessLevel.FULL)),
    service: ClientService = Depends(get_client_service),
    trace_id: str = Depends(get_trace_id),
) -> ClientResponse:
    client = service.update_client(access.principal, client_id, payload.changes(), trace_id)
    return ClientResponse.from_entity(client)
