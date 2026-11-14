# ===== AI GENERATED: account_controller =====
# Purpose: /me - the signed-in employee, roles and capability levels
# Inputs: bearer token
# Returns: MeResponse
# Flow:
# 1. get_principal authenticates (any active employee)
# 2. Authorization service lists capability levels for the roles

from fastapi import APIRouter, Depends

from ..DTO.account_dto import MeResponse
from ..Entity.employee import Principal
from ..providers import get_authorization_service, get_principal
from ..Service.authorization_service import AuthorizationService

router = APIRouter(prefix="/api/v1", tags=["account"])


@router.get("/me", response_model=MeResponse)
def read_current_account(
    principal: Principal = Depends(get_principal),
    authorization: AuthorizationService = Depends(get_authorization_service),
) -> MeResponse:
    return MeResponse(
        employee_id=principal.employee_id,
        full_name=principal.full_name,
        role_codes=list(principal.role_codes),
        capabilities=authorization.capability_levels(principal),
    )
