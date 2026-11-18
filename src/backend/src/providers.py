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
from .Contract.i_storage import IImageSanitizer, IObjectStorage
from .Contract.i_token_verifier import ITokenVerifier
from .Contract.i_webhook_verifier import IWebhookVerifier
from .database import SessionLocal
from .Entity.access import AccessLevel
from .Entity.business_rule_error import BusinessRuleError
from .Entity.employee import Principal
from .Infrastructure.Clerk.clerk_token_verifier import ClerkTokenVerifier
from .Infrastructure.Clerk.clerk_webhook_verifier import ClerkWebhookVerifier
from .Infrastructure.Imaging.pillow_image_sanitizer import PillowImageSanitizer
from .Infrastructure.Supabase.supabase_object_storage import SupabaseObjectStorage
from .rate_limiter import SlidingWindowLimiter
from .Repository.audit_repository import AuditRepository
from .Repository.document_repositories import IdempotencyRepository, OrDocumentRepository
from .Repository.employee_repository import EmployeeRepository
from .Repository.financial_repository import FinancialRepository
from .Repository.fleet_repositories import DriverLicenseRepository, TruckRepository
from .Repository.operations_repositories import ClientRepository, DeliveryOrderRepository
from .Repository.permission_repository import PermissionRepository
from .Repository.trip_repository import TripRepository
from .Repository.unit_of_work import SqlAlchemyUnitOfWork
from .Repository.webhook_event_repository import WebhookEventRepository
from .Service.advance_service import AdvanceService
from .Service.audit_service import AuditService
from .Service.authentication_service import AuthenticationService
from .Service.authorization_service import AuthorizationService
from .Service.billing_service import BillingService
from .Service.clerk_webhook_service import ClerkWebhookService
from .Service.client_service import ClientService
from .Service.delivery_order_service import DeliveryOrderService
from .Service.driver_license_service import DriverLicenseService
from .Service.employee_service import EmployeeService
from .Service.finance_query_service import FinanceQueryService
from .Service.financial_workflow import FinancialWorkflow
from .Service.or_service import OrService
from .Service.payroll_service import PayrollService
from .Service.trip_finance_service import TripFinanceService
from .Service.trip_service import TripService
from .Service.trip_state_synchronizer import TripStateSynchronizer
from .Service.truck_service import TruckService

# AI MODIFIED: Apply atomic, bounded budgets by peer address and verified employee identity.

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


def get_object_storage() -> IObjectStorage:
    settings = get_settings()
    return SupabaseObjectStorage(
        settings.supabase_url, settings.supabase_service_key, settings.supabase_bucket
    )


def get_image_sanitizer() -> IImageSanitizer:
    return PillowImageSanitizer()


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
    if not limiter.allow(key, get_settings().rate_limit_webhook_per_minute):
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


def get_trip_service(session: Session = Depends(get_session)) -> TripService:
    return TripService(
        TripRepository(session),
        DeliveryOrderRepository(session),
        TruckRepository(session),
        EmployeeRepository(session),
        DriverLicenseRepository(session),
        OrDocumentRepository(session),
        AuditRepository(session),
        SqlAlchemyUnitOfWork(session),
        financial_controls=get_trip_finance_service(session),
    )


def get_or_service(
    session: Session = Depends(get_session),
    storage: IObjectStorage = Depends(get_object_storage),
    sanitizer: IImageSanitizer = Depends(get_image_sanitizer),
) -> OrService:
    settings = get_settings()
    trips = TripRepository(session)
    return OrService(
        trips,
        OrDocumentRepository(session),
        IdempotencyRepository(session),
        storage,
        sanitizer,
        AuditRepository(session),
        SqlAlchemyUnitOfWork(session),
        TripStateSynchronizer(trips, DeliveryOrderRepository(session), TruckRepository(session)),
        get_trip_service(session),
        settings.signed_url_ttl_seconds,
        settings.max_upload_bytes,
        financial_controls=get_trip_finance_service(session),
        presentation_enabled=settings.environment.lower() in {"development", "test", "presentation"},
    )


def get_audit_service(session: Session = Depends(get_session)) -> AuditService:
    return AuditService(AuditRepository(session))


def get_authorization_service(session: Session = Depends(get_session)) -> AuthorizationService:
    settings = get_settings()
    flags = {"helper_or_upload_enabled": settings.helper_or_upload_enabled}
    return AuthorizationService(PermissionRepository(session), flags)


# AI MODIFIED: Financial services share one request session and transaction ports.
def _financial_service(service_type: type[FinancialWorkflow], session: Session) -> FinancialWorkflow:
    return service_type(
        FinancialRepository(session),
        TripRepository(session),
        DeliveryOrderRepository(session),
        OrDocumentRepository(session),
        EmployeeRepository(session),
        get_authorization_service(session),
        AuditRepository(session),
        SqlAlchemyUnitOfWork(session),
        get_settings().payroll_deductions_enabled,
        ClientRepository(session),
        get_settings().environment.lower() in {"development", "test", "presentation"},
        TruckRepository(session),
    )


def get_trip_finance_service(session: Session = Depends(get_session)) -> TripFinanceService:
    return _financial_service(TripFinanceService, session)  # type: ignore[return-value]


def get_advance_service(session: Session = Depends(get_session)) -> AdvanceService:
    return _financial_service(AdvanceService, session)  # type: ignore[return-value]


def get_payroll_service(session: Session = Depends(get_session)) -> PayrollService:
    return _financial_service(PayrollService, session)  # type: ignore[return-value]


def get_billing_service(session: Session = Depends(get_session)) -> BillingService:
    return _financial_service(BillingService, session)  # type: ignore[return-value]


def get_finance_query_service(session: Session = Depends(get_session)) -> FinanceQueryService:
    return _financial_service(FinanceQueryService, session)  # type: ignore[return-value]


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
    settings = get_settings()
    if not limiter.allow(_client_key(request, "api-ip"), settings.rate_limit_api_ip_per_minute):
        raise _too_many_requests()
    if not limiter.allow(key, settings.rate_limit_failed_auth_per_minute, consume=False):
        raise _too_many_requests()
    authentication = AuthenticationService(verifier, EmployeeRepository(session))
    try:
        principal = authentication.authenticate(credentials.credentials if credentials else None)
    except BusinessRuleError as rejection:
        if rejection.status_code in (401, 403):
            if not limiter.allow(key, settings.rate_limit_failed_auth_per_minute):
                raise _too_many_requests() from rejection
        raise
    if not limiter.allow(f"api-user:{principal.employee_id}", settings.rate_limit_api_user_per_minute):
        raise _too_many_requests()
    return principal


def enforce_upload_rate_limit(
    request: Request,
    principal: Principal = Depends(get_principal),
    limiter: SlidingWindowLimiter = Depends(get_rate_limiter),
) -> None:
    """Throttle image-processing/storage attempts before reading and sanitizing the file."""
    settings = get_settings()
    if not limiter.allow(_client_key(request, "upload-ip"), settings.rate_limit_upload_ip_per_minute):
        raise _too_many_requests()
    if not limiter.allow(f"upload-user:{principal.employee_id}", settings.rate_limit_upload_user_per_minute):
        raise _too_many_requests()


get_principal.requires_authentication = True  # type: ignore[attr-defined]


@dataclass(frozen=True)
class AccessContext:
    """The authenticated principal plus its strongest level for the capability."""

    principal: Principal
    level: AccessLevel


def require_capability(
    capability: str,
    minimum_level: AccessLevel | None = None,
    only_levels: tuple[AccessLevel, ...] | None = None,
):
    """Dependency factory: 403 unless a role grants the capability (at the required level)."""

    def check_capability(
        principal: Principal = Depends(get_principal),
        authorization: AuthorizationService = Depends(get_authorization_service),
    ) -> AccessContext:
        level = authorization.require_level(principal, capability)
        too_weak = minimum_level is not None and level.rank < minimum_level.rank
        not_allowed = only_levels is not None and level not in only_levels
        if too_weak or not_allowed:
            raise BusinessRuleError(
                403, "PERMISSION_DENIED", "Forbidden", "Your role does not allow this action."
            )
        return AccessContext(principal, level)

    check_capability.capability = capability  # type: ignore[attr-defined]
    check_capability.minimum_level = minimum_level  # type: ignore[attr-defined]
    check_capability.only_levels = only_levels  # type: ignore[attr-defined]
    return check_capability
