# ===== AI GENERATED: AdvanceService =====
# Purpose: Personal and operating advance approval, release and reconciliation.
# Inputs: Independently authorized requests and actual movement references.
# Returns: Advance and append-only movement records.
# Flow: Approval creates no debt; release creates principal; operating funds never become personal debt.

from dataclasses import replace
from uuid import UUID

from ..DTO.finance_dto import AdvanceApprovalRequest, AdvanceRequest, DelegationRequest, MovementRequest
from ..Entity.access import AccessLevel
from ..Entity.clock import manila_today
from ..Entity.employee import Principal
from ..Entity.finance import Advance, AdvanceDelegation, AdvanceMovement, ExpenseSheet
from .financial_workflow import FinancialWorkflow, reject


class AdvanceService(FinancialWorkflow):
    def request_advance(self, principal: Principal, payload: AdvanceRequest) -> Advance:
        level = self.require(principal, "cash_advance.request", full=False)
        if level is AccessLevel.OWN and payload.employee_id != principal.employee_id:
            raise reject("PERMISSION_DENIED", "You can only request your own advance.", 403)
        self.employee(payload.employee_id)
        if payload.kind == "OPERATING":
            self.require(principal, "cash_advance.release_repay")
            if payload.trip_id is None:
                raise reject("OPERATING_TRIP_REQUIRED", "Operating funds must be linked to a trip.")
            trip = self.trip(payload.trip_id)
            if payload.employee_id not in (trip.driver_id, *trip.helper_ids):
                raise reject("OPERATING_CUSTODIAN_INVALID", "Choose a crew member assigned to that trip.")
        elif payload.trip_id is not None:
            raise reject(
                "PERSONAL_ADVANCE_TRIP", "A personal advance cannot be recorded as trip operating funds."
            )
        return self.finances.save(Advance(**payload.model_dump(), requested_by=principal.employee_id))

    def approve_advance(
        self, principal: Principal, identifier: UUID, payload: AdvanceApprovalRequest
    ) -> Advance:
        # Owner or an explicitly delegated, unexpired HR approver; neither may approve themselves.
        if self.authorization.level_for(principal, "cash_advance.approve") is None:
            self.require(principal, "cash_advance.delegated_approve")
            delegations = self.finances.find(
                AdvanceDelegation, employee_id=principal.employee_id, revoked=False
            )
            if not any(delegation.expires_on >= manila_today() for delegation in delegations):
                raise reject("ADVANCE_DELEGATION_REQUIRED", "An active Owner delegation is required.", 403)
        advance = self.load(Advance, identifier)
        self.independent(principal, advance.requested_by, advance.employee_id)
        if advance.state != "REQUESTED":
            raise reject("ADVANCE_NOT_PENDING", "This request has already been reviewed.")
        if payload.amount > advance.amount or payload.installment > payload.amount:
            raise reject(
                "ADVANCE_LIMIT",
                "Approval cannot exceed the request, and installments cannot exceed approval.",
            )
        if payload.start_on.day not in (1, 16):
            raise reject("INVALID_REPAYMENT_PERIOD", "Repayments must start on the 1st or 16th.")
        return self.finances.save(
            replace(
                advance,
                state="APPROVED",
                approved_by=principal.employee_id,
                amount=payload.amount,
                installment=payload.installment if advance.kind == "PERSONAL" else advance.installment,
                start_on=payload.start_on,
                acknowledgment=payload.acknowledgment,
            )
        )

    def release_advance(
        self, principal: Principal, identifier: UUID, payload: MovementRequest
    ) -> AdvanceMovement:
        self.require(principal, "cash_advance.release_repay")
        advance = self.load(Advance, identifier)
        self.independent(principal, advance.approved_by, advance.employee_id)
        if advance.state not in ("APPROVED", "RELEASED") or not advance.acknowledgment:
            raise reject(
                "ADVANCE_NOT_APPROVED",
                "Independently approve and acknowledge the arrangement before release.",
            )
        self.require_past_date(payload.occurred_on)
        released, _balance = self.balance(advance)
        if released + payload.amount > advance.amount:
            raise reject("ADVANCE_OVER_RELEASE", "Actual releases cannot exceed the approved principal.")
        self.finances.save(replace(advance, state="RELEASED"))
        return self.finances.save(
            AdvanceMovement(
                advance_id=identifier,
                kind="RELEASE",
                actor_id=principal.employee_id,
                **payload.model_dump(),
            )
        )

    def return_operating_funds(
        self, principal: Principal, identifier: UUID, payload: MovementRequest
    ) -> AdvanceMovement:
        self.require(principal, "cash_advance.release_repay")
        advance = self.load(Advance, identifier)
        if advance.kind != "OPERATING" or advance.state != "RELEASED":
            raise reject(
                "NOT_OPERATING_FUNDS", "Only released operating funds can have an unused-funds return."
            )
        self.require_past_date(payload.occurred_on)
        _released, balance = self.balance(advance)
        if payload.amount > balance:
            raise reject("RETURN_EXCEEDS_RELEASE", "The return exceeds outstanding operating funds.")
        return self.finances.save(
            AdvanceMovement(
                advance_id=identifier,
                kind="RETURN",
                actor_id=principal.employee_id,
                **payload.model_dump(),
            )
        )

    def reconcile_operating(self, principal: Principal, identifier: UUID) -> Advance:
        self.require(principal, "cash_advance.approve")
        advance = self.load(Advance, identifier)
        self.independent(principal, advance.requested_by, advance.employee_id)
        releases = self.finances.find(AdvanceMovement, advance_id=identifier, kind="RELEASE")
        self.independent(principal, *(entry.actor_id for entry in releases))
        if advance.kind != "OPERATING" or advance.state not in ("RELEASED", "REVIEW_REQUIRED"):
            raise reject(
                "NOT_OPERATING_FUNDS", "Select released operating funds for independent reconciliation."
            )
        sheets = self.finances.find(ExpenseSheet, trip_id=advance.trip_id)
        if not sheets or sheets[0].state not in ("FINALIZED", "CONFIRMED_ZERO"):
            raise reject("EXPENSE_REVIEW_REQUIRED", "Review the trip's actual purchases first.")
        others = [
            entry
            for entry in self.finances.find(Advance, trip_id=advance.trip_id, kind="OPERATING")
            if entry.record_id != identifier and entry.state != "REQUESTED"
        ]
        if others:
            raise reject(
                "OPERATING_RECONCILIATION_REVIEW",
                "Multiple funding arrangements need a reviewed allocation of purchases.",
            )
        _released, balance = self.balance(advance)
        state = "RECONCILED" if balance == sheets[0].total else "REVIEW_REQUIRED"
        return self.finances.save(replace(advance, state=state))

    def delegate_approver(self, principal: Principal, payload: DelegationRequest) -> AdvanceDelegation:
        self.require(principal, "cash_advance.approve")
        self.employee(payload.employee_id)
        if payload.expires_on < manila_today():
            raise reject("DELEGATION_EXPIRED", "Choose a current or future delegation expiry.")
        return self.finances.save(
            AdvanceDelegation(**payload.model_dump(), delegated_by=principal.employee_id)
        )

    def revoke_delegation(self, principal: Principal, identifier: UUID) -> AdvanceDelegation:
        self.require(principal, "cash_advance.approve")
        return self.finances.save(replace(self.load(AdvanceDelegation, identifier), revoked=True))
