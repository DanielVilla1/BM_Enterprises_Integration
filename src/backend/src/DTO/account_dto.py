# ===== AI GENERATED: account_dto =====
# Purpose: Response shapes for /me, health, permissions, audit and webhooks
# Inputs: entities from services
# Returns: explicit Pydantic response models
# Flow:
# 1. MeResponse carries roles and capability levels for the UI
# 2. Matrix and audit pages for the Owner
# 3. Problem details model documents the error contract

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from ..Entity.access import AccessLevel, RoleCode
from ..Entity.employee import AuditRecord, PermissionGrant


class HealthResponse(BaseModel):
    status: Literal["ok"]


class MeResponse(BaseModel):
    employee_id: UUID
    full_name: str
    role_codes: list[RoleCode]
    capabilities: dict[str, AccessLevel]


class PermissionGrantResponse(BaseModel):
    capability: str
    role_code: RoleCode
    access_level: AccessLevel
    conditional_setting: str | None

    @classmethod
    def from_entity(cls, grant: PermissionGrant) -> "PermissionGrantResponse":
        return cls(
            capability=grant.capability,
            role_code=grant.role_code,
            access_level=grant.access_level,
            conditional_setting=grant.conditional_setting,
        )


class PermissionMatrixResponse(BaseModel):
    grants: list[PermissionGrantResponse]


class AuditRecordResponse(BaseModel):
    audit_id: UUID
    occurred_at: datetime
    actor_employee_id: UUID | None
    action: str
    entity_type: str
    entity_id: str | None
    details: dict[str, object]
    trace_id: str | None

    @classmethod
    def from_entity(cls, record: AuditRecord) -> "AuditRecordResponse":
        return cls(
            audit_id=record.audit_id,
            occurred_at=record.occurred_at,
            actor_employee_id=record.actor_employee_id,
            action=record.action,
            entity_type=record.entity_type,
            entity_id=record.entity_id,
            details=record.details,
            trace_id=record.trace_id,
        )


class AuditPageResponse(BaseModel):
    items: list[AuditRecordResponse]
    limit: int
    offset: int


class WebhookAckResponse(BaseModel):
    status: Literal["processed", "duplicate", "ignored"]


class FieldErrorResponse(BaseModel):
    field: str
    message: str


class AccountSetupResponse(BaseModel):
    """Diagnostics for the caller's own verified identity, without employee privileges."""

    reason: Literal["identity_not_linked", "employee_inactive"]
    clerk_user_id: str


class ProblemDetailsResponse(BaseModel):
    """RFC 9457 body returned for every error (application/problem+json)."""

    type: str
    title: str
    status: int
    detail: str
    code: str
    trace_id: str
    errors: list[FieldErrorResponse] | None = None
    blocking_trip_ids: list[str] | None = None
    account_setup: AccountSetupResponse | None = None
