# ===== AI GENERATED: fleet_repository_contracts =====
# Purpose: Ports for truck and driver license persistence
# Inputs: domain values
# Returns: fleet entities
# Flow:
# 1. ITruckRepository: CRUD, status, maintenance records
# 2. IDriverLicenseRepository: read and upsert per employee

from collections.abc import Mapping
from datetime import date
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from ..Entity.fleet import DriverLicense, MaintenanceRecord, Truck, TruckStatus


class ITruckRepository(Protocol):
    def get_by_id(self, truck_id: UUID) -> Truck | None: ...

    def get_by_plate(self, plate_number: str) -> Truck | None: ...

    def list_page(
        self, limit: int, offset: int, status: TruckStatus | None, only_active: bool | None
    ) -> list[Truck]: ...

    def create(self, plate_number: str, description: str | None, capacity_tons: Decimal) -> Truck: ...

    def update(self, truck_id: UUID, changes: Mapping[str, object]) -> Truck | None: ...

    def set_status(self, truck_id: UUID, status: TruckStatus) -> Truck | None: ...

    def open_maintenance(self, truck_id: UUID, reason: str, started_by: UUID | None) -> MaintenanceRecord: ...

    def close_maintenance(self, truck_id: UUID) -> MaintenanceRecord | None: ...

    def list_maintenance(self, truck_id: UUID) -> list[MaintenanceRecord]: ...


class IDriverLicenseRepository(Protocol):
    def get_by_employee(self, employee_id: UUID) -> DriverLicense | None: ...

    def get_by_number(self, license_number: str) -> DriverLicense | None: ...

    def upsert(self, employee_id: UUID, license_number: str, expiry_date: date) -> DriverLicense: ...
