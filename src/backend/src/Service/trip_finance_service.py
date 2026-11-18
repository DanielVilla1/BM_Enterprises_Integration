# ===== AI GENERATED: TripFinanceService =====
# Purpose: Expense review, final charges, versioned rates and original earnings.
# Inputs: Authorized commands and the common financial transaction context.
# Returns: Immutable domain records; completion never depends on financial readiness.
# Flow: Review independently; finalize source values; snapshot percentages; generate once.

import logging
from dataclasses import replace
from decimal import Decimal
from uuid import UUID

from ..DTO.finance_dto import ChargeRequest, ExpenseRequest, RateRequest, ReviewRequest
from ..Entity.access import AccessLevel
from ..Entity.business_rule_error import BusinessRuleError
from ..Entity.clock import manila_today
from ..Entity.dispatch import TripStatus
from ..Entity.employee import Principal
from ..Entity.finance import (
    ZERO,
    Earning,
    ExpenseSheet,
    Invoice,
    InvoiceLine,
    RateVersion,
    TripFinancial,
    money,
)
from .financial_workflow import FinancialWorkflow, business_date, reject


class TripFinanceService(FinancialWorkflow):
    def save_expenses(self, principal: Principal, trip_id: UUID, payload: ExpenseRequest) -> ExpenseSheet:
        level = self.require(principal, "expense.enter", full=False)
        trip = self.trip(trip_id, principal, level is AccessLevel.OWN)
        if level is AccessLevel.OWN and trip.driver_id != principal.employee_id:
            raise reject("TRIP_NOT_FOUND", "Only the assigned driver can enter these expenses.", 404)
        if trip.status in (TripStatus.CANCELLED, TripStatus.FAILED):
            raise reject(
                "TRIP_FINANCIALLY_CLOSED", "Cancelled/failed trip compensation requires separate review."
            )
        existing = self.finances.find(ExpenseSheet, trip_id=trip_id)
        sheet = existing[0] if existing else ExpenseSheet(trip_id=trip_id, entered_by=principal.employee_id)
        if sheet.state not in ("ENTERING",):
            raise reject(
                "EXPENSES_LOCKED",
                "Return submitted expenses for changes; finalized records require adjustments.",
            )
        if payload.declared_zero == bool(payload.lines):
            raise reject(
                "EXPLICIT_EXPENSES_REQUIRED",
                "Provide expense lines or explicitly declare zero, with a reason.",
            )
        for line in payload.lines:
            self.require_past_date(line.incurred_on)
        return self.finances.save(
            replace(
                sheet,
                entered_by=principal.employee_id,
                reviewed_by=None,
                reason=payload.reason,
                declared_zero=payload.declared_zero,
                contributors=sorted(set(sheet.contributors) | {str(principal.employee_id)}),
                lines=[line.model_dump(mode="json") for line in payload.lines],
                total=money(sum((line.amount for line in payload.lines), ZERO)),
            )
        )

    def submit_expenses(self, principal: Principal, trip_id: UUID) -> ExpenseSheet:
        level = self.require(principal, "expense.enter", full=False)
        trip = self.trip(trip_id, principal, level is AccessLevel.OWN)
        if level is AccessLevel.OWN and trip.driver_id != principal.employee_id:
            raise reject("TRIP_NOT_FOUND", "The trip was not found.", 404)
        sheets = self.finances.find(ExpenseSheet, trip_id=trip_id)
        if not sheets or sheets[0].state != "ENTERING":
            raise reject("EXPENSES_NOT_ENTERING", "Save an explicit expense declaration first.")
        return self.finances.save(replace(sheets[0], state="AWAITING_REVIEW"))

    def review_expenses(self, principal: Principal, trip_id: UUID, payload: ReviewRequest) -> ExpenseSheet:
        self.require(principal, "expense.approve")
        sheets = self.finances.find(ExpenseSheet, trip_id=trip_id)
        if not sheets or sheets[0].state != "AWAITING_REVIEW":
            raise reject("EXPENSES_NOT_SUBMITTED", "Submit expenses for independent review first.")
        sheet = sheets[0]
        trip = self.trip(trip_id)
        self.independent(
            principal,
            sheet.entered_by,
            trip.driver_id,
            *trip.helper_ids,
            *(UUID(identifier) for identifier in sheet.contributors),
        )
        state = ("CONFIRMED_ZERO" if sheet.declared_zero else "FINALIZED") if payload.approved else "ENTERING"
        reviewed = self.finances.save(
            replace(
                sheet,
                state=state,
                reviewed_by=principal.employee_id if payload.approved else None,
                reason=payload.reason,
            )
        )
        self._auto_calculate(trip_id)
        return reviewed

    def finalize_charge(self, principal: Principal, trip_id: UUID, payload: ChargeRequest) -> TripFinancial:
        self.require(principal, "charge.finalize")
        self.trip(trip_id)
        financial = self.financial(trip_id)
        if financial.charge_state == "FINALIZED":
            raise reject("CHARGE_FINALIZED", "Final charges are immutable; use a reviewed correction.")
        variance = payload.amount != payload.agreed_amount
        finalized = self.finances.save(
            replace(
                financial,
                charge=payload.amount,
                agreed_amount=payload.agreed_amount,
                entered_by=principal.employee_id,
                reference=payload.reference,
                reason=payload.reason,
                charge_state="AWAITING_REVIEW" if variance else "FINALIZED",
                finalized_by=None if variance else principal.employee_id,
            )
        )
        self._auto_calculate(trip_id)
        return finalized

    def approve_charge_variance(self, principal: Principal, trip_id: UUID) -> TripFinancial:
        self.require(principal, "earning_percentage.set")
        financial = self.financial(trip_id)
        if financial.charge_state != "AWAITING_REVIEW":
            raise reject("CHARGE_NOT_PENDING", "This charge has no pending variance review.")
        self.independent(principal, financial.entered_by)
        trip = self.trip(trip_id)
        self.independent(principal, trip.driver_id, *trip.helper_ids)
        finalized = self.finances.save(
            replace(financial, charge_state="FINALIZED", finalized_by=principal.employee_id)
        )
        self._auto_calculate(trip_id)
        return finalized

    def create_rate(self, principal: Principal, payload: RateRequest) -> RateVersion:
        self.require(principal, "earning_percentage.set")
        if payload.effective_on <= manila_today():
            raise reject("FUTURE_RATE_REQUIRED", "Rates must start at midnight Manila on a future date.")
        if payload.driver_one + payload.helper_one > 100 or payload.driver_two + payload.helper_two * 2 > 100:
            raise reject("INVALID_RATE_TOTAL", "Crew percentages cannot exceed 100 percent.")
        if self.finances.find(RateVersion, effective_on=payload.effective_on):
            raise reject("RATE_DATE_EXISTS", "A rate version already exists for that date.")
        return self.finances.save(RateVersion(**payload.model_dump(), entered_by=principal.employee_id))

    def generate_earnings(self, principal: Principal, trip_id: UUID) -> TripFinancial:
        self.require(principal, "earnings.calculate")
        return self._calculate_earnings(trip_id)

    def _auto_calculate(self, trip_id: UUID) -> None:
        try:
            self._calculate_earnings(trip_id)
        except BusinessRuleError as failure:
            if failure.error_code not in ("PENDING_CALCULATION", "FINANCIAL_HOLD"):
                raise

    def after_completion(self, trip_id: UUID, trace_id: str | None) -> None:
        """A new financial transaction follows successful operational completion.

        A calculation failure cannot undo receipt confirmation or block dispatch.
        The authorized calculate command and pending-calculation report permit retries.
        """
        try:
            self.finances.lock()
            previous = self.finances.find(Earning, trip_id=trip_id)
            self._auto_calculate(trip_id)
            if not previous and self.finances.find(Earning, trip_id=trip_id):
                self.audit.append(
                    None,
                    "earnings.generated",
                    "trip",
                    str(trip_id),
                    {"trigger": "receipt_completion"},
                    trace_id,
                )
            self.unit_of_work.commit()
        except Exception:
            self.unit_of_work.rollback()
            logging.getLogger(__name__).warning("Earnings calculation remains pending for trip %s", trip_id)

    def _calculate_earnings(self, trip_id: UUID) -> TripFinancial:
        trip = self.trip(trip_id)
        financial = self.financial(trip_id)
        if financial.held:
            if financial.hold_reason == "NEGATIVE_EARNINGS_BASE":
                return financial
            raise reject("FINANCIAL_HOLD", financial.hold_reason)
        sheets = self.finances.find(ExpenseSheet, trip_id=trip_id)
        if (
            trip.status is not TripStatus.COMPLETED
            or not trip.receipt_confirmed_at
            or not trip.departed_at
            or financial.charge_state != "FINALIZED"
            or financial.charge is None
            or not sheets
            or sheets[0].state not in ("FINALIZED", "CONFIRMED_ZERO")
        ):
            raise reject(
                "PENDING_CALCULATION",
                "Complete the trip, finalize its charge and independently review expenses first.",
            )
        if self.finances.find(Earning, trip_id=trip_id):
            return financial
        base = financial.charge - sheets[0].total
        if base < ZERO:
            # Persist the review hold; this is a successful command with a held outcome.
            return self.finances.save(replace(financial, held=True, hold_reason="NEGATIVE_EARNINGS_BASE"))
        version = (
            self.load(RateVersion, financial.rate_id) if financial.rate_id else self.rate_at(trip.departed_at)
        )
        financial = self.finances.save(replace(financial, rate_id=version.record_id))
        two_helpers = len(trip.helper_ids) == 2
        percentages = [version.driver_two if two_helpers else version.driver_one]
        percentages += [version.helper_two if two_helpers else version.helper_one] * len(trip.helper_ids)
        amounts = [money(base * percentage / Decimal("100")) for percentage in percentages]
        variance = sum(amounts, ZERO) - money(base * sum(percentages, ZERO) / Decimal("100"))
        for position, (employee_id, percentage, amount) in enumerate(
            zip((trip.driver_id, *trip.helper_ids), percentages, amounts, strict=True)
        ):
            self.finances.save(
                Earning(
                    trip_id=trip_id,
                    employee_id=employee_id,
                    rate_id=version.record_id,
                    percentage=percentage,
                    base=base,
                    amount=amount,
                    original_date=business_date(trip.receipt_confirmed_at),
                    rounding_variance=variance if position == 0 else ZERO,
                )
            )
        return financial

    def release_hold(self, principal: Principal, trip_id: UUID) -> TripFinancial:
        self.require(principal, "earning_percentage.set")
        trip = self.trip(trip_id)
        self.independent(principal, trip.driver_id, *trip.helper_ids)
        financial = self.financial(trip_id)
        if not financial.held or trip.status is not TripStatus.COMPLETED or not trip.receipt_confirmed_at:
            raise reject(
                "HOLD_NOT_RELEASABLE", "Reconfirm actual company receipt before releasing this hold."
            )
        sheets = self.finances.find(ExpenseSheet, trip_id=trip_id)
        if financial.charge is not None and sheets and financial.charge < sheets[0].total:
            raise reject(
                "NEGATIVE_EARNINGS_BASE", "Negative earnings need a separately reviewed financial correction."
            )
        financial = self.finances.save(replace(financial, held=False, hold_reason=""))
        for earning in self.finances.find(Earning, trip_id=trip_id):
            self.finances.save(replace(earning, state="READY"))
        for line in self.finances.find(InvoiceLine, trip_id=trip_id, active=True):
            invoice = self.load(Invoice, line.invoice_id)
            lines = self.finances.find(InvoiceLine, invoice_id=invoice.record_id, active=True)
            held = any(self.financial(entry.trip_id).held for entry in lines)
            self.finances.save(replace(invoice, held=held))
        return financial
