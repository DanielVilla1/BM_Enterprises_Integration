# ===== AI GENERATED: orm_models =====
# Purpose: SQLAlchemy table models for Sprint 1 persistence
# Inputs: Base from database.py
# Returns: table classes used only by repositories
# Flow:
# 1. Define roles, employees, role assignments
# 2. Define permission matrix, audit log, webhook ledger
# 3. Keep all constraints mirrored by the Alembic migration

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    Uuid,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


def utc_now() -> datetime:
    """Current time in UTC (spec: ISO 8601, UTC)."""
    return datetime.now(UTC)


class RoleRow(Base):
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)


class EmployeeRow(Base):
    __tablename__ = "employees"

    employee_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    clerk_user_id: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, server_default=func.now()
    )


Index("uq_employees_email_lower", func.lower(EmployeeRow.email), unique=True)


class EmployeeRoleRow(Base):
    __tablename__ = "employee_roles"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("employees.employee_id"), primary_key=True
    )
    role_code: Mapped[str] = mapped_column(String(32), ForeignKey("roles.code"), primary_key=True)
    assigned_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("employees.employee_id"), nullable=True
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, server_default=func.now()
    )
    exception_reason: Mapped[str | None] = mapped_column(Text, nullable=True)


class RolePermissionRow(Base):
    __tablename__ = "role_permissions"

    capability: Mapped[str] = mapped_column(String(64), primary_key=True)
    role_code: Mapped[str] = mapped_column(String(32), ForeignKey("roles.code"), primary_key=True)
    access_level: Mapped[str] = mapped_column(String(8), nullable=False)
    conditional_setting: Mapped[str | None] = mapped_column(String(64), nullable=True)


class AuditLogRow(Base):
    __tablename__ = "audit_log"

    audit_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, server_default=func.now()
    )
    actor_employee_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("employees.employee_id"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)


class ProcessedWebhookRow(Base):
    __tablename__ = "processed_webhook_events"

    event_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, server_default=func.now()
    )


class ClientRow(Base):
    __tablename__ = "clients"

    client_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    contact_person: Mapped[str | None] = mapped_column(String(120), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, server_default=func.now()
    )


Index("uq_clients_name_lower", func.lower(ClientRow.name), unique=True)


class TruckRow(Base):
    __tablename__ = "trucks"
    __table_args__ = (
        CheckConstraint("capacity_tons > 0", name="ck_trucks_capacity_positive"),
        CheckConstraint(
            "status IN ('AVAILABLE', 'ASSIGNED', 'IN_TRANSIT', 'MAINTENANCE')", name="ck_trucks_status"
        ),
    )

    truck_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    plate_number: Mapped[str] = mapped_column(String(16), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(120), nullable=True)
    capacity_tons: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="AVAILABLE")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, server_default=func.now()
    )


class MaintenanceRecordRow(Base):
    __tablename__ = "truck_maintenance_records"

    record_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    truck_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("trucks.truck_id"), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, server_default=func.now()
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    started_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("employees.employee_id"), nullable=True
    )


class DriverLicenseRow(Base):
    __tablename__ = "driver_licenses"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("employees.employee_id"), primary_key=True
    )
    license_number: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, server_default=func.now()
    )


class DeliveryOrderRow(Base):
    __tablename__ = "delivery_orders"
    __table_args__ = (
        CheckConstraint("total_weight_tons > 0", name="ck_delivery_orders_weight_positive"),
        CheckConstraint(
            "status IN ('PENDING', 'PARTIALLY_ASSIGNED', 'SCHEDULED', 'IN_PROGRESS', "
            "'COMPLETED', 'CANCELLED')",
            name="ck_delivery_orders_status",
        ),
        Index("ix_delivery_orders_status_date", "status", "scheduled_date"),
    )

    order_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("clients.client_id"), nullable=False)
    client_reference: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pickup_location: Mapped[str] = mapped_column(String(300), nullable=False)
    delivery_location: Mapped[str] = mapped_column(String(300), nullable=False)
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_weight_tons: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="PENDING")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("employees.employee_id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, server_default=func.now()
    )


class TripRow(Base):
    __tablename__ = "trips"
    __table_args__ = (
        CheckConstraint("load_tons > 0", name="ck_trips_load_positive"),
        CheckConstraint(
            "status IN ('SCHEDULED', 'ACCEPTED', 'CLEARED_FOR_DISPATCH', 'IN_TRANSIT', "
            "'DELIVERED_OR_PENDING', 'OR_UPLOADED', 'COMPLETED', 'FAILED', 'CANCELLED')",
            name="ck_trips_status",
        ),
        Index("ix_trips_order", "order_id"),
        Index("ix_trips_truck_status", "truck_id", "status"),
        Index("ix_trips_status", "status"),
    )

    trip_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("delivery_orders.order_id"), nullable=False)
    truck_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("trucks.truck_id"), nullable=False)
    load_tons: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="SCHEDULED")
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cleared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    departed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("employees.employee_id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, server_default=func.now()
    )


class TripCrewRow(Base):
    __tablename__ = "trip_crew"
    __table_args__ = (
        CheckConstraint("crew_role IN ('DRIVER', 'HELPER')", name="ck_trip_crew_role"),
        Index("ix_trip_crew_employee", "employee_id"),
        Index("ix_trip_crew_trip", "trip_id"),
        Index(
            "uq_trip_crew_one_active_driver",
            "trip_id",
            unique=True,
            postgresql_where=text("crew_role = 'DRIVER' AND removed_at IS NULL"),
            sqlite_where=text("crew_role = 'DRIVER' AND removed_at IS NULL"),
        ),
        Index(
            "uq_trip_crew_active_member",
            "trip_id",
            "employee_id",
            unique=True,
            postgresql_where=text("removed_at IS NULL"),
            sqlite_where=text("removed_at IS NULL"),
        ),
    )

    crew_entry_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("trips.trip_id"), nullable=False)
    employee_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("employees.employee_id"), nullable=False)
    crew_role: Mapped[str] = mapped_column(String(8), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, server_default=func.now()
    )
    removed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TruckReplacementRow(Base):
    __tablename__ = "truck_replacements"

    replacement_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    trip_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("trips.trip_id"), nullable=False)
    original_truck_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("trucks.truck_id"), nullable=False)
    replacement_truck_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("trucks.truck_id"), nullable=False
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    effective_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, server_default=func.now()
    )
    replaced_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("employees.employee_id"), nullable=True
    )
