# ===== AI GENERATED: PayrollService =====
# Purpose: Payroll previews, approved adjustments, once-only repayment posting and payments.
# Inputs: Ready original earnings and independently approved employee arrangements.
# Returns: Immutable statements and payment/reversal ledgers.
# Flow: Draft without posting; finalize atomically; refuse negative pay and held earnings.

from dataclasses import replace
from decimal import Decimal
from uuid import UUID, uuid5

from ..DTO.finance_dto import AdjustmentRequest, PaymentRequest, PayrollRequest
from ..Entity.clock import manila_today
from ..Entity.employee import Principal
from ..Entity.finance import (
    ZERO,
    Advance,
    AdvanceMovement,
    Earning,
    FinancialPayment,
    PayAdjustment,
    Payroll,
    PayStatement,
    payroll_period,
)
from .financial_workflow import FinancialWorkflow, reject


class PayrollService(FinancialWorkflow):
    def propose_adjustment(self, principal: Principal, payload: AdjustmentRequest) -> PayAdjustment:
        self.require(
            principal,
            "payroll_adjustment.prepare" if payload.kind in ("CREDIT", "DEBIT") else "deduction.record",
        )
        self.employee(payload.employee_id)
        if payload.kind != "CREDIT" and not self.deductions_enabled:
            raise reject(
                "DEDUCTIONS_DISABLED",
                "D16 review must authorize employee deductions before they can be enabled.",
            )
        if payload.period_start != payroll_period(payload.period_start)[0]:
            raise reject("INVALID_PAYROLL_PERIOD", "Select the 1st or 16th for the payroll period.")
        return self.finances.save(PayAdjustment(**payload.model_dump(), entered_by=principal.employee_id))

    def approve_adjustment(self, principal: Principal, identifier: UUID) -> PayAdjustment:
        self.require(principal, "deduction.approve")
        adjustment = self.load(PayAdjustment, identifier)
        self.independent(principal, adjustment.entered_by, adjustment.employee_id)
        if adjustment.state != "PENDING":
            raise reject("ADJUSTMENT_NOT_PENDING", "This proposal has already been reviewed.")
        if adjustment.kind != "CREDIT" and not self.deductions_enabled:
            raise reject("DEDUCTIONS_DISABLED", "Employee deductions are disabled pending D16 review.")
        return self.finances.save(replace(adjustment, state="APPROVED", approved_by=principal.employee_id))

    def prepare_payroll(self, principal: Principal, payload: PayrollRequest) -> Payroll:
        self.require(principal, "payroll.prepare")
        start_on, end_on = payroll_period(payload.start_on)
        if payload.start_on != start_on:
            raise reject("INVALID_PAYROLL_PERIOD", "Payroll starts on the 1st or 16th.")
        if self.finances.find(Payroll, start_on=start_on):
            raise reject("PAYROLL_EXISTS", "This period already has a payroll record.")
        return self.finances.save(
            Payroll(start_on=start_on, end_on=end_on, prepared_by=principal.employee_id)
        )

    def eligible_earnings(self, payroll: Payroll) -> list[Earning]:
        return [
            earning
            for earning in self.finances.find(Earning, payroll_id=None)
            if earning.original_date <= payroll.end_on
            and earning.state == "READY"
            and not self.financial(earning.trip_id).held
        ]

    def preview(self, payroll: Payroll) -> list[PayStatement]:
        earnings = self.eligible_earnings(payroll)
        adjustments = [
            entry
            for entry in self.finances.find(PayAdjustment, payroll_id=None, state="APPROVED")
            if entry.period_start <= payroll.start_on
        ]
        employee_ids = sorted({entry.employee_id for entry in (*earnings, *adjustments)}, key=str)
        statements: list[PayStatement] = []
        for employee_id in employee_ids:
            employee_earnings = [entry for entry in earnings if entry.employee_id == employee_id]
            employee_adjustments = [entry for entry in adjustments if entry.employee_id == employee_id]
            gross = sum((entry.amount for entry in employee_earnings), ZERO)
            gross += sum((entry.amount for entry in employee_adjustments if entry.kind == "CREDIT"), ZERO)
            deductions = sum((entry.amount for entry in employee_adjustments if entry.kind != "CREDIT"), ZERO)
            if deductions and not self.deductions_enabled:
                raise reject(
                    "DEDUCTIONS_DISABLED", "This payroll includes deductions that are currently disabled."
                )
            if deductions > gross:
                raise reject(
                    "NEGATIVE_NET_PAY",
                    "Approved deductions exceed available gross; review this employee's arrangement.",
                )
            available = gross - deductions
            repayments = ZERO
            lines = [
                {
                    "kind": "EARNING",
                    "record_id": str(entry.record_id),
                    "trip_id": str(entry.trip_id),
                    "original_date": entry.original_date.isoformat(),
                    "percentage": str(entry.percentage),
                    "amount": str(entry.amount),
                    "carry_forward": str(entry.original_date < payroll.start_on),
                }
                for entry in employee_earnings
            ]
            lines += [
                {
                    "kind": entry.kind,
                    "record_id": str(entry.record_id),
                    "amount": str(entry.amount),
                    "reason": entry.reason,
                }
                for entry in employee_adjustments
            ]
            for advance in self.finances.find(
                Advance, employee_id=employee_id, kind="PERSONAL", state="RELEASED"
            ):
                if advance.start_on is None or advance.start_on > payroll.start_on:
                    continue
                _released, balance = self.balance(advance)
                repayment = min(advance.installment, balance, available)
                if repayment > ZERO:
                    lines.append(
                        {"kind": "REPAYMENT", "advance_id": str(advance.record_id), "amount": str(repayment)}
                    )
                    repayments += repayment
                    available -= repayment
            statements.append(
                PayStatement(
                    record_id=uuid5(payroll.record_id, str(employee_id)),
                    payroll_id=payroll.record_id,
                    employee_id=employee_id,
                    gross=gross,
                    deductions=deductions,
                    repayments=repayments,
                    net=available,
                    lines=lines,
                )
            )
        return statements

    def finalize_payroll(self, principal: Principal, identifier: UUID) -> Payroll:
        self.require(principal, "payroll.prepare")
        payroll = self.load(Payroll, identifier)
        if payroll.state != "DRAFT":
            raise reject("PAYROLL_NOT_DRAFT", "Only a draft payroll can be finalized.")
        if payroll.end_on >= manila_today():
            raise reject(
                "PAYROLL_PERIOD_OPEN", "Finalize after the period's last Manila business day has ended."
            )
        later = [
            entry
            for entry in self.finances.find(Payroll, state="FINALIZED")
            if entry.end_on >= payroll.start_on
        ]
        if later:
            raise reject(
                "PAYROLL_CHRONOLOGY",
                "A later period is already finalized; carry late earnings to the next open period.",
            )
        statements = self.preview(payroll)
        if not statements:
            raise reject(
                "NO_READY_EARNINGS", "There are no ready earnings or approved adjustments for this period."
            )
        self.independent(principal, *(statement.employee_id for statement in statements))
        for statement in statements:
            self.finances.save(statement)
            for line in statement.lines:
                if line["kind"] == "REPAYMENT":
                    self.finances.save(
                        AdvanceMovement(
                            advance_id=UUID(line["advance_id"]),
                            kind="REPAYMENT",
                            amount=Decimal(line["amount"]),
                            actor_id=principal.employee_id,
                            reference=f"Payroll {identifier}",
                            occurred_on=manila_today(),
                            payroll_id=identifier,
                        )
                    )
                elif line["kind"] == "EARNING":
                    earning = self.load(Earning, UUID(line["record_id"]))
                    self.finances.save(replace(earning, payroll_id=identifier))
                else:
                    adjustment = self.load(PayAdjustment, UUID(line["record_id"]))
                    self.finances.save(replace(adjustment, payroll_id=identifier))
        return self.finances.save(replace(payroll, state="FINALIZED", finalized_by=principal.employee_id))

    def reverse_payroll(self, principal: Principal, identifier: UUID, reason: str) -> Payroll:
        self.require(principal, "payroll.reverse")
        payroll = self.load(Payroll, identifier)
        self.independent(principal, payroll.finalized_by)
        if payroll.state != "FINALIZED":
            raise reject("PAYROLL_NOT_FINALIZED", "Only finalized payroll can be reversed.")
        statements = self.finances.find(PayStatement, payroll_id=identifier)
        self.independent(principal, *(statement.employee_id for statement in statements))
        if any(
            self.finances.find(FinancialPayment, statement_id=statement.record_id) for statement in statements
        ):
            raise reject(
                "PAYROLL_HAS_PAYMENTS",
                "Reconcile actual disbursements before reversal; payment evidence is retained.",
            )
        for repayment in self.finances.find(AdvanceMovement, payroll_id=identifier, kind="REPAYMENT"):
            self.finances.save(
                AdvanceMovement(
                    advance_id=repayment.advance_id,
                    kind="REVERSAL",
                    amount=repayment.amount,
                    actor_id=principal.employee_id,
                    reference=reason,
                    occurred_on=manila_today(),
                    payroll_id=identifier,
                    reverses_id=repayment.record_id,
                )
            )
        for earning in self.finances.find(Earning, payroll_id=identifier):
            self.finances.save(replace(earning, payroll_id=None))
        for adjustment in self.finances.find(PayAdjustment, payroll_id=identifier):
            self.finances.save(replace(adjustment, payroll_id=None))
        return self.finances.save(replace(payroll, state="REVERSED", reason=reason))

    def record_payment(
        self, principal: Principal, identifier: UUID, payload: PaymentRequest
    ) -> FinancialPayment:
        self.require(principal, "payroll_payment.record")
        statement = self.load(PayStatement, identifier)
        self.independent(principal, statement.employee_id)
        payroll = self.load(Payroll, statement.payroll_id)
        if payroll.state != "FINALIZED":
            raise reject("PAYROLL_NOT_FINALIZED", "Only finalized statements can be paid.")
        earnings = [
            entry
            for entry in self.finances.find(Earning, payroll_id=payroll.record_id)
            if entry.employee_id == statement.employee_id
        ]
        if any(entry.state == "HELD" or self.financial(entry.trip_id).held for entry in earnings):
            raise reject(
                "FINANCIAL_HOLD",
                "Resolve receipt/financial corrections before recording further payroll payments.",
            )
        paid = sum(
            (entry.allocated for entry in self.finances.find(FinancialPayment, statement_id=identifier)), ZERO
        )
        if payload.amount > statement.net - paid:
            raise reject("PAYROLL_OVERPAYMENT", "Payment exceeds the statement's unpaid balance.")
        self.require_past_date(payload.paid_on)
        return self.finances.save(
            FinancialPayment(
                statement_id=identifier,
                allocated=payload.amount,
                actor_id=principal.employee_id,
                **payload.model_dump(),
            )
        )
