# ===== AI GENERATED: ClerkWebhookService =====
# Purpose: Apply verified Clerk webhooks exactly once
# Inputs: raw body, headers, verifier, repositories, unit of work
# Returns: "processed" | "duplicate" | "ignored" or 400 on bad signature
# Flow:
# 1. Verify the signature over the raw body
# 2. Register the svix id; a repeat is a duplicate (no effect)
# 3. user.created/updated: link by verified email; user.deleted: deactivate
# 4. Effects, ledger and audit commit together

from ..Contract.i_audit_repository import IAuditRepository
from ..Contract.i_employee_repository import IEmployeeRepository
from ..Contract.i_unit_of_work import IUnitOfWork
from ..Contract.i_webhook_event_repository import IWebhookEventRepository
from ..Contract.i_webhook_verifier import IWebhookVerifier, WebhookSignatureError
from ..Entity.business_rule_error import BusinessRuleError

MAXIMUM_EVENT_ID_LENGTH = 128


class ClerkWebhookService:
    def __init__(
        self,
        verifier: IWebhookVerifier,
        events: IWebhookEventRepository,
        employees: IEmployeeRepository,
        audit: IAuditRepository,
        unit_of_work: IUnitOfWork,
    ) -> None:
        self._verifier = verifier
        self._events = events
        self._employees = employees
        self._audit = audit
        self._unit_of_work = unit_of_work

    def process(self, raw_body: bytes, headers: dict[str, str]) -> str:
        try:
            payload = self._verifier.verify(raw_body, headers)
        except WebhookSignatureError as signature_error:
            raise BusinessRuleError(
                400, "WEBHOOK_SIGNATURE_INVALID", "Bad request", "Webhook signature rejected."
            ) from signature_error
        event_id = headers.get("svix-id", "")
        event_type = payload.get("type")
        if not event_id or len(event_id) > MAXIMUM_EVENT_ID_LENGTH or not isinstance(event_type, str):
            raise BusinessRuleError(400, "WEBHOOK_MALFORMED", "Bad request", "Webhook event is malformed.")
        if not self._events.try_register(event_id, event_type[:64]):
            return "duplicate"
        outcome = self._apply(event_type, payload.get("data"))
        self._unit_of_work.commit()
        return outcome

    def _apply(self, event_type: str, event_data: object) -> str:
        if not isinstance(event_data, dict):
            return "ignored"
        clerk_user_id = event_data.get("id")
        if not isinstance(clerk_user_id, str) or not clerk_user_id:
            return "ignored"
        if event_type in ("user.created", "user.updated"):
            return self._link_by_verified_email(clerk_user_id, event_data)
        if event_type == "user.deleted":
            return self._deactivate_deleted_user(clerk_user_id)
        return "ignored"

    def _link_by_verified_email(self, clerk_user_id: str, event_data: dict[str, object]) -> str:
        email = self._verified_primary_email(event_data)
        if email is None:
            return "ignored"
        employee = self._employees.get_by_email(email)
        if employee is None:
            return "ignored"
        if employee.clerk_user_id == clerk_user_id:
            return "ignored"
        if employee.clerk_user_id is not None or self._employees.get_by_clerk_user_id(clerk_user_id):
            self._audit.append(
                None,
                "webhook.clerk.link_conflict",
                "employee",
                str(employee.employee_id),
                {},
                None,
            )
            return "ignored"
        self._employees.set_clerk_user_id(employee.employee_id, clerk_user_id)
        self._audit.append(
            None,
            "employee.identity_linked",
            "employee",
            str(employee.employee_id),
            {"source": "clerk_webhook"},
            None,
        )
        return "processed"

    def _deactivate_deleted_user(self, clerk_user_id: str) -> str:
        employee = self._employees.get_by_clerk_user_id(clerk_user_id)
        if employee is None or not employee.is_active:
            return "ignored"
        self._employees.set_active(employee.employee_id, False)
        self._audit.append(
            None,
            "employee.deactivated",
            "employee",
            str(employee.employee_id),
            {"source": "clerk_webhook"},
            None,
        )
        return "processed"

    @staticmethod
    def _verified_primary_email(event_data: dict[str, object]) -> str | None:
        primary_id = event_data.get("primary_email_address_id")
        addresses = event_data.get("email_addresses")
        if not isinstance(addresses, list):
            return None
        for address in addresses:
            if not isinstance(address, dict) or address.get("id") != primary_id:
                continue
            verification = address.get("verification")
            email = address.get("email_address")
            is_verified = isinstance(verification, dict) and verification.get("status") == "verified"
            if is_verified and isinstance(email, str) and email:
                return email
        return None
