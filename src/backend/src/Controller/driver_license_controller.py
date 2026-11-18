# ===== AI GENERATED: driver_license_controller =====
# Purpose: Driver license endpoints (driver_license.view capability)
# Inputs: validated DTOs, AccessContext
# Returns: full license (Full/View/Own) or validity only (Ltd)
# Flow:
# 1. Level decides the projection; the number never reaches Ltd callers
# 2. Only FULL (Owner, Fleet Manager) may save

from uuid import UUID

from fastapi import APIRouter, Depends

from ..DTO.account_dto import ProblemDetailsResponse
from ..DTO.fleet_dto import (
    DriverLicenseDetailResponse,
    DriverLicenseLimitedResponse,
    DriverLicenseRequest,
)
from ..Entity.access import AccessLevel
from ..providers import AccessContext, get_driver_license_service, get_trace_id, require_capability
from ..Service.driver_license_service import DriverLicenseService

CAPABILITY = "driver_license.view"

router = APIRouter(
    prefix="/api/v1/employees/{employee_id}/driver-license",
    tags=["driver-licenses"],
    responses={401: {"model": ProblemDetailsResponse}, 403: {"model": ProblemDetailsResponse}},
)


@router.get("", response_model=DriverLicenseDetailResponse | DriverLicenseLimitedResponse)
def read_driver_license(
    employee_id: UUID,
    access: AccessContext = Depends(require_capability(CAPABILITY)),
    service: DriverLicenseService = Depends(get_driver_license_service),
) -> DriverLicenseDetailResponse | DriverLicenseLimitedResponse:
    summary = service.get_license(access.principal, access.level, employee_id)
    if access.level is AccessLevel.LTD:
        return DriverLicenseLimitedResponse.from_summary(summary)
    return DriverLicenseDetailResponse.from_summary(summary)


@router.put("", response_model=DriverLicenseDetailResponse)
def save_driver_license(
    employee_id: UUID,
    payload: DriverLicenseRequest,
    access: AccessContext = Depends(require_capability(CAPABILITY, AccessLevel.FULL)),
    service: DriverLicenseService = Depends(get_driver_license_service),
    trace_id: str = Depends(get_trace_id),
) -> DriverLicenseDetailResponse:
    summary = service.save_license(
        access.principal, access.level, employee_id, payload.license_number, payload.expiry_date, trace_id
    )
    return DriverLicenseDetailResponse.from_summary(summary)
