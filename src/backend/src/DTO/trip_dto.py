# ===== AI GENERATED: trip_dto =====
# Purpose: Request / response shapes for trips, crew and dispatch resources
# Inputs: validated JSON bodies and entities
# Returns: strict Pydantic models (extra fields forbidden on input)
# Flow:
# 1. Crew: exactly one driver and one or two helpers
# 2. Responses carry the order's route so crews see where to go
# 3. Loads are metric tons serialized as JSON numbers

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, StringConstraints

from ..Entity.dispatch import DispatchResources, ResourceAvailability, TripStatus, TripView
from .or_dto import OrDocumentResponse

ReasonText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=500)]
LoadTons = Annotated[
    Decimal,
    Field(gt=0, le=100000, max_digits=9, decimal_places=3),
    PlainSerializer(float, return_type=float, when_used="json"),
]
HelperIds = Annotated[list[UUID], Field(min_length=1, max_length=2)]


class TripAssignRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    truck_id: UUID
    driver_id: UUID
    helper_ids: HelperIds
    load_tons: LoadTons


class TripCrewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    driver_id: UUID
    helper_ids: HelperIds


class TripReasonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: ReasonText


class TruckReplacementRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    replacement_truck_id: UUID
    reason: ReasonText
    original_truck_needs_maintenance: bool


class TripResponse(BaseModel):
    trip_id: UUID
    order_id: UUID
    truck_id: UUID
    load_tons: Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]
    status: TripStatus
    driver_id: UUID
    helper_ids: list[UUID]
    scheduled_date: date
    pickup_location: str
    delivery_location: str
    accepted_at: datetime | None
    cleared_at: datetime | None
    departed_at: datetime | None
    delivered_at: datetime | None
    closed_reason: str | None
    created_at: datetime
    or_uploaded_at: datetime | None
    receipt_confirmed_at: datetime | None
    receipt_received_at: datetime | None
    documents: list[OrDocumentResponse]

    @classmethod
    def from_view(cls, view: TripView) -> "TripResponse":
        trip = view.trip
        return cls(
            trip_id=trip.trip_id,
            order_id=trip.order_id,
            truck_id=trip.truck_id,
            load_tons=trip.load_tons,
            status=trip.status,
            driver_id=trip.driver_id,
            helper_ids=list(trip.helper_ids),
            scheduled_date=view.scheduled_date,
            pickup_location=view.pickup_location,
            delivery_location=view.delivery_location,
            accepted_at=trip.accepted_at,
            cleared_at=trip.cleared_at,
            departed_at=trip.departed_at,
            delivered_at=trip.delivered_at,
            closed_reason=trip.closed_reason,
            created_at=trip.created_at,
            or_uploaded_at=trip.or_uploaded_at,
            receipt_confirmed_at=trip.receipt_confirmed_at,
            receipt_received_at=trip.receipt_received_at,
            documents=[OrDocumentResponse.from_entity(one) for one in view.documents],
        )


class TripPageResponse(BaseModel):
    items: list[TripResponse]
    limit: int
    offset: int


class ResourceAvailabilityResponse(BaseModel):
    resource_id: UUID
    name: str
    can_receive_assignment: bool
    reason: str | None
    blocking_trip_id: UUID | None
    capacity_tons: Annotated[
        Decimal | None,
        PlainSerializer(lambda value: None if value is None else float(value), when_used="json"),
    ] = None

    @classmethod
    def from_entity(cls, resource: ResourceAvailability) -> "ResourceAvailabilityResponse":
        return cls(
            resource_id=resource.resource_id,
            name=resource.name,
            can_receive_assignment=resource.can_receive_assignment,
            reason=resource.reason,
            blocking_trip_id=resource.blocking_trip_id,
            capacity_tons=resource.capacity_tons,
        )


class DispatchResourcesResponse(BaseModel):
    trucks: list[ResourceAvailabilityResponse]
    drivers: list[ResourceAvailabilityResponse]
    helpers: list[ResourceAvailabilityResponse]

    @classmethod
    def from_entity(cls, resources: DispatchResources) -> "DispatchResourcesResponse":
        return cls(
            trucks=[ResourceAvailabilityResponse.from_entity(one) for one in resources.trucks],
            drivers=[ResourceAvailabilityResponse.from_entity(one) for one in resources.drivers],
            helpers=[ResourceAvailabilityResponse.from_entity(one) for one in resources.helpers],
        )
