# ===== AI GENERATED: health_controller =====
# Purpose: Public liveness endpoint
# Inputs: none
# Returns: HealthResponse
# Flow:
# 1. Respond ok without touching the database or any secret

from fastapi import APIRouter

from ..DTO.account_dto import HealthResponse

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
def read_health() -> HealthResponse:
    return HealthResponse(status="ok")
