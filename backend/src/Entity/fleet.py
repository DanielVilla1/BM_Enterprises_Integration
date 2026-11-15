# ===== AI GENERATED: fleet_entities =====
# Purpose: Trucks, maintenance records and driver licenses
# Inputs: values mapped by repositories
# Returns: frozen dataclasses and enums
# Flow:
# 1. TruckStatus follows the proposal's truck statuses
# 2. License validity is derived from the expiry date, never stored

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

EXPIRING_SOON_DAYS = 30


class TruckStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    ASSIGNED = "ASSIGNED"
    IN_TRANSIT = "IN_TRANSIT"
    MAINTENANCE = "MAINTENANCE"


class LicenseValidity(StrEnum):
    VALID = "VALID"
    EXPIRING_SOON = "EXPIRING_SOON"
    EXPIRED = "EXPIRED"


def license_validity(expiry_date: date, today: date) -> LicenseValidity:
    """A license is valid through its expiry date; flag it 30 days ahead."""
    days_left = (expiry_date - today).days
    if days_left < 0:
        return LicenseValidity.EXPIRED
    if days_left <= EXPIRING_SOON_DAYS:
        return LicenseValidity.EXPIRING_SOON
    return LicenseValidity.VALID


@dataclass(frozen=True)
class Truck:
    truck_id: UUID
    plate_number: str
    description: str | None
    capacity_tons: Decimal
    status: TruckStatus
    is_active: bool
    created_at: datetime


@dataclass(frozen=True)
class MaintenanceRecord:
    record_id: UUID
    truck_id: UUID
    reason: str
    started_at: datetime
    ended_at: datetime | None
    started_by: UUID | None


@dataclass(frozen=True)
class DriverLicense:
    employee_id: UUID
    license_number: str
    expiry_date: date
    updated_at: datetime


@dataclass(frozen=True)
class LicenseSummary:
    license: DriverLicense
    validity: LicenseValidity
