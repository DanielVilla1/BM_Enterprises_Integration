# ===== AI GENERATED: orm_models =====
# Purpose: SQLAlchemy table models for Sprint 1 persistence
# Inputs: Base from database.py
# Returns: table classes used only by repositories
# Flow:
# 1. Define roles, employees, role assignments
# 2. Define permission matrix, audit log, webhook ledger
# 3. Keep all constraints mirrored by the Alembic migration

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, String, Text, Uuid, func
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
