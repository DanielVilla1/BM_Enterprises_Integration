# ===== AI GENERATED: FinancialWorkflow =====
# Purpose: Shared transaction, authorization, retry and receipt-correction controls.
# Inputs: Repository ports, permission service, audit and unit of work.
# Returns: Command results and immutable domain records.
# Flow: Lock; validate retry identity; apply one command; audit and commit atomically.

import hashlib
import json
from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel

from ..Contract.i_audit_repository import IAuditRepository
from ..Contract.i_document_repositories import IOrDocumentRepository
from ..Contract.i_employee_repository import IEmployeeRepository
from ..Contract.i_financial_repository import IFinancialRepository
from ..Contract.i_fleet_repositories import ITruckRepository
from ..Contract.i_operations_repositories import IClientRepository, IDeliveryOrderRepository
from ..Contract.i_trip_repository import ITripRepository
from ..Contract.i_unit_of_work import IUnitOfWork
from ..DTO.finance_dto import CommandResponse
from ..Entity.access import AccessLevel, RoleCode
from ..Entity.business_rule_error import BusinessRuleError
from ..Entity.clock import MANILA_OFFSET, manila_today
from ..Entity.dispatch import Trip, TripStatus
from ..Entity.documents import OrDocumentKind
from ..Entity.employee import Principal
from ..Entity.finance import (
    ZERO,
    Advance,
    AdvanceMovement,
    Earning,
    FinancialOperation,
    FinancialRecord,
    Invoice,
    InvoiceLine,
    RateVersion,
    TripFinancial,
)
from .authorization_service import AuthorizationService

RecordType = TypeVar("RecordType", bound=FinancialRecord)


def reject(code: str, detail: str, status: int = 409) -> BusinessRuleError:
    """Stable domain failure, translated by the existing problem-details handler."""
    return BusinessRuleError(status, code, "Forbidden" if status == 403 else "Financial workflow", detail)


def business_date(moment: datetime) -> date:
    """SQLite timestamps are naive UTC; all financial cutoffs use Manila dates."""
    return (moment.replace(tzinfo=UTC) if moment.tzinfo is None else moment).astimezone(MANILA_OFFSET).date()


class FinancialWorkflow:
    def __init__(
        self,
        finances: IFinancialRepository,
        trips: ITripRepository,
        orders: IDeliveryOrderRepository,
        documents: IOrDocumentRepository,
        employees: IEmployeeRepository,
        authorization: AuthorizationService,
        audit: IAuditRepository,
        unit_of_work: IUnitOfWork,
        deductions_enabled: bool = False,
        clients: IClientRepository | None = None,
        presentation_enabled: bool = False,
        trucks: ITruckRepository | None = None,
    ) -> None:
        self.finances = finances
        self.trips = trips
        self.orders = orders
        self.documents = documents
        self.employees = employees
        self.authorization = authorization
        self.audit = audit
        self.unit_of_work = unit_of_work
        self.deductions_enabled = deductions_enabled
        self.clients = clients
        self.presentation_enabled = presentation_enabled
        self.trucks = trucks

    def execute(
        self,
        principal: Principal,
        key: str,
        operation: str,
        payload: BaseModel,
        trace_id: str | None,
        command: Callable[[], FinancialRecord],
    ) -> CommandResponse:
        fingerprint = hashlib.sha256(
            (operation + ":" + json.dumps(payload.model_dump(mode="json"), sort_keys=True)).encode()
        ).hexdigest()
        try:
            self.finances.lock()
            previous = self.finances.find(FinancialOperation, actor_id=principal.employee_id, key=key)
            if previous:
                if previous[0].fingerprint != fingerprint:
                    raise reject("IDEMPOTENCY_CONFLICT", "This key was already used for a different command.")
                return CommandResponse.model_validate(previous[0].response)
            record = command()
            state = "HELD" if getattr(record, "held", False) else getattr(record, "state", "SAVED")
            response = CommandResponse(record_id=record.record_id, state=state)
            self.finances.save(
                FinancialOperation(
                    actor_id=principal.employee_id,
                    key=key,
                    fingerprint=fingerprint,
                    response=response.model_dump(mode="json"),
                )
            )
            self.audit.append(
                principal.employee_id,
                operation.split(":")[0],
                type(record).__name__,
                str(record.record_id),
                {
                    "reason": getattr(payload, "reason", ""),
                    "idempotency_key": key,
                    "request": payload.model_dump(mode="json"),
                },
                trace_id,
            )
            self.unit_of_work.commit()
            return response
        except Exception:
            self.unit_of_work.rollback()
            raise

    def require(self, principal: Principal, capability: str, full: bool = True) -> AccessLevel:
        level = self.authorization.require_level(principal, capability)
        if full and level is not AccessLevel.FULL:
            raise reject("PERMISSION_DENIED", "Your role does not allow this action.", 403)
        return level

    @staticmethod
    def independent(principal: Principal, *people: UUID | None) -> None:
        if principal.employee_id in people:
            raise reject("SELF_APPROVAL_FORBIDDEN", "A different authorized person must approve this record.")

    def load(self, record_type: type[RecordType], identifier: UUID) -> RecordType:
        record = self.finances.get(record_type, identifier)
        if record is None:
            raise reject("FINANCIAL_RECORD_NOT_FOUND", "The financial record was not found.", 404)
        return record

    def trip(self, trip_id: UUID, principal: Principal | None = None, own: bool = False) -> Trip:
        trip = self.trips.get_by_id(trip_id)
        if trip is None or (
            own and principal and principal.employee_id not in (trip.driver_id, *trip.helper_ids)
        ):
            raise reject("TRIP_NOT_FOUND", "The trip was not found.", 404)
        return trip

    def employee(self, employee_id: UUID) -> None:
        employee = self.employees.get_by_id(employee_id)
        if employee is None or not employee.is_active:
            raise reject("EMPLOYEE_NOT_FOUND", "Select an active employee.", 404)

    def financial(self, trip_id: UUID) -> TripFinancial:
        records = self.finances.find(TripFinancial, trip_id=trip_id)
        return records[0] if records else TripFinancial(trip_id=trip_id)

    def rate_at(self, departed_at: datetime) -> RateVersion:
        versions = [
            version
            for version in self.finances.find(RateVersion)
            if version.effective_on <= business_date(departed_at)
        ]
        return max(versions, key=lambda version: version.effective_on)

    def snapshot_departure(self, trip_id: UUID) -> None:
        """Called in the departure transaction; immutable versions also cover legacy trips."""
        trip = self.trip(trip_id)
        if trip.departed_at:
            financial = self.financial(trip_id)
            if financial.rate_id is None:
                self.finances.save(replace(financial, rate_id=self.rate_at(trip.departed_at).record_id))

    def lock_finances(self) -> None:
        self.finances.lock()

    def hold_receipt(self, trip_id: UUID, reason: str) -> None:
        """Run inside the Owner receipt-correction transaction, before its commit."""
        self.finances.save(replace(self.financial(trip_id), held=True, hold_reason=reason))
        for earning in self.finances.find(Earning, trip_id=trip_id):
            self.finances.save(replace(earning, state="HELD"))
        for line in self.finances.find(InvoiceLine, trip_id=trip_id, active=True):
            self.finances.save(replace(self.load(Invoice, line.invoice_id), held=True))

    def balance(self, advance: Advance) -> tuple[Decimal, Decimal]:
        movements = self.finances.find(AdvanceMovement, advance_id=advance.record_id)
        released = sum((entry.amount for entry in movements if entry.kind == "RELEASE"), ZERO)
        reductions = sum((entry.amount for entry in movements if entry.kind in ("REPAYMENT", "RETURN")), ZERO)
        reversed_total = sum((entry.amount for entry in movements if entry.kind == "REVERSAL"), ZERO)
        return released, released - reductions + reversed_total

    def billing_ready(self, trip: Trip, allow_allocated: bool = False) -> bool:
        financial = self.financial(trip.trip_id)
        signed = any(
            document.kind is OrDocumentKind.SIGNED_OR
            for document in self.documents.list_for_trip(trip.trip_id, False)
        )
        allocated = self.finances.find(InvoiceLine, trip_id=trip.trip_id, active=True)
        return self.billing_ready_from_facts(trip, financial, signed, bool(allocated), allow_allocated)

    @staticmethod
    def billing_ready_from_facts(
        trip: Trip, financial: TripFinancial, signed: bool, allocated: bool, allow_allocated: bool = False
    ) -> bool:
        return bool(
            trip.status is TripStatus.COMPLETED
            and trip.receipt_confirmed_at
            and signed
            and financial.charge_state == "FINALIZED"
            and not financial.held
            and (allow_allocated or not allocated)
        )

    @staticmethod
    def require_past_date(moment: date) -> None:
        if moment > manila_today():
            raise reject(
                "FUTURE_FINANCIAL_DATE", "Record the actual business date; it cannot be in the future."
            )

    def has_role(self, principal: Principal, role: RoleCode) -> bool:
        return role in principal.role_codes
