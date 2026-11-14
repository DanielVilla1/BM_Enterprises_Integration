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
