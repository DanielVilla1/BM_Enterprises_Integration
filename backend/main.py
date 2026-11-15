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
from .src.Controller.employee_controller import router as employee_router
from .src.Controller.health_controller import router as health_router
from .src.Controller.webhook_controller import router as webhook_router
from .src.problem_details import install_problem_details


def create_application() -> FastAPI:
    settings = get_settings()
    docs_enabled = settings.enable_api_docs
    application = FastAPI(
        title="BM Enterprises Hauling API",
        version="1.0.0",
        openapi_url="/api/v1/openapi.json" if docs_enabled else None,
        docs_url="/api/v1/docs" if docs_enabled else None,
        redoc_url=None,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_allowed_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
    )
    install_problem_details(application)
    for router in (
        health_router,
        account_router,
        employee_router,
        administration_router,
        webhook_router,
    ):
        application.include_router(router)
    return application


app = create_application()
