# ===== AI GENERATED: main_app =====
# Purpose: Create the BM Enterprises FastAPI application
# Inputs: application settings
# Returns: `app` (ASGI) serving /api/v1
# Flow:
# 1. Docs/OpenAPI only when enabled (decision D-docs per spec section 11)
# 2. Explicit CORS origins; problem+json handlers; routers

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .src.config import get_settings
from .src.Controller.account_controller import router as account_router
from .src.Controller.administration_controller import router as administration_router
from .src.Controller.client_controller import router as client_router
from .src.Controller.delivery_order_controller import router as delivery_order_router
from .src.Controller.driver_license_controller import router as driver_license_router
from .src.Controller.employee_controller import router as employee_router
from .src.Controller.finance_controller import router as finance_router
from .src.Controller.health_controller import router as health_router
from .src.Controller.or_controller import router as or_router
from .src.Controller.trip_controller import router as trip_router
from .src.Controller.truck_controller import router as truck_router
from .src.Controller.webhook_controller import router as webhook_router
from .src.DTO.account_dto import ProblemDetailsResponse
from .src.openapi_contract import install_openapi_contract
from .src.problem_details import install_problem_details
from .src.request_limits import BodySizeLimitMiddleware
from .src.response_security import ResponseSecurityMiddleware

REQUEST_OVERHEAD_BYTES = 1024 * 1024


def create_application() -> FastAPI:
    settings = get_settings()
    docs_enabled = settings.enable_api_docs
    application = FastAPI(
        title="BM Enterprises Hauling API",
        version="1.0.0",
        openapi_url="/api/v1/openapi.json" if docs_enabled else None,
        docs_url="/api/v1/docs" if docs_enabled else None,
        redoc_url=None,
        # AI MODIFIED: Document the actual RFC 9457 validation contract consistently on Python 3.12+.
        responses={422: {"model": ProblemDetailsResponse, "description": "Validation failed"}},
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_allowed_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
    )
    application.add_middleware(
        BodySizeLimitMiddleware, maximum_bytes=settings.max_upload_bytes + REQUEST_OVERHEAD_BYTES
    )
    install_problem_details(application)
    application.add_middleware(ResponseSecurityMiddleware)
    for router in (
        health_router,
        finance_router,
        account_router,
        employee_router,
        driver_license_router,
        client_router,
        truck_router,
        delivery_order_router,
        trip_router,
        or_router,
        administration_router,
        webhook_router,
    ):
        application.include_router(router)
    install_openapi_contract(application)
    return application


app = create_application()
