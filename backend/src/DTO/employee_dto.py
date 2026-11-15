# ===== AI GENERATED: employee_dto =====
# Purpose: Request / response shapes for employee endpoints
# Inputs: validated JSON bodies and Employee entities
# Returns: strict Pydantic models (extra fields forbidden on input)
# Flow:
# 1. Requests: create, update, identity link, role assignment
# 2. Responses: detail, limited, page; fields listed explicitly (API3)

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from ..Entity.access import RoleCode
from ..Entity.employee import Employee

_EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

FullNameText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
EmailText = Annotated[str, StringConstraints(strip_whitespace=True, max_length=254, pattern=_EMAIL_PATTERN)]
PhoneText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=32)]


class EmployeeCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: FullNameText
    email: EmailText
    phone: PhoneText | None = None


class EmployeeUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: FullNameText | None = None
    email: EmailText | None = None
    phone: PhoneText | None = None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> "EmployeeUpdateRequest":
        if self.full_name is None and self.email is None and self.phone is None:
            raise ValueError("at least one field must be provided")
        return self


class IdentityLinkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    clerk_user_id: Annotated[str, StringConstraints(min_length=5, max_length=64, pattern=r"^[A-Za-z0-9_]+$")]


class RoleAssignmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role_codes: list[RoleCode] = Field(max_length=7)
    exception_reason: (
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=500)] | None
    ) = None


class EmployeeLimitedResponse(BaseModel):
    """Minimum fields for the 'Ltd' matrix level."""

    employee_id: UUID
    full_name: str
    is_active: bool

    @classmethod
    def from_entity(cls, employee: Employee) -> "EmployeeLimitedResponse":
        return cls(
            employee_id=employee.employee_id,
            full_name=employee.full_name,
            is_active=employee.is_active,
        )


class EmployeeDetailResponse(BaseModel):
    employee_id: UUID
    full_name: str
    email: str
    phone: str | None
    is_active: bool
    has_account: bool
    role_codes: list[RoleCode]
    created_at: datetime

    @classmethod
    def from_entity(cls, employee: Employee) -> "EmployeeDetailResponse":
        return cls(
            employee_id=employee.employee_id,
            full_name=employee.full_name,
            email=employee.email,
            phone=employee.phone,
            is_active=employee.is_active,
            has_account=employee.clerk_user_id is not None,
            role_codes=list(employee.role_codes),
            created_at=employee.created_at,
        )


class EmployeePageResponse(BaseModel):
    items: list[EmployeeDetailResponse | EmployeeLimitedResponse]
    limit: int
    offset: int
