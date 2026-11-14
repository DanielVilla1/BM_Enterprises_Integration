# ===== AI GENERATED: ITripRepository =====
# Purpose: Port for trip, crew history and truck replacement persistence
# Inputs: domain values
# Returns: Trip entities and resource-trip facts
# Flow:
# 1. CRUD and status changes for trips; crew is retained as history
# 2. Queries that answer "which open trips hold this resource?"
# 3. lock_resources serializes concurrent assignments on PostgreSQL

from collections.abc import Iterable
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from ..Entity.dispatch import ResourceTrip, Trip, TripStatus, TruckReplacement


class ITripRepository(Protocol):
    def get_by_id(self, trip_id: UUID) -> Trip | None: ...

    def list_page(
        self,
        limit: int,
        offset: int,
        status: TripStatus | None,
        order_id: UUID | None,
        truck_id: UUID | None,
    ) -> list[Trip]: ...

    def list_assigned(
        self, employee_id: UUID, limit: int, offset: int, status: TripStatus | None
    ) -> list[Trip]: ...

    def list_for_order(self, order_id: UUID) -> list[Trip]: ...

    def create(
        self,
        order_id: UUID,
        truck_id: UUID,
        load_tons: Decimal,
        driver_id: UUID,
        helper_ids: tuple[UUID, ...],
        created_by: UUID | None,
    ) -> Trip: ...

    def replace_crew(self, trip_id: UUID, driver_id: UUID, helper_ids: tuple[UUID, ...]) -> Trip | None: ...

    def set_status(self, trip_id: UUID, status: TripStatus) -> Trip | None: ...

    def close(self, trip_id: UUID, status: TripStatus, reason: str) -> Trip | None: ...

    def set_truck(self, trip_id: UUID, truck_id: UUID) -> Trip | None: ...

    def record_replacement(
        self,
        trip_id: UUID,
        original_truck_id: UUID,
        replacement_truck_id: UUID,
        reason: str,
        replaced_by: UUID | None,
    ) -> TruckReplacement: ...

    def find_open_resource_trips(
        self, truck_id: UUID, employee_ids: Iterable[UUID], exclude_trip_id: UUID | None
    ) -> list[ResourceTrip]: ...

    def list_open_resource_trips(self) -> list[ResourceTrip]: ...

    def open_truck_statuses(self, truck_id: UUID) -> list[TripStatus]: ...

    def lock_resources(self, truck_ids: Iterable[UUID], employee_ids: Iterable[UUID]) -> None: ...
