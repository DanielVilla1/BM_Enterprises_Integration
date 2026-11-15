# ===== AI GENERATED: trip_controller =====
# Purpose: Dispatch endpoints: assign, progress, cancel/fail, crew, truck replacement
# Inputs: validated DTOs, AccessContext from the permission matrix
# Returns: trip DTOs; 409 problem+json with stable codes for rule failures
# Flow:
# 1. dispatch.assign (Owner, Dispatcher) assigns, clears, changes crew
# 2. trip.progress with level OWN: only the assigned driver accepts, departs, delivers
# 3. trip.assignment_view: crew see their own trips; Owner/Dispatcher see all

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from ..DTO.account_dto import ProblemDetailsResponse
from ..DTO.trip_dto import (
    DispatchResourcesResponse,
    TripAssignRequest,
    TripCrewRequest,
    TripPageResponse,
    TripReasonRequest,
    TripResponse,
    TruckReplacementRequest,
)
from ..Entity.access import AccessLevel
from ..Entity.dispatch import TripStatus
from ..providers import AccessContext, get_trace_id, get_trip_service, require_capability
from ..Service.trip_service import TripService

router = APIRouter(
    prefix="/api/v1",
    tags=["dispatch"],
    responses={
        401: {"model": ProblemDetailsResponse},
        403: {"model": ProblemDetailsResponse},
        409: {"model": ProblemDetailsResponse},
    },
)


@router.get("/dispatch/resources", response_model=DispatchResourcesResponse)
def read_dispatch_resources(
    _access: AccessContext = Depends(require_capability("dispatch.assign")),
    service: TripService = Depends(get_trip_service),
) -> DispatchResourcesResponse:
    return DispatchResourcesResponse.from_entity(service.list_resources())


@router.get("/trips", response_model=TripPageResponse)
def list_trips(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0, le=100000),
    status: TripStatus | None = None,
    order_id: UUID | None = None,
    truck_id: UUID | None = None,
    _access: AccessContext = Depends(require_capability("dispatch.assign")),
    service: TripService = Depends(get_trip_service),
) -> TripPageResponse:
    views = service.list_trips(limit, offset, status, order_id, truck_id)
    return TripPageResponse(
        items=[TripResponse.from_view(view) for view in views], limit=limit, offset=offset
    )


@router.get("/trips/assigned", response_model=TripPageResponse)
def list_assigned_trips(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0, le=100000),
    status: TripStatus | None = None,
    access: AccessContext = Depends(require_capability("trip.assignment_view")),
    service: TripService = Depends(get_trip_service),
) -> TripPageResponse:
    views = service.list_assigned(access.principal, access.level, limit, offset, status)
    return TripPageResponse(
        items=[TripResponse.from_view(view) for view in views], limit=limit, offset=offset
    )


@router.get("/trips/{trip_id}", response_model=TripResponse)
def read_trip(
    trip_id: UUID,
    access: AccessContext = Depends(require_capability("trip.assignment_view")),
    service: TripService = Depends(get_trip_service),
) -> TripResponse:
    return TripResponse.from_view(service.get_trip(access.principal, access.level, trip_id))


@router.post("/delivery-orders/{order_id}/trips", response_model=TripResponse, status_code=201)
def assign_trip(
    order_id: UUID,
    payload: TripAssignRequest,
    access: AccessContext = Depends(require_capability("dispatch.assign", AccessLevel.FULL)),
    service: TripService = Depends(get_trip_service),
    trace_id: str = Depends(get_trace_id),
) -> TripResponse:
    view = service.create_trip(
        access.principal,
        order_id,
        payload.truck_id,
        payload.driver_id,
        tuple(payload.helper_ids),
        payload.load_tons,
        trace_id,
    )
    return TripResponse.from_view(view)


@router.post("/trips/{trip_id}/accept", response_model=TripResponse)
def accept_trip(
    trip_id: UUID,
    access: AccessContext = Depends(require_capability("trip.progress", only_levels=(AccessLevel.OWN,))),
    service: TripService = Depends(get_trip_service),
    trace_id: str = Depends(get_trace_id),
) -> TripResponse:
    return TripResponse.from_view(service.accept_trip(access.principal, access.level, trip_id, trace_id))


@router.post("/trips/{trip_id}/clear-dispatch", response_model=TripResponse)
def clear_trip_dispatch(
    trip_id: UUID,
    access: AccessContext = Depends(require_capability("dispatch.assign", AccessLevel.FULL)),
    service: TripService = Depends(get_trip_service),
    trace_id: str = Depends(get_trace_id),
) -> TripResponse:
    return TripResponse.from_view(service.clear_dispatch(access.principal, trip_id, trace_id))


@router.post("/trips/{trip_id}/depart", response_model=TripResponse)
def depart_trip(
    trip_id: UUID,
    access: AccessContext = Depends(require_capability("trip.progress", only_levels=(AccessLevel.OWN,))),
    service: TripService = Depends(get_trip_service),
    trace_id: str = Depends(get_trace_id),
) -> TripResponse:
    return TripResponse.from_view(service.depart_trip(access.principal, access.level, trip_id, trace_id))


@router.post("/trips/{trip_id}/deliver", response_model=TripResponse)
def deliver_trip(
    trip_id: UUID,
    access: AccessContext = Depends(require_capability("trip.progress", only_levels=(AccessLevel.OWN,))),
    service: TripService = Depends(get_trip_service),
    trace_id: str = Depends(get_trace_id),
) -> TripResponse:
    return TripResponse.from_view(service.record_delivery(access.principal, access.level, trip_id, trace_id))


@router.post("/trips/{trip_id}/cancel", response_model=TripResponse)
def cancel_trip(
    trip_id: UUID,
    payload: TripReasonRequest,
    access: AccessContext = Depends(require_capability("trip.cancel_or_fail", AccessLevel.FULL)),
    service: TripService = Depends(get_trip_service),
    trace_id: str = Depends(get_trace_id),
) -> TripResponse:
    return TripResponse.from_view(service.cancel_trip(access.principal, trip_id, payload.reason, trace_id))


@router.post("/trips/{trip_id}/fail", response_model=TripResponse)
def fail_trip(
    trip_id: UUID,
    payload: TripReasonRequest,
    access: AccessContext = Depends(require_capability("trip.cancel_or_fail", AccessLevel.FULL)),
    service: TripService = Depends(get_trip_service),
    trace_id: str = Depends(get_trace_id),
) -> TripResponse:
    return TripResponse.from_view(service.fail_trip(access.principal, trip_id, payload.reason, trace_id))


@router.put("/trips/{trip_id}/crew", response_model=TripResponse)
def change_trip_crew(
    trip_id: UUID,
    payload: TripCrewRequest,
    access: AccessContext = Depends(require_capability("dispatch.assign", AccessLevel.FULL)),
    service: TripService = Depends(get_trip_service),
    trace_id: str = Depends(get_trace_id),
) -> TripResponse:
    view = service.change_crew(
        access.principal, trip_id, payload.driver_id, tuple(payload.helper_ids), trace_id
    )
    return TripResponse.from_view(view)


@router.post("/trips/{trip_id}/truck-replacement", response_model=TripResponse)
def replace_trip_truck(
    trip_id: UUID,
    payload: TruckReplacementRequest,
    access: AccessContext = Depends(require_capability("truck.replace", AccessLevel.FULL)),
    service: TripService = Depends(get_trip_service),
    trace_id: str = Depends(get_trace_id),
) -> TripResponse:
    view = service.replace_truck(
        access.principal,
        trip_id,
        payload.replacement_truck_id,
        payload.reason,
        payload.original_truck_needs_maintenance,
        trace_id,
    )
    return TripResponse.from_view(view)
