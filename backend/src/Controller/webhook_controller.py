# ===== AI GENERATED: webhook_controller =====
# Purpose: Public Clerk webhook receiver (authenticated by signature only)
# Inputs: raw request body and svix-* headers
# Returns: WebhookAckResponse; 400 on bad signature
# Flow:
# 1. Cap the body size, read raw bytes
# 2. Hand bytes + headers to the service (verifies before any effect)
# 3. Run the blocking service call off the event loop

from fastapi import APIRouter, Depends, Request
from fastapi.concurrency import run_in_threadpool

from ..config import get_settings
from ..DTO.account_dto import ProblemDetailsResponse, WebhookAckResponse
from ..Entity.business_rule_error import BusinessRuleError
from ..providers import get_webhook_service
from ..Service.clerk_webhook_service import ClerkWebhookService

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


@router.post(
    "/clerk",
    response_model=WebhookAckResponse,
    responses={400: {"model": ProblemDetailsResponse}},
)
async def receive_clerk_webhook(
    request: Request, service: ClerkWebhookService = Depends(get_webhook_service)
) -> WebhookAckResponse:
    maximum_bytes = get_settings().max_webhook_body_bytes
    declared_length = request.headers.get("content-length")
    if declared_length is not None and declared_length.isdigit() and int(declared_length) > maximum_bytes:
        raise BusinessRuleError(413, "PAYLOAD_TOO_LARGE", "Payload too large", "Body is too large.")
    raw_body = await request.body()
    if len(raw_body) > maximum_bytes:
        raise BusinessRuleError(413, "PAYLOAD_TOO_LARGE", "Payload too large", "Body is too large.")
    outcome = await run_in_threadpool(service.process, raw_body, dict(request.headers))
    return WebhookAckResponse(status=outcome)  # type: ignore[arg-type]
