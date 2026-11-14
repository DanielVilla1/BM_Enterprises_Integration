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
from .Repository.audit_repository import AuditRepository
from .Repository.employee_repository import EmployeeRepository
from .Repository.permission_repository import PermissionRepository
from .Repository.unit_of_work import SqlAlchemyUnitOfWork
from .Repository.webhook_event_repository import WebhookEventRepository
from .Service.audit_service import AuditService
from .Service.authentication_service import AuthenticationService
from .Service.authorization_service import AuthorizationService
from .Service.clerk_webhook_service import ClerkWebhookService
from .Service.employee_service import EmployeeService

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


def get_trace_id(request: Request) -> str:
    return getattr(request.state, "trace_id", "")


def get_employee_service(session: Session = Depends(get_session)) -> EmployeeService:
    return EmployeeService(
        EmployeeRepository(session), AuditRepository(session), SqlAlchemyUnitOfWork(session)
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
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
    verifier: ITokenVerifier = Depends(get_token_verifier),
) -> Principal:
    authentication = AuthenticationService(verifier, EmployeeRepository(session))
    return authentication.authenticate(credentials.credentials if credentials else None)


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
