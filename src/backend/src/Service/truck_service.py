# ===== AI GENERATED: TruckService =====
# Purpose: Truck records, capacity and maintenance status
# Inputs: truck repository, audit, unit of work
# Returns: Truck / MaintenanceRecord entities or BusinessRuleError
# Flow:
# 1. Normalize plates; enforce uniqueness
# 2. Maintenance only starts from AVAILABLE; busy trucks cannot be retired
# 3. Audit every change, commit once

from collections.abc import Mapping
from decimal import Decimal
from uuid import UUID

from ..Contract.i_audit_repository import IAuditRepository
from ..Contract.i_fleet_repositories import ITruckRepository
from ..Contract.i_unit_of_work import IUnitOfWork
from ..Entity.business_rule_error import BusinessRuleError
from ..Entity.employee import Principal
from ..Entity.fleet import MaintenanceRecord, Truck, TruckStatus

BUSY_STATUSES = (TruckStatus.ASSIGNED, TruckStatus.IN_TRANSIT)


def normalize_plate(plate_number: str) -> str:
    """Plates are stored upper-case without surrounding or repeated spaces."""
    return " ".join(plate_number.upper().split())


def _not_found() -> BusinessRuleError:
    return BusinessRuleError(404, "TRUCK_NOT_FOUND", "Not found", "The truck was not found.")


def _busy() -> BusinessRuleError:
    return BusinessRuleError(
        409, "TRUCK_BUSY", "Conflict", "The truck is assigned or on a trip and cannot be changed this way."
    )


class TruckService:
    def __init__(self, trucks: ITruckRepository, audit: IAuditRepository, unit_of_work: IUnitOfWork) -> None:
        self._trucks = trucks
        self._audit = audit
        self._unit_of_work = unit_of_work

    def list_trucks(
        self, limit: int, offset: int, status: TruckStatus | None, only_active: bool | None
    ) -> list[Truck]:
        return self._trucks.list_page(limit, offset, status, only_active)

    def get_truck(self, truck_id: UUID) -> Truck:
        truck = self._trucks.get_by_id(truck_id)
        if truck is None:
            raise _not_found()
        return truck

    def create_truck(
        self,
        principal: Principal,
        plate_number: str,
        description: str | None,
        capacity_tons: Decimal,
        trace_id: str | None,
    ) -> Truck:
        plate = normalize_plate(plate_number)
        self._ensure_plate_free(plate, owner_id=None)
        truck = self._trucks.create(plate, description, capacity_tons)
        self._record(principal, "truck.created", truck.truck_id, {}, trace_id)
        self._unit_of_work.commit()
        return truck

    def update_truck(
        self, principal: Principal, truck_id: UUID, changes: Mapping[str, object], trace_id: str | None
    ) -> Truck:
        existing = self.get_truck(truck_id)
        applied = dict(changes)
        if isinstance(applied.get("plate_number"), str):
            applied["plate_number"] = normalize_plate(str(applied["plate_number"]))
            self._ensure_plate_free(str(applied["plate_number"]), owner_id=truck_id)
        if applied.get("is_active") is False and existing.status in BUSY_STATUSES:
            raise _busy()
        updated = self._trucks.update(truck_id, applied)
        if updated is None:
            raise _not_found()
        self._record(principal, "truck.updated", truck_id, {"fields": sorted(applied)}, trace_id)
        self._unit_of_work.commit()
        return updated

    def start_maintenance(
        self, principal: Principal, truck_id: UUID, reason: str, trace_id: str | None
    ) -> MaintenanceRecord:
        truck = self.get_truck(truck_id)
        if truck.status in BUSY_STATUSES:
            raise _busy()
        if truck.status is TruckStatus.MAINTENANCE:
            raise BusinessRuleError(
                409, "ALREADY_IN_MAINTENANCE", "Conflict", "The truck is already in maintenance."
            )
        record = self._trucks.open_maintenance(truck_id, reason, principal.employee_id)
        self._trucks.set_status(truck_id, TruckStatus.MAINTENANCE)
        self._record(principal, "truck.maintenance_started", truck_id, {}, trace_id)
        self._unit_of_work.commit()
        return record

    def complete_maintenance(
        self, principal: Principal, truck_id: UUID, trace_id: str | None
    ) -> MaintenanceRecord:
        truck = self.get_truck(truck_id)
        if truck.status is not TruckStatus.MAINTENANCE:
            raise BusinessRuleError(409, "NOT_IN_MAINTENANCE", "Conflict", "The truck is not in maintenance.")
        record = self._trucks.close_maintenance(truck_id)
        if record is None:
            raise BusinessRuleError(
                409, "NOT_IN_MAINTENANCE", "Conflict", "The truck has no open maintenance record."
            )
        self._trucks.set_status(truck_id, TruckStatus.AVAILABLE)
        self._record(principal, "truck.maintenance_completed", truck_id, {}, trace_id)
        self._unit_of_work.commit()
        return record

    def list_maintenance(self, truck_id: UUID) -> list[MaintenanceRecord]:
        self.get_truck(truck_id)
        return self._trucks.list_maintenance(truck_id)

    def _ensure_plate_free(self, plate: str, owner_id: UUID | None) -> None:
        holder = self._trucks.get_by_plate(plate)
        if holder is not None and holder.truck_id != owner_id:
            raise BusinessRuleError(
                409, "PLATE_ALREADY_EXISTS", "Conflict", "A truck with that plate number already exists."
            )

    def _record(
        self,
        principal: Principal,
        action: str,
        truck_id: UUID,
        details: dict[str, object],
        trace_id: str | None,
    ) -> None:
        self._audit.append(principal.employee_id, action, "truck", str(truck_id), details, trace_id)
