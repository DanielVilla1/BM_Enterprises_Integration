# ===== AI GENERATED: business_rule_error =====
# Purpose: Domain exception carrying an HTTP status and stable error code
# Inputs: status_code, error_code, title, detail
# Returns: exception translated to problem+json by the API layer
# Flow:
# 1. Services raise it when a rule or permission fails
# 2. A global handler renders application/problem+json


class BusinessRuleError(Exception):
    """Raised by services; never carries internal details."""

    def __init__(self, status_code: int, error_code: str, title: str, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.error_code = error_code
        self.title = title
        self.detail = detail
