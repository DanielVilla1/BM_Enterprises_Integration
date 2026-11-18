# ===== AI GENERATED: delivery_order_controller =====
# Purpose: Delivery order endpoints (DO-01, CT-01)
# Inputs: validated DTOs, AccessContext
# Returns: order DTOs; new orders are PENDING
# Flow:
# 1. Reads need any grant (Owner/Accounting view); writes need FULL (Dispatcher)
# 2. Delegate to DeliveryOrderService; map entities to DTOs

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from ..DTO.account_dto import ProblemDetailsResponse
from ..DTO.operations_dto import (
    DeliveryOrderCancelRequest,
    DeliveryOrderCreateRequest,
    DeliveryOrderPageResponse,
    DeliveryOrderResponse,
    DeliveryOrderUpdateRequest,
)
from ..Entity.access import AccessLevel
from ..Entity.operations import OrderStatus
from ..providers import AccessContext, get_delivery_order_service, get_trace_id, require_capability
from ..Service.delivery_order_service import DeliveryOrderService

CAPABILITY = "delivery_order.manage"

router = APIRouter(
    prefix="/api/v1/delivery-orders",
    tags=["delivery-orders"],
    responses={401: {"model": ProblemDetailsResponse}, 403: {"model": ProblemDetailsResponse}},
)


@router.get("", response_model=DeliveryOrderPageResponse)
def list_delivery_orders(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0, le=100000),
    status: OrderStatus | None = None,
    client_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    _access: AccessContext = Depends(require_capability(CAPABILITY)),
    service: DeliveryOrderService = Depends(get_delivery_order_service),
) -> DeliveryOrderPageResponse:
    orders = service.list_orders(limit, offset, status, client_id, date_from, date_to)
    return DeliveryOrderPageResponse(
        items=[DeliveryOrderResponse.from_entity(order) for order in orders], limit=limit, offset=offset
    )


@router.post(
    "",
    response_model=DeliveryOrderResponse,
    status_code=201,
    responses={409: {"model": ProblemDetailsResponse}, 422: {"model": ProblemDetailsResponse}},
)
def create_delivery_order(
    payload: DeliveryOrderCreateRequest,
    access: AccessContext = Depends(require_capability(CAPABILITY, AccessLevel.FULL)),
    service: DeliveryOrderService = Depends(get_delivery_order_service),
    trace_id: str = Depends(get_trace_id),
) -> DeliveryOrderResponse:
    order = service.create_order(
        access.principal,
        payload.client_id,
        payload.client_reference,
        payload.pickup_location,
        payload.delivery_location,
        payload.scheduled_date,
        payload.total_weight_tons,
        payload.notes,
        trace_id,
    )
    return DeliveryOrderResponse.from_entity(order)


@router.get("/{order_id}", response_model=DeliveryOrderResponse)
def read_delivery_order(
    order_id: UUID,
    _access: AccessContext = Depends(require_capability(CAPABILITY)),
    service: DeliveryOrderService = Depends(get_delivery_order_service),
) -> DeliveryOrderResponse:
    return DeliveryOrderResponse.from_entity(service.get_order(order_id))


@router.patch("/{order_id}", response_model=DeliveryOrderResponse)
def update_delivery_order(
    order_id: UUID,
    payload: DeliveryOrderUpdateRequest,
    access: AccessContext = Depends(require_capability(CAPABILITY, AccessLevel.FULL)),
    service: DeliveryOrderService = Depends(get_delivery_order_service),
    trace_id: str = Depends(get_trace_id),
) -> DeliveryOrderResponse:
    order = service.update_order(access.principal, order_id, payload.changes(), trace_id)
    return DeliveryOrderResponse.from_entity(order)


@router.post("/{order_id}/cancel", response_model=DeliveryOrderResponse)
def cancel_delivery_order(
    order_id: UUID,
    payload: DeliveryOrderCancelRequest,
    access: AccessContext = Depends(require_capability(CAPABILITY, AccessLevel.FULL)),
    service: DeliveryOrderService = Depends(get_delivery_order_service),
    trace_id: str = Depends(get_trace_id),
) -> DeliveryOrderResponse:
    order = service.cancel_order(access.principal, order_id, payload.reason, trace_id)
    return DeliveryOrderResponse.from_entity(order)
