# ===== AI GENERATED: dispatch_entities =====
# Purpose: Trips, crew and the dispatch availability rules (spec 4, 5)
# Inputs: values mapped by repositories
# Returns: frozen dataclasses, status sets, order/truck status derivation
# Flow:
# 1. Trip statuses follow spec 4.2
# 2. PRE_UPLOAD trips block a resource from the next assignment; any open trip blocks departure
# 3. Order and truck statuses are derived from trips, never set by hand

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from .documents import OrDocument
from .fleet import TruckStatus
from .operations import OrderStatus


class TripStatus(StrEnum):
    SCHEDULED = "SCHEDULED"
    ACCEPTED = "ACCEPTED"
    CLEARED_FOR_DISPATCH = "CLEARED_FOR_DISPATCH"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED_OR_PENDING = "DELIVERED_OR_PENDING"
    OR_UPLOADED = "OR_UPLOADED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ResourceKind(StrEnum):
    TRUCK = "TRUCK"
    DRIVER = "DRIVER"
    HELPER = "HELPER"


PRE_DEPARTURE_STATUSES = frozenset(
    {TripStatus.SCHEDULED, TripStatus.ACCEPTED, TripStatus.CLEARED_FOR_DISPATCH}
)
PRE_UPLOAD_STATUSES = PRE_DEPARTURE_STATUSES | {TripStatus.IN_TRANSIT, TripStatus.DELIVERED_OR_PENDING}
OPEN_STATUSES = PRE_UPLOAD_STATUSES | {TripStatus.OR_UPLOADED}
DEPARTED_STATUSES = frozenset(
    {
        TripStatus.IN_TRANSIT,
        TripStatus.DELIVERED_OR_PENDING,
        TripStatus.OR_UPLOADED,
        TripStatus.COMPLETED,
    }
)
INACTIVE_LOAD_STATUSES = frozenset({TripStatus.CANCELLED, TripStatus.FAILED})
REPLACEABLE_TRUCK_STATUSES = PRE_DEPARTURE_STATUSES | {TripStatus.IN_TRANSIT}

MINIMUM_HELPERS = 1
MAXIMUM_HELPERS = 2


@dataclass(frozen=True)
class Trip:
    trip_id: UUID
    order_id: UUID
    truck_id: UUID
    load_tons: Decimal
    status: TripStatus
    driver_id: UUID
    helper_ids: tuple[UUID, ...]
    accepted_at: datetime | None
    cleared_at: datetime | None
    departed_at: datetime | None
    delivered_at: datetime | None
    closed_reason: str | None
    created_by: UUID | None
    created_at: datetime
    or_uploaded_at: datetime | None = None
    or_uploaded_by: UUID | None = None
    receipt_confirmed_at: datetime | None = None
    receipt_confirmed_by: UUID | None = None
    receipt_received_at: datetime | None = None


@dataclass(frozen=True)
class ResourceTrip:
    """A resource (truck or crew member) tied to one open trip."""

    trip_id: UUID
    status: TripStatus
    kind: ResourceKind
    resource_id: UUID


@dataclass(frozen=True)
class TripView:
    """A trip with the order details a crew member needs."""

    trip: Trip
    scheduled_date: date
    pickup_location: str
    delivery_location: str
    documents: tuple[OrDocument, ...] = ()


@dataclass(frozen=True)
class TruckReplacement:
    replacement_id: UUID
    trip_id: UUID
    original_truck_id: UUID
    replacement_truck_id: UUID
    reason: str
    effective_at: datetime
    replaced_by: UUID | None


def assigned_load(trips: list[Trip]) -> Decimal:
    """Load still counted against the order: cancelled and failed trips free their share."""
    return sum((one.load_tons for one in trips if one.status not in INACTIVE_LOAD_STATUSES), Decimal(0))


def derive_order_status(total_weight: Decimal, trips: list[Trip]) -> OrderStatus:
    active = [one for one in trips if one.status not in INACTIVE_LOAD_STATUSES]
    assigned = assigned_load(trips)
    if active and assigned >= total_weight and all(one.status is TripStatus.COMPLETED for one in active):
        return OrderStatus.COMPLETED
    if any(one.status in DEPARTED_STATUSES for one in active):
        return OrderStatus.IN_PROGRESS
    if assigned >= total_weight:
        return OrderStatus.SCHEDULED
    if assigned > 0:
        return OrderStatus.PARTIALLY_ASSIGNED
    return OrderStatus.PENDING


def derive_truck_status(open_statuses: list[TripStatus]) -> TruckStatus:
    """Operational status of a truck that is not in maintenance."""
    if TripStatus.IN_TRANSIT in open_statuses:
        return TruckStatus.IN_TRANSIT
    if open_statuses:
        return TruckStatus.ASSIGNED
    return TruckStatus.AVAILABLE


def blocking_trips(resource_trips: list[ResourceTrip], statuses: frozenset[TripStatus]) -> list[ResourceTrip]:
    """Open trips of the resources whose status is in `statuses`, one per trip id."""
    seen: set[UUID] = set()
    blockers: list[ResourceTrip] = []
    for resource_trip in resource_trips:
        if resource_trip.status in statuses and resource_trip.trip_id not in seen:
            seen.add(resource_trip.trip_id)
            blockers.append(resource_trip)
    return blockers


@dataclass(frozen=True)
class ResourceAvailability:
    """Whether a truck or crew member can take a new assignment, and why not."""

    resource_id: UUID
    name: str
    can_receive_assignment: bool
    reason: str | None
    blocking_trip_id: UUID | None
    capacity_tons: Decimal | None = None


@dataclass(frozen=True)
class DispatchResources:
    trucks: list[ResourceAvailability]
    drivers: list[ResourceAvailability]
    helpers: list[ResourceAvailability]
