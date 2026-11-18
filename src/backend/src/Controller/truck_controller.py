# ===== AI GENERATED: truck_controller =====
# Purpose: Truck and maintenance endpoints (truck.manage capability)
# Inputs: validated DTOs, AccessContext
# Returns: truck and maintenance DTOs
# Flow:
# 1. Reads need any grant (Dispatcher views); writes need FULL (Owner, Fleet)
# 2. Delegate to TruckService; map entities to DTOs

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from ..DTO.account_dto import ProblemDetailsResponse
from ..DTO.fleet_dto import (
    MaintenanceRecordResponse,
    MaintenanceStartRequest,
    TruckCreateRequest,
    TruckPageResponse,
    TruckResponse,
    TruckUpdateRequest,
)
from ..Entity.access import AccessLevel
from ..Entity.fleet import TruckStatus
from ..providers import AccessContext, get_trace_id, get_truck_service, require_capability
from ..Service.truck_service import TruckService

CAPABILITY = "truck.manage"

router = APIRouter(
    prefix="/api/v1/trucks",
    tags=["trucks"],
    responses={401: {"model": ProblemDetailsResponse}, 403: {"model": ProblemDetailsResponse}},
)


@router.get("", response_model=TruckPageResponse)
def list_trucks(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0, le=100000),
    status: TruckStatus | None = None,
    active: bool | None = None,
    _access: AccessContext = Depends(require_capability(CAPABILITY)),
    service: TruckService = Depends(get_truck_service),
) -> TruckPageResponse:
    trucks = service.list_trucks(limit, offset, status, active)
    return TruckPageResponse(
        items=[TruckResponse.from_entity(truck) for truck in trucks], limit=limit, offset=offset
    )


@router.post("", response_model=TruckResponse, status_code=201)
def create_truck(
    payload: TruckCreateRequest,
    access: AccessContext = Depends(require_capability(CAPABILITY, AccessLevel.FULL)),
    service: TruckService = Depends(get_truck_service),
    trace_id: str = Depends(get_trace_id),
) -> TruckResponse:
    truck = service.create_truck(
        access.principal, payload.plate_number, payload.description, payload.capacity_tons, trace_id
    )
    return TruckResponse.from_entity(truck)


@router.get("/{truck_id}", response_model=TruckResponse)
def read_truck(
    truck_id: UUID,
    _access: AccessContext = Depends(require_capability(CAPABILITY)),
    service: TruckService = Depends(get_truck_service),
) -> TruckResponse:
    return TruckResponse.from_entity(service.get_truck(truck_id))


@router.patch("/{truck_id}", response_model=TruckResponse)
def update_truck(
    truck_id: UUID,
    payload: TruckUpdateRequest,
    access: AccessContext = Depends(require_capability(CAPABILITY, AccessLevel.FULL)),
    service: TruckService = Depends(get_truck_service),
    trace_id: str = Depends(get_trace_id),
) -> TruckResponse:
    truck = service.update_truck(access.principal, truck_id, payload.changes(), trace_id)
    return TruckResponse.from_entity(truck)


@router.get("/{truck_id}/maintenance", response_model=list[MaintenanceRecordResponse])
def list_truck_maintenance(
    truck_id: UUID,
    _access: AccessContext = Depends(require_capability(CAPABILITY)),
    service: TruckService = Depends(get_truck_service),
) -> list[MaintenanceRecordResponse]:
    return [MaintenanceRecordResponse.from_entity(row) for row in service.list_maintenance(truck_id)]


@router.post("/{truck_id}/maintenance", response_model=MaintenanceRecordResponse, status_code=201)
def start_truck_maintenance(
    truck_id: UUID,
    payload: MaintenanceStartRequest,
    access: AccessContext = Depends(require_capability(CAPABILITY, AccessLevel.FULL)),
    service: TruckService = Depends(get_truck_service),
    trace_id: str = Depends(get_trace_id),
) -> MaintenanceRecordResponse:
    record = service.start_maintenance(access.principal, truck_id, payload.reason, trace_id)
    return MaintenanceRecordResponse.from_entity(record)


@router.post("/{truck_id}/maintenance/complete", response_model=MaintenanceRecordResponse)
def complete_truck_maintenance(
    truck_id: UUID,
    access: AccessContext = Depends(require_capability(CAPABILITY, AccessLevel.FULL)),
    service: TruckService = Depends(get_truck_service),
    trace_id: str = Depends(get_trace_id),
) -> MaintenanceRecordResponse:
    record = service.complete_maintenance(access.principal, truck_id, trace_id)
    return MaintenanceRecordResponse.from_entity(record)
