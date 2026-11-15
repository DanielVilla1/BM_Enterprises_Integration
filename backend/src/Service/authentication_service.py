# ===== AI GENERATED: AuthenticationService =====
# Purpose: Turn a bearer token into an active-employee Principal (AUTH-01)
# Inputs: raw token, token verifier, employee repository
# Returns: Principal or BusinessRuleError (401 / 403 / 503)
# Flow:
# 1. Verify the token locally (signature, issuer, expiry, azp)
# 2. Map the Clerk subject to a local employee
# 3. Reject unknown or inactive employees; load roles from PostgreSQL

from ..Contract.i_employee_repository import IEmployeeRepository
from ..Contract.i_token_verifier import (
    ITokenVerifier,
    ProviderUnavailableError,
    TokenVerificationError,
)
from ..Entity.business_rule_error import BusinessRuleError
from ..Entity.employee import Principal


class AuthenticationService:
    def __init__(self, token_verifier: ITokenVerifier, employees: IEmployeeRepository) -> None:
        self._token_verifier = token_verifier
        self._employees = employees

    def authenticate(self, raw_token: str | None) -> Principal:
        if not raw_token:
            raise BusinessRuleError(
                401, "AUTH_MISSING_TOKEN", "Authentication required", "A bearer token is required."
            )
        try:
            claims = self._token_verifier.verify(raw_token)
        except TokenVerificationError as verification_error:
            raise BusinessRuleError(
                401, "AUTH_INVALID_TOKEN", "Invalid token", "The bearer token was rejected."
            ) from verification_error
        except ProviderUnavailableError as provider_error:
            raise BusinessRuleError(
                503,
                "AUTH_PROVIDER_UNAVAILABLE",
                "Identity provider unavailable",
                "The token could not be verified right now. Try again shortly.",
            ) from provider_error
        employee = self._employees.get_by_clerk_user_id(claims.subject)
        if employee is None or not employee.is_active:
            raise BusinessRuleError(
                403,
                "AUTH_NO_ACTIVE_EMPLOYEE",
                "No active employee",
                "This account is not linked to an active employee record.",
            )
        return Principal(
            employee_id=employee.employee_id,
            clerk_user_id=claims.subject,
            full_name=employee.full_name,
            role_codes=employee.role_codes,
        )
