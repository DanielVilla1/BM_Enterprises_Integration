# ===== AI GENERATED: FinanceQueryService =====
# Purpose: Role-scoped financial workspaces and exception reports.
# Inputs: Authenticated principal, section and bounded paging.
# Returns: Explicit response DTOs with commercial/payroll fields separately authorized.
# Flow: Restrict ownership first; project public DTOs; expose only authorized financial totals.

from decimal import Decimal
from uuid import UUID

from ..DTO.finance_dto import (
    AdjustmentResponse,
    AdvanceMovementResponse,
    AdvanceResponse,
    ChargeResponse,
    EarningResponse,
    ExpenseResponse,
    FinanceWorkspaceResponse,
    InvoiceLineResponse,
    InvoiceResponse,
    PaymentResponse,
    PayrollResponse,
    RateResponse,
    ReportFleetResponse,
    ReportMaintenanceResponse,
    ReportReplacementResponse,
    ReportsResponse,
    ReportTripResponse,
    StatementResponse,
    TripFinanceSummary,
)
from ..Entity.access import AccessLevel
from ..Entity.dispatch import Trip, TripStatus
from ..Entity.documents import OrDocument, OrDocumentKind
from ..Entity.employee import Principal
from ..Entity.finance import (
    ZERO,
    Advance,
    AdvanceDelegation,
    AdvanceMovement,
    Earning,
    ExpenseSheet,
    FinancialOperation,
    FinancialPayment,
    Invoice,
    InvoiceLine,
    PayAdjustment,
    Payroll,
    PayStatement,
    RateVersion,
    TripFinancial,
)
from ..Entity.finance_query import TripFinanceFacts
from .financial_workflow import FinancialWorkflow, reject
from .payroll_service import PayrollService


class FinanceQueryService(FinancialWorkflow):
    def _trip_facts(self, trips: list[Trip]) -> TripFinanceFacts:
        identifiers = [trip.trip_id for trip in trips]
        orders = {
            order.order_id: order for order in self.orders.get_many(list({trip.order_id for trip in trips}))
        }
        return TripFinanceFacts(
            orders=orders,
            financials={
                entry.trip_id: entry
                for entry in self.finances.find_many(TripFinancial, "trip_id", identifiers)
            },
            expenses={
                entry.trip_id: entry
                for entry in self.finances.find_many(ExpenseSheet, "trip_id", identifiers)
            },
            earned_trip_ids={
                entry.trip_id for entry in self.finances.find_many(Earning, "trip_id", identifiers)
            },
            documents=self.documents.list_active_for_trips(identifiers),
            allocated_trip_ids={
                entry.trip_id
                for entry in self.finances.find_many(InvoiceLine, "trip_id", identifiers)
                if entry.active
            },
            client_names=(
                {
                    client.client_id: client.name
                    for client in self.clients.get_many(list({order.client_id for order in orders.values()}))
                }
                if self.clients
                else {}
            ),
        )

    def _ready_from_facts(self, trip: Trip, facts: TripFinanceFacts) -> bool:
        return self.billing_ready_from_facts(
            trip,
            facts.financials.get(trip.trip_id, TripFinancial(trip_id=trip.trip_id)),
            any(
                document.kind is OrDocumentKind.SIGNED_OR
                for document in facts.documents.get(trip.trip_id, [])
            ),
            trip.trip_id in facts.allocated_trip_ids,
        )

    def presentation_document(
        self, principal: Principal, level: AccessLevel, document_id: UUID
    ) -> OrDocument:
        document = self.documents.get(document_id)
        if (
            not self.presentation_enabled
            or document is None
            or not document.storage_path.startswith("presentation/")
        ):
            raise reject("DOCUMENT_NOT_FOUND", "The document was not found.", 404)
        self.trip(document.trip_id, principal, level is AccessLevel.OWN)
        return document

    def advance_response(self, advance: Advance) -> AdvanceResponse:
        released, balance = self.balance(advance)
        return AdvanceResponse.model_validate(
            {
                **vars(advance),
                "state": (
                    "SETTLED"
                    if advance.kind == "PERSONAL" and released > ZERO and balance == ZERO
                    else advance.state
                ),
                "released": released,
                "balance": balance,
                "movements": [
                    AdvanceMovementResponse.model_validate(entry)
                    for entry in self.finances.find(AdvanceMovement, advance_id=advance.record_id)
                ],
            }
        )

    def statement_response(self, statement: PayStatement, payroll: Payroll) -> StatementResponse:
        payments = self.finances.find(FinancialPayment, statement_id=statement.record_id)
        paid = sum((entry.allocated for entry in payments), ZERO)
        advances = self.finances.find(Advance, employee_id=statement.employee_id, kind="PERSONAL")
        earnings = [
            entry
            for entry in self.finances.find(Earning, payroll_id=payroll.record_id)
            if entry.employee_id == statement.employee_id
        ]
        held = any(entry.state == "HELD" or self.financial(entry.trip_id).held for entry in earnings)
        return StatementResponse.model_validate(
            {
                **vars(statement),
                "paid": paid,
                "unpaid": statement.net - paid,
                "remaining_advance": sum((self.balance(advance)[1] for advance in advances), ZERO),
                "held": held,
            }
        )

    def invoice_response(self, invoice: Invoice) -> InvoiceResponse:
        payments = self.finances.find(FinancialPayment, invoice_id=invoice.record_id)
        paid = sum((entry.allocated for entry in payments), ZERO)
        return InvoiceResponse.model_validate(
            {
                **vars(invoice),
                "paid": paid,
                "outstanding": invoice.total - paid,
                "unallocated_credit": sum((entry.amount - entry.allocated for entry in payments), ZERO),
                "lines": [
                    InvoiceLineResponse.model_validate(line)
                    for line in self.finances.find(InvoiceLine, invoice_id=invoice.record_id)
                ],
            }
        )

    def workspace(
        self, principal: Principal, section: str, limit: int, offset: int, payroll_service: PayrollService
    ) -> FinanceWorkspaceResponse:
        capability = {
            "expenses": "expense.view",
            "payroll": "payroll.view",
            "advances": "cash_advance.view",
            "billing": "billing.manage",
        }[section]
        level = self.require(principal, capability, full=False)
        own = level is AccessLevel.OWN
        result = FinanceWorkspaceResponse(
            limit=limit, offset=offset, deductions_enabled=self.deductions_enabled
        )
        result.presentation_data = bool(self.finances.find(FinancialOperation, key="presentation-seed-v1"))
        commercial = self.authorization.level_for(principal, "client_rate.view") is not None
        if not own:
            result.people = [
                {"record_id": str(employee.employee_id), "name": employee.full_name}
                for employee in self.employees.list_directory()
            ]
        else:
            result.people = [{"record_id": str(principal.employee_id), "name": principal.full_name}]
        if section in ("expenses", "billing", "payroll", "advances"):
            trip_page = (
                self.trips.list_assigned(principal.employee_id, limit + 1, offset, None)
                if own
                else self.trips.list_page(limit + 1, offset, None, None, None)
            )
            result.has_more = len(trip_page) > limit
            facts = self._trip_facts(trip_page[:limit])
            for trip in trip_page[:limit]:
                order = facts.orders.get(trip.order_id)
                if order is None:
                    continue
                financial = facts.financials.get(trip.trip_id, TripFinancial(trip_id=trip.trip_id))
                sheets = [facts.expenses[trip.trip_id]] if trip.trip_id in facts.expenses else []
                earnings = trip.trip_id in facts.earned_trip_ids
                result.trips.append(
                    TripFinanceSummary(
                        trip_id=trip.trip_id,
                        client_id=order.client_id,
                        client_name=facts.client_names.get(order.client_id, ""),
                        driver_id=trip.driver_id,
                        helper_ids=list(trip.helper_ids),
                        status=trip.status.value,
                        scheduled_date=order.scheduled_date,
                        expense_state=sheets[0].state if sheets else "MISSING",
                        earnings_state=(
                            "HELD" if financial.held else "CALCULATED" if earnings else "PENDING_CALCULATION"
                        ),
                        billing_state=(
                            ("READY" if self._ready_from_facts(trip, facts) else "PENDING_OR_BILLED")
                            if commercial
                            else None
                        ),
                        charge=financial.charge if commercial else None,
                    )
                )
                if section == "expenses" and sheets:
                    result.expenses.append(ExpenseResponse.model_validate(sheets[0]))
                if section in ("expenses", "billing") and commercial and trip.trip_id in facts.financials:
                    result.charges.append(ChargeResponse.model_validate(financial))
            if commercial:
                result.rates = [
                    RateResponse.model_validate(entry) for entry in self.finances.find(RateVersion)
                ]
        if section == "billing":
            invoices = self.finances.find(Invoice)
            result.invoices = [self.invoice_response(entry) for entry in invoices[offset : offset + limit]]
            result.has_more |= len(invoices) > offset + limit
            result.payments = [
                PaymentResponse.model_validate(payment)
                for invoice in result.invoices
                for payment in self.finances.find(FinancialPayment, invoice_id=invoice.record_id)
            ]
        if section == "advances":
            if self.authorization.level_for(principal, "cash_advance.approve"):
                result.delegations = [
                    {
                        "record_id": str(entry.record_id),
                        "employee_id": str(entry.employee_id),
                        "expires_on": entry.expires_on.isoformat(),
                        "reason": entry.reason,
                        "revoked": str(entry.revoked).lower(),
                    }
                    for entry in self.finances.find(AdvanceDelegation)
                ]
            advances = self.finances.find(Advance, **({"employee_id": principal.employee_id} if own else {}))
            result.advances = [self.advance_response(entry) for entry in advances[offset : offset + limit]]
            result.has_more |= len(advances) > offset + limit
        if section == "payroll":
            payrolls = self.finances.find(Payroll)
            result.payrolls = [
                PayrollResponse.model_validate(entry) for entry in payrolls[offset : offset + limit]
            ]
            result.has_more |= len(payrolls) > offset + limit
            earnings = self.finances.find(Earning, **({"employee_id": principal.employee_id} if own else {}))
            result.earnings = [
                EarningResponse.model_validate(entry) for entry in earnings[offset : offset + limit]
            ]
            result.has_more |= len(earnings) > offset + limit
            adjustments = self.finances.find(
                PayAdjustment, **({"employee_id": principal.employee_id} if own else {})
            )
            result.adjustments = [
                AdjustmentResponse.model_validate(entry) for entry in adjustments[offset : offset + limit]
            ]
            for payroll in payrolls[offset : offset + limit]:
                statements = (
                    payroll_service.preview(payroll)
                    if payroll.state == "DRAFT"
                    else self.finances.find(PayStatement, payroll_id=payroll.record_id)
                )
                result.statements.extend(
                    self.statement_response(statement, payroll)
                    for statement in statements
                    if not own or statement.employee_id == principal.employee_id
                )
            statement_ids = {statement.record_id for statement in result.statements}
            result.payments = [
                PaymentResponse.model_validate(entry)
                for entry in self.finances.find(FinancialPayment)
                if entry.statement_id in statement_ids
            ]
        return result

    def reports(self, principal: Principal, level: AccessLevel, limit: int, offset: int) -> ReportsResponse:
        # FULL report permission does not confer commercial or employee-pay access.
        own = level is AccessLevel.OWN
        trips = (
            self.trips.list_assigned(principal.employee_id, limit + 1, offset, None)
            if own
            else self.trips.list_page(limit + 1, offset, None, None, None)
        )
        result: list[ReportTripResponse] = []
        facts = self._trip_facts(trips[:limit])
        capabilities = self.authorization.capability_levels(principal)
        replacements: list[ReportReplacementResponse] = []
        fleet: list[ReportFleetResponse] = []
        fleet_access = "truck.manage" in capabilities
        if fleet_access:
            replacements = [
                ReportReplacementResponse.model_validate(entry)
                for entry in self.trips.list_replacements_for_trips([trip.trip_id for trip in trips[:limit]])
            ]
        totals: dict[str, int] = {}
        for trip in trips[:limit]:
            order = facts.orders.get(trip.order_id)
            if order is None:
                continue
            documents = facts.documents.get(trip.trip_id, [])
            stamped = any(entry.kind is OrDocumentKind.STAMPED_COPY for entry in documents)
            financial = facts.financials.get(trip.trip_id, TripFinancial(trip_id=trip.trip_id))
            flags: list[str] = []
            if trip.status is TripStatus.OR_UPLOADED:
                flags.append("OR_AWAITING_RECEIPT")
                flags.append("ASSIGNABLE_DISPATCH_BLOCKED")
            if trip.status is TripStatus.COMPLETED and not stamped:
                flags.append("COMPLETED_WITHOUT_STAMPED_COPY")
            if financial.held:
                flags.append("FINANCIAL_HOLD")
            if trip.status is TripStatus.COMPLETED:
                sheets = [facts.expenses[trip.trip_id]] if trip.trip_id in facts.expenses else []
                if not sheets or sheets[0].state not in ("FINALIZED", "CONFIRMED_ZERO"):
                    flags.append("EXPENSES_NOT_FINALIZED")
                if sheets and sheets[0].state == "AWAITING_REVIEW":
                    flags.append("EXPENSES_AWAITING_REVIEW")
                if trip.trip_id not in facts.earned_trip_ids:
                    flags.append("PAYROLL_PENDING_CALCULATION")
                if "billing.manage" in capabilities and self._ready_from_facts(trip, facts):
                    flags.append("READY_UNBILLED_CARRYOVER")
            for flag in flags:
                totals[flag] = totals.get(flag, 0) + 1
            totals[trip.status.value] = totals.get(trip.status.value, 0) + 1
            result.append(
                ReportTripResponse(
                    trip_id=trip.trip_id,
                    status=trip.status.value,
                    scheduled_date=order.scheduled_date,
                    truck_id=trip.truck_id,
                    driver_id=trip.driver_id,
                    helper_ids=list(trip.helper_ids),
                    flags=flags,
                )
            )
        financial_totals: dict[str, Decimal] = {}
        report_invoices: list[InvoiceResponse] = []
        report_statements: list[StatementResponse] = []
        report_advances: list[AdvanceResponse] = []
        if "client_rate.view" in capabilities:
            invoices = [entry for entry in self.finances.find(Invoice) if entry.state != "VOID"]
            financial_totals["invoiced"] = sum((entry.total for entry in invoices if entry.issued_on), ZERO)
            report_invoices = [self.invoice_response(entry) for entry in invoices[offset : offset + limit]]
            financial_totals["outstanding_client_payments"] = sum(
                (self.invoice_response(entry).outstanding for entry in invoices if entry.issued_on), ZERO
            )
            financial_totals["collections"] = sum(
                (entry.allocated for entry in self.finances.find(FinancialPayment) if entry.invoice_id), ZERO
            )
            financial_totals["unallocated_credit"] = sum(
                (
                    entry.amount - entry.allocated
                    for entry in self.finances.find(FinancialPayment)
                    if entry.invoice_id
                ),
                ZERO,
            )
        payroll_access = capabilities.get("payroll.view")
        if payroll_access:
            earnings = self.finances.find(
                Earning,
                **({"employee_id": principal.employee_id} if payroll_access is AccessLevel.OWN else {}),
            )
            financial_totals["earnings_ready"] = sum(
                (entry.amount for entry in earnings if entry.state == "READY" and entry.payroll_id is None),
                ZERO,
            )
            advances = self.finances.find(
                Advance,
                kind="PERSONAL",
                **({"employee_id": principal.employee_id} if payroll_access is AccessLevel.OWN else {}),
            )
            financial_totals["personal_advance_balance"] = sum(
                (self.balance(entry)[1] for entry in advances), ZERO
            )
            approved_payrolls = {
                entry.record_id: entry for entry in self.finances.find(Payroll, state="FINALIZED")
            }
            statements = [
                entry
                for entry in self.finances.find(
                    PayStatement,
                    **({"employee_id": principal.employee_id} if payroll_access is AccessLevel.OWN else {}),
                )
                if entry.payroll_id in approved_payrolls
            ]
            all_statement_responses = [
                self.statement_response(entry, approved_payrolls[entry.payroll_id]) for entry in statements
            ]
            report_statements = all_statement_responses[offset : offset + limit]
            financial_totals["gross_payroll"] = sum((entry.gross for entry in statements), ZERO)
            financial_totals["payroll_deductions"] = sum((entry.deductions for entry in statements), ZERO)
            financial_totals["net_payroll"] = sum((entry.net for entry in statements), ZERO)
            financial_totals["unpaid_employee_balances"] = sum(
                (entry.unpaid for entry in all_statement_responses), ZERO
            )
        advance_access = capabilities.get("cash_advance.view")
        if advance_access:
            advances = self.finances.find(
                Advance,
                **({"employee_id": principal.employee_id} if advance_access is AccessLevel.OWN else {}),
            )
            report_advances = [self.advance_response(entry) for entry in advances[offset : offset + limit]]
            financial_totals["unreconciled_operating_funds"] = sum(
                (
                    self.balance(entry)[1]
                    for entry in advances
                    if entry.kind == "OPERATING" and entry.state in ("RELEASED", "REVIEW_REQUIRED")
                ),
                ZERO,
            )
        if fleet_access and self.trucks:
            truck_page = self.trucks.list_page(limit, offset, None, None)
            maintenance = self.trucks.list_maintenance_for_trucks([truck.truck_id for truck in truck_page])
            for truck in truck_page:
                fleet.append(
                    ReportFleetResponse(
                        truck_id=truck.truck_id,
                        plate_number=truck.plate_number,
                        status=truck.status.value,
                        maintenance=[
                            ReportMaintenanceResponse.model_validate(entry)
                            for entry in maintenance
                            if entry.truck_id == truck.truck_id
                        ],
                    )
                )
        return ReportsResponse(
            people=(
                [
                    {"record_id": str(employee.employee_id), "name": employee.full_name}
                    for employee in self.employees.list_directory()
                ]
                if not own
                else [{"record_id": str(principal.employee_id), "name": principal.full_name}]
            ),
            fleet=fleet,
            replacements=replacements,
            presentation_data=bool(self.finances.find(FinancialOperation, key="presentation-seed-v1")),
            trips=result,
            totals=totals,
            financial_totals=financial_totals,
            advances=report_advances,
            statements=report_statements,
            invoices=report_invoices,
            limit=limit,
            offset=offset,
            has_more=len(trips) > limit,
        )
