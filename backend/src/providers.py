# ===== AI GENERATED: providers =====
# Purpose: FastAPI dependency wiring (sessions, services, auth, permissions)
# Inputs: settings, SQLAlchemy sessions, bearer credentials
# Returns: injectable factories used by controllers
# Flow:
# 1. Build repositories and services around one request session
# 2. get_principal verifies the token and maps it to an active employee
# 3. require_capability enforces the matrix (deny by default)

from collections.abc import Iterator
from dataclasses import dataclass
from functools import lru_cache

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import get_settings
from .Contract.i_token_verifier import ITokenVerifier
from .Contract.i_webhook_verifier import IWebhookVerifier
from .database import SessionLocal
from .Entity.access import AccessLevel
from .Entity.business_rule_error import BusinessRuleError
from .Entity.employee import Principal
from .Infrastructure.Clerk.clerk_token_verifier import ClerkTokenVerifier
from .Infrastructure.Clerk.clerk_webhook_verifier import ClerkWebhookVerifier
from .rate_limiter import SlidingWindowLimiter
from .Repository.audit_repository import AuditRepository
from .Repository.employee_repository import EmployeeRepository
from .Repository.fleet_repositories import DriverLicenseRepository, TruckRepository
from .Repository.operations_repositories import ClientRepository, DeliveryOrderRepository
from .Repository.permission_repository import PermissionRepository
from .Repository.unit_of_work import SqlAlchemyUnitOfWork
from .Repository.webhook_event_repository import WebhookEventRepository
from .Service.audit_service import AuditService
from .Service.authentication_service import AuthenticationService
from .Service.authorization_service import AuthorizationService
from .Service.clerk_webhook_service import ClerkWebhookService
from .Service.client_service import ClientService
from .Service.delivery_order_service import DeliveryOrderService
from .Service.driver_license_service import DriverLicenseService
from .Service.employee_service import EmployeeService
from .Service.truck_service import TruckService

bearer_scheme = HTTPBearer(auto_error=False, description="Clerk session token")


def get_session() -> Iterator[Session]:
    """One session per request; uncommitted work is rolled back on close."""
    with SessionLocal() as session:
        yield session


@lru_cache
def get_token_verifier() -> ITokenVerifier:
    settings = get_settings()
    return ClerkTokenVerifier(
        issuer=settings.clerk_issuer,
        jwks_url=settings.clerk_jwks_url,
        audience=settings.clerk_audience,
        authorized_parties=settings.clerk_authorized_parties,
        clock_skew_seconds=settings.clerk_clock_skew_seconds,
    )


def get_webhook_verifier() -> IWebhookVerifier:
    return ClerkWebhookVerifier(get_settings().clerk_webhook_secret)


@lru_cache
def get_rate_limiter() -> SlidingWindowLimiter:
    return SlidingWindowLimiter()


def _client_key(request: Request, purpose: str) -> str:
    client_host = request.client.host if request.client else "unknown"
    return f"{purpose}:{client_host}"


def _too_many_requests() -> BusinessRuleError:
    return BusinessRuleError(
        429,
        "RATE_LIMITED",
        "Too many requests",
        "Too many requests. Wait a minute and try again.",
        {"Retry-After": "60"},
    )


def enforce_webhook_rate_limit(
    request: Request, limiter: SlidingWindowLimiter = Depends(get_rate_limiter)
) -> None:
    key = _client_key(request, "webhook")
    limiter.record(key)
    if limiter.count(key, 60) > get_settings().rate_limit_webhook_per_minute:
        raise _too_many_requests()


def get_trace_id(request: Request) -> str:
    return getattr(request.state, "trace_id", "")


def get_employee_service(session: Session = Depends(get_session)) -> EmployeeService:
    return EmployeeService(
        EmployeeRepository(session), AuditRepository(session), SqlAlchemyUnitOfWork(session)
    )


def get_client_service(session: Session = Depends(get_session)) -> ClientService:
    return ClientService(ClientRepository(session), AuditRepository(session), SqlAlchemyUnitOfWork(session))


def get_truck_service(session: Session = Depends(get_session)) -> TruckService:
    return TruckService(TruckRepository(session), AuditRepository(session), SqlAlchemyUnitOfWork(session))


def get_driver_license_service(session: Session = Depends(get_session)) -> DriverLicenseService:
    return DriverLicenseService(
        EmployeeRepository(session),
        DriverLicenseRepository(session),
        AuditRepository(session),
        SqlAlchemyUnitOfWork(session),
    )


def get_delivery_order_service(session: Session = Depends(get_session)) -> DeliveryOrderService:
    return DeliveryOrderService(
        DeliveryOrderRepository(session),
        ClientRepository(session),
        AuditRepository(session),
        SqlAlchemyUnitOfWork(session),
    )


def get_audit_service(session: Session = Depends(get_session)) -> AuditService:
    return AuditService(AuditRepository(session))


def get_authorization_service(session: Session = Depends(get_session)) -> AuthorizationService:
    settings = get_settings()
    flags = {"helper_or_upload_enabled": settings.helper_or_upload_enabled}
    return AuthorizationService(PermissionRepository(session), flags)


def get_webhook_service(
    session: Session = Depends(get_session),
    verifier: IWebhookVerifier = Depends(get_webhook_verifier),
) -> ClerkWebhookService:
    return ClerkWebhookService(
        verifier,
        WebhookEventRepository(session),
        EmployeeRepository(session),
        AuditRepository(session),
        SqlAlchemyUnitOfWork(session),
    )


def get_principal(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
    verifier: ITokenVerifier = Depends(get_token_verifier),
    limiter: SlidingWindowLimiter = Depends(get_rate_limiter),
) -> Principal:
    key = _client_key(request, "auth-failure")
    if limiter.count(key, 60) >= get_settings().rate_limit_failed_auth_per_minute:
        raise _too_many_requests()
    authentication = AuthenticationService(verifier, EmployeeRepository(session))
    try:
        return authentication.authenticate(credentials.credentials if credentials else None)
    except BusinessRuleError as rejection:
        if rejection.status_code in (401, 403):
            limiter.record(key)
        raise


get_principal.requires_authentication = True  # type: ignore[attr-defined]


@dataclass(frozen=True)
class AccessContext:
    """The authenticated principal plus its strongest level for the capability."""

    principal: Principal
    level: AccessLevel


def require_capability(capability: str, minimum_level: AccessLevel | None = None):
    """Dependency factory: 403 unless a role grants the capability (at the minimum level)."""

    def check_capability(
        principal: Principal = Depends(get_principal),
        authorization: AuthorizationService = Depends(get_authorization_service),
    ) -> AccessContext:
        level = authorization.require_level(principal, capability)
        if minimum_level is not None and level.rank < minimum_level.rank:
            raise BusinessRuleError(
                403, "PERMISSION_DENIED", "Forbidden", "Your role does not allow this action."
            )
        return AccessContext(principal, level)

    check_capability.capability = capability  # type: ignore[attr-defined]
    check_capability.minimum_level = minimum_level  # type: ignore[attr-defined]
    return check_capability
