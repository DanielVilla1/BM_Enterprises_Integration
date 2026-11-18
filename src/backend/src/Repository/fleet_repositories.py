# ===== AI GENERATED: fleet_repositories =====
# Purpose: SQLAlchemy implementations for trucks, maintenance and licenses
# Inputs: Session
# Returns: fleet entities (never ORM rows)
# Flow:
# 1. Query rows, map to entities
# 2. Updates only touch whitelisted columns
# 3. Flush writes; services commit

from collections.abc import Mapping
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..Entity.fleet import DriverLicense, MaintenanceRecord, Truck, TruckStatus
from .orm_models import DriverLicenseRow, MaintenanceRecordRow, TruckRow, utc_now

_TRUCK_FIELDS = {"plate_number", "description", "capacity_tons", "is_active"}


def _truck(row: TruckRow) -> Truck:
    return Truck(
        truck_id=row.truck_id,
        plate_number=row.plate_number,
        description=row.description,
        capacity_tons=Decimal(row.capacity_tons),
        status=TruckStatus(row.status),
        is_active=row.is_active,
        created_at=row.created_at,
    )


def _maintenance(row: MaintenanceRecordRow) -> MaintenanceRecord:
    return MaintenanceRecord(
        record_id=row.record_id,
        truck_id=row.truck_id,
        reason=row.reason,
        started_at=row.started_at,
        ended_at=row.ended_at,
        started_by=row.started_by,
    )


class TruckRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, truck_id: UUID) -> Truck | None:
        row = self._session.get(TruckRow, truck_id)
        return _truck(row) if row is not None else None

    def get_by_plate(self, plate_number: str) -> Truck | None:
        statement = select(TruckRow).where(func.upper(TruckRow.plate_number) == plate_number.upper())
        row = self._session.scalars(statement).first()
        return _truck(row) if row is not None else None

    def list_page(
        self, limit: int, offset: int, status: TruckStatus | None, only_active: bool | None
    ) -> list[Truck]:
        statement = select(TruckRow).order_by(TruckRow.plate_number)
        if status is not None:
            statement = statement.where(TruckRow.status == status.value)
        if only_active is not None:
            statement = statement.where(TruckRow.is_active == only_active)
        rows = self._session.scalars(statement.limit(limit).offset(offset)).all()
        return [_truck(row) for row in rows]

    def create(self, plate_number: str, description: str | None, capacity_tons: Decimal) -> Truck:
        row = TruckRow(
            plate_number=plate_number,
            description=description,
            capacity_tons=capacity_tons,
            status=TruckStatus.AVAILABLE.value,
            is_active=True,
        )
        self._session.add(row)
        self._session.flush()
        self._session.refresh(row)
        return _truck(row)

    def update(self, truck_id: UUID, changes: Mapping[str, object]) -> Truck | None:
        row = self._session.get(TruckRow, truck_id)
        if row is None:
            return None
        for field_name, value in changes.items():
            if field_name in _TRUCK_FIELDS:
                setattr(row, field_name, value)
        self._session.flush()
        self._session.refresh(row)
        return _truck(row)

    def set_status(self, truck_id: UUID, status: TruckStatus) -> Truck | None:
        row = self._session.get(TruckRow, truck_id)
        if row is None:
            return None
        row.status = status.value
        self._session.flush()
        return _truck(row)

    def open_maintenance(self, truck_id: UUID, reason: str, started_by: UUID | None) -> MaintenanceRecord:
        row = MaintenanceRecordRow(truck_id=truck_id, reason=reason, started_by=started_by)
        self._session.add(row)
        self._session.flush()
        self._session.refresh(row)
        return _maintenance(row)

    def close_maintenance(self, truck_id: UUID) -> MaintenanceRecord | None:
        statement = select(MaintenanceRecordRow).where(
            MaintenanceRecordRow.truck_id == truck_id, MaintenanceRecordRow.ended_at.is_(None)
        )
        row = self._session.scalars(statement).first()
        if row is None:
            return None
        row.ended_at = utc_now()
        self._session.flush()
        return _maintenance(row)

    def list_maintenance_for_trucks(self, truck_ids: list[UUID]) -> list[MaintenanceRecord]:
        if not truck_ids:
            return []
        statement = select(MaintenanceRecordRow).where(MaintenanceRecordRow.truck_id.in_(truck_ids))
        return [_maintenance(row) for row in self._session.scalars(statement)]

    def list_maintenance(self, truck_id: UUID) -> list[MaintenanceRecord]:
        statement = (
            select(MaintenanceRecordRow)
            .where(MaintenanceRecordRow.truck_id == truck_id)
            .order_by(MaintenanceRecordRow.started_at.desc(), MaintenanceRecordRow.record_id)
        )
        return [_maintenance(row) for row in self._session.scalars(statement).all()]


class DriverLicenseRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    @staticmethod
    def _to_entity(row: DriverLicenseRow) -> DriverLicense:
        return DriverLicense(
            employee_id=row.employee_id,
            license_number=row.license_number,
            expiry_date=row.expiry_date,
            updated_at=row.updated_at,
        )

    def get_by_employee(self, employee_id: UUID) -> DriverLicense | None:
        row = self._session.get(DriverLicenseRow, employee_id)
        return self._to_entity(row) if row is not None else None

    def get_by_number(self, license_number: str) -> DriverLicense | None:
        statement = select(DriverLicenseRow).where(DriverLicenseRow.license_number == license_number)
        row = self._session.scalars(statement).first()
        return self._to_entity(row) if row is not None else None

    def upsert(self, employee_id: UUID, license_number: str, expiry_date: date) -> DriverLicense:
        row = self._session.get(DriverLicenseRow, employee_id)
        if row is None:
            row = DriverLicenseRow(
                employee_id=employee_id, license_number=license_number, expiry_date=expiry_date
            )
            self._session.add(row)
        else:
            row.license_number = license_number
            row.expiry_date = expiry_date
            row.updated_at = utc_now()
        self._session.flush()
        self._session.refresh(row)
        return self._to_entity(row)
