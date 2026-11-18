# ===== AI GENERATED: problem_details =====
# Purpose: RFC 9457 application/problem+json for every error path
# Inputs: exceptions raised anywhere in the app
# Returns: handlers + trace-id middleware installed by install_problem_details
# Flow:
# 1. Middleware assigns a server-generated trace id per request
# 2. Handlers render validation, HTTP, business, DB and unhandled errors
# 3. Bodies never contain stack traces, SQL or file paths

import logging
import uuid
from http import HTTPStatus
from typing import cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .Entity.business_rule_error import BusinessRuleError

PROBLEM_MEDIA_TYPE = "application/problem+json"
logger = logging.getLogger("bm_enterprises.errors")


class TraceIdMiddleware:
    """Pure ASGI middleware; never trusts a client-supplied trace id."""

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return
        trace_id = uuid.uuid4().hex
        scope.setdefault("state", {})["trace_id"] = trace_id

        async def send_with_trace(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = message.setdefault("headers", [])
                if not any(name.lower() == b"x-trace-id" for name, _ in headers):
                    headers.append((b"x-trace-id", trace_id.encode()))
                # AI MODIFIED: Avoid caching employee data and disable content sniffing/framing.
                for name, value in (
                    (b"cache-control", b"no-store"),
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"referrer-policy", b"no-referrer"),
                ):
                    if not any(existing.lower() == name for existing, _ in headers):
                        headers.append((name, value))
            await send(message)

        await self._app(scope, receive, send_with_trace)


def _trace_id(request: Request) -> str:
    return getattr(request.state, "trace_id", "") or uuid.uuid4().hex


def build_problem_response(
    request: Request,
    status_code: int,
    error_code: str,
    title: str,
    detail: str,
    errors: list[dict[str, str]] | None = None,
    extra_headers: dict[str, str] | None = None,
    extensions: dict[str, object] | None = None,
) -> JSONResponse:
    body: dict[str, object] = {
        "type": f"urn:bm-enterprises:problem:{error_code.lower().replace('_', '-')}",
        "title": title,
        "status": status_code,
        "detail": detail,
        "code": error_code,
        "trace_id": _trace_id(request),
    }
    if errors:
        body["errors"] = errors
    for extension_name, extension_value in (extensions or {}).items():
        body.setdefault(extension_name, extension_value)
    trace_id = body["trace_id"]
    headers = {"X-Trace-Id": str(trace_id)}
    if status_code == 401:
        headers["WWW-Authenticate"] = "Bearer"
    headers.update(extra_headers or {})
    return JSONResponse(body, status_code=status_code, media_type=PROBLEM_MEDIA_TYPE, headers=headers)


async def handle_business_rule_error(request: Request, error: Exception) -> JSONResponse:
    error = cast(BusinessRuleError, error)
    return build_problem_response(
        request,
        error.status_code,
        error.error_code,
        error.title,
        error.detail,
        None,
        error.headers,
        error.extensions,
    )


async def handle_validation_error(request: Request, error: Exception) -> JSONResponse:
    error = cast(RequestValidationError, error)
    field_errors = [
        {"field": ".".join(str(part) for part in issue["loc"]), "message": str(issue["msg"])}
        for issue in error.errors()
    ]
    return build_problem_response(
        request, 422, "VALIDATION_ERROR", "Validation failed", "The request is invalid.", field_errors
    )


async def handle_http_error(request: Request, error: Exception) -> JSONResponse:
    error = cast(StarletteHTTPException, error)
    try:
        phrase = HTTPStatus(error.status_code)
        title, detail = phrase.phrase, phrase.description
    except ValueError:
        title, detail = "Error", "The request could not be completed."
    return build_problem_response(request, error.status_code, f"HTTP_{error.status_code}", title, detail)


async def handle_integrity_error(request: Request, error: Exception) -> JSONResponse:
    logger.warning("integrity error trace=%s", _trace_id(request))
    return build_problem_response(
        request, 409, "CONFLICT", "Conflict", "The request conflicts with existing data."
    )


async def handle_database_unavailable(request: Request, error: Exception) -> JSONResponse:
    logger.error("database unavailable trace=%s", _trace_id(request))
    return build_problem_response(
        request,
        503,
        "DATABASE_UNAVAILABLE",
        "Service unavailable",
        "The service is temporarily unavailable. Try again shortly.",
    )


async def handle_unexpected_error(request: Request, error: Exception) -> JSONResponse:
    logger.error("unhandled error trace=%s type=%s", _trace_id(request), type(error).__name__, exc_info=error)
    return build_problem_response(
        request, 500, "INTERNAL_ERROR", "Internal server error", "An unexpected error occurred."
    )


def install_problem_details(application: FastAPI) -> None:
    """Register middleware and every exception handler on the application."""
    application.add_middleware(TraceIdMiddleware)
    application.add_exception_handler(BusinessRuleError, handle_business_rule_error)
    application.add_exception_handler(RequestValidationError, handle_validation_error)
    application.add_exception_handler(StarletteHTTPException, handle_http_error)
    application.add_exception_handler(IntegrityError, handle_integrity_error)
    application.add_exception_handler(OperationalError, handle_database_unavailable)
    application.add_exception_handler(Exception, handle_unexpected_error)
