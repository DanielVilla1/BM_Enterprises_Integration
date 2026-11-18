# ===== AI GENERATED: fleet_dto =====
# Purpose: Request / response shapes for trucks, maintenance and licenses
# Inputs: validated JSON bodies and entities
# Returns: strict Pydantic models (extra fields forbidden on input)
# Flow:
# 1. Capacity is Decimal metric tons serialized as a JSON number
# 2. License responses come in a full and a limited (validity only) form

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, StringConstraints

from ..Entity.fleet import LicenseSummary, LicenseValidity, MaintenanceRecord, Truck, TruckStatus
from .partial_update import PartialUpdateRequest

PlateText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=2, max_length=16, pattern=r"^[A-Za-z0-9 -]+$"),
]
DescriptionText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
ReasonText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=500)]
LicenseNumberText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=5, max_length=32, pattern=r"^[A-Za-z0-9-]+$")
]
CapacityTons = Annotated[
    Decimal,
    Field(gt=0, le=100, max_digits=6, decimal_places=3),
    PlainSerializer(float, return_type=float, when_used="json"),
]


class TruckCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plate_number: PlateText
    description: DescriptionText | None = None
    capacity_tons: CapacityTons


class TruckUpdateRequest(PartialUpdateRequest):
    required_fields = frozenset({"plate_number", "capacity_tons", "is_active"})

    plate_number: PlateText | None = None
    description: DescriptionText | None = None
    capacity_tons: CapacityTons | None = None
    is_active: bool | None = None


class MaintenanceStartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: ReasonText


class TruckResponse(BaseModel):
    truck_id: UUID
    plate_number: str
    description: str | None
    capacity_tons: Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]
    status: TruckStatus
    is_active: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, truck: Truck) -> "TruckResponse":
        return cls(
            truck_id=truck.truck_id,
            plate_number=truck.plate_number,
            description=truck.description,
            capacity_tons=truck.capacity_tons,
            status=truck.status,
            is_active=truck.is_active,
            created_at=truck.created_at,
        )


class TruckPageResponse(BaseModel):
    items: list[TruckResponse]
    limit: int
    offset: int


class MaintenanceRecordResponse(BaseModel):
    record_id: UUID
    truck_id: UUID
    reason: str
    started_at: datetime
    ended_at: datetime | None

    @classmethod
    def from_entity(cls, record: MaintenanceRecord) -> "MaintenanceRecordResponse":
        return cls(
            record_id=record.record_id,
            truck_id=record.truck_id,
            reason=record.reason,
            started_at=record.started_at,
            ended_at=record.ended_at,
        )


class DriverLicenseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    license_number: LicenseNumberText
    expiry_date: date


class DriverLicenseDetailResponse(BaseModel):
    employee_id: UUID
    license_number: str
    expiry_date: date
    validity: LicenseValidity

    @classmethod
    def from_summary(cls, summary: LicenseSummary) -> "DriverLicenseDetailResponse":
        return cls(
            employee_id=summary.license.employee_id,
            license_number=summary.license.license_number,
            expiry_date=summary.license.expiry_date,
            validity=summary.validity,
        )


class DriverLicenseLimitedResponse(BaseModel):
    """Validity status only: no license number and no expiry date."""

    employee_id: UUID
    validity: LicenseValidity

    @classmethod
    def from_summary(cls, summary: LicenseSummary) -> "DriverLicenseLimitedResponse":
        return cls(employee_id=summary.license.employee_id, validity=summary.validity)
