# ===== AI GENERATED: employee_entities =====
# Purpose: Persistence-agnostic employee, principal and audit records
# Inputs: values mapped by repositories
# Returns: frozen dataclasses used inside services
# Flow:
# 1. Employee: person record linked to one Clerk user
# 2. Principal: authenticated employee with roles
# 3. AuditRecord / PermissionGrant: supporting domain values

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from .access import AccessLevel, RoleCode


@dataclass(frozen=True)
class Employee:
    """A person employed by BM Enterprises (spec 3.2)."""

    employee_id: UUID
    full_name: str
    email: str
    phone: str | None
    clerk_user_id: str | None
    is_active: bool
    role_codes: tuple[RoleCode, ...]
    created_at: datetime


@dataclass(frozen=True)
class Principal:
    """The signed-in, active employee making a request."""

    employee_id: UUID
    clerk_user_id: str
    full_name: str
    role_codes: tuple[RoleCode, ...]


@dataclass(frozen=True)
class EmployeeDirectoryEntry:
    employee_id: UUID
    full_name: str


@dataclass(frozen=True)
class AuditRecord:
    """One immutable audit entry."""

    audit_id: UUID
    occurred_at: datetime
    actor_employee_id: UUID | None
    action: str
    entity_type: str
    entity_id: str | None
    details: dict[str, object] = field(default_factory=dict)
    trace_id: str | None = None


@dataclass(frozen=True)
class PermissionGrant:
    """One cell of the permission matrix."""

    capability: str
    role_code: RoleCode
    access_level: AccessLevel
    conditional_setting: str | None
