# ===== AI GENERATED: BillingService =====
# Purpose: Eligible carry-over batches, immutable issued invoices and collections.
# Inputs: Accounting selections and independently approved void requests.
# Returns: Invoice allocations and exact payment/credit records.
# Flow: Validate each charge; allocate once; revalidate issue; preserve payment evidence.

from dataclasses import replace
from datetime import timedelta
from uuid import UUID

from ..DTO.finance_dto import InvoiceRequest, PaymentRequest
from ..Entity.clock import manila_today
from ..Entity.employee import Principal
from ..Entity.finance import ZERO, FinancialPayment, Invoice, InvoiceLine
from .financial_workflow import FinancialWorkflow, business_date, reject


class BillingService(FinancialWorkflow):
    def create_invoice(self, principal: Principal, payload: InvoiceRequest) -> Invoice:
        self.require(principal, "billing.manage")
        self.require_past_date(payload.cutoff)
        if len(set(payload.trip_ids)) != len(payload.trip_ids):
            raise reject("DUPLICATE_BILLING_TRIP", "Select each trip only once.")
        lines: list[InvoiceLine] = []
        invoice = Invoice(
            client_id=payload.client_id,
            cutoff=payload.cutoff,
            entered_by=principal.employee_id,
            total=ZERO,
            terms_days=payload.terms_days,
        )
        for trip_id in sorted(payload.trip_ids, key=str):
            trip = self.trip(trip_id)
            order = self.orders.get_by_id(trip.order_id)
            if order is None or order.client_id != payload.client_id or not self.billing_ready(trip):
                raise reject(
                    "TRIP_NOT_BILLABLE",
                    "Every trip must be ready, unbilled and belong to the selected client.",
                )
            if not trip.delivered_at or business_date(trip.delivered_at) > payload.cutoff:
                raise reject(
                    "TRIP_AFTER_CUTOFF", "The trip's actual delivery date falls after this batch cutoff."
                )
            charge = self.financial(trip_id).charge
            if charge is None:
                raise reject("CHARGE_REQUIRED", "A finalized positive charge is required.")
            lines.append(
                InvoiceLine(
                    invoice_id=invoice.record_id,
                    trip_id=trip_id,
                    amount=charge,
                    delivered_on=business_date(trip.delivered_at),
                )
            )
        invoice = self.finances.save(replace(invoice, total=sum((line.amount for line in lines), ZERO)))
        for line in lines:
            self.finances.save(line)
        return invoice

    def issue_invoice(self, principal: Principal, identifier: UUID) -> Invoice:
        self.require(principal, "billing.manage")
        invoice = self.load(Invoice, identifier)
        if invoice.state != "DRAFT" or invoice.held:
            raise reject("INVOICE_NOT_ISSUABLE", "Only a draft without financial holds can be issued.")
        lines = self.finances.find(InvoiceLine, invoice_id=identifier, active=True)
        if not lines or any(
            not self.billing_ready(self.trip(line.trip_id), allow_allocated=True) for line in lines
        ):
            raise reject(
                "INVOICE_LINES_NOT_READY",
                "A trip's receipt or financial readiness has changed; review the batch.",
            )
        today = manila_today()
        return self.finances.save(
            replace(
                invoice, state="ISSUED", issued_on=today, due_on=today + timedelta(days=invoice.terms_days)
            )
        )

    def request_void(self, principal: Principal, identifier: UUID, reason: str) -> Invoice:
        self.require(principal, "billing.manage")
        invoice = self.load(Invoice, identifier)
        if invoice.state not in ("DRAFT", "ISSUED"):
            raise reject("INVOICE_VOID_STATE", "This invoice is already void or awaiting approval.")
        return self.finances.save(
            replace(invoice, state="VOID_REQUESTED", reason=reason, void_requested_by=principal.employee_id)
        )

    def approve_void(self, principal: Principal, identifier: UUID) -> Invoice:
        self.require(principal, "invoice.void_approve")
        invoice = self.load(Invoice, identifier)
        self.independent(principal, invoice.void_requested_by)
        if invoice.state != "VOID_REQUESTED":
            raise reject("INVOICE_VOID_NOT_REQUESTED", "Accounting must request the void first.")
        if self.finances.find(FinancialPayment, invoice_id=identifier):
            raise reject(
                "INVOICE_HAS_COLLECTIONS",
                "Reconcile collections/credits before voiding. Paid charges cannot be rebilled.",
            )
        for line in self.finances.find(InvoiceLine, invoice_id=identifier, active=True):
            self.finances.save(replace(line, active=False))
        return self.finances.save(replace(invoice, state="VOID"))

    def record_collection(
        self, principal: Principal, identifier: UUID, payload: PaymentRequest
    ) -> FinancialPayment:
        self.require(principal, "billing.manage")
        invoice = self.load(Invoice, identifier)
        if invoice.state != "ISSUED" or invoice.held:
            raise reject(
                "INVOICE_NOT_COLLECTIBLE", "Only an issued invoice without holds accepts collections."
            )
        self.require_past_date(payload.paid_on)
        paid = sum(
            (entry.allocated for entry in self.finances.find(FinancialPayment, invoice_id=identifier)), ZERO
        )
        allocation = min(payload.amount, invoice.total - paid)
        return self.finances.save(
            FinancialPayment(
                invoice_id=identifier,
                allocated=allocation,
                actor_id=principal.employee_id,
                **payload.model_dump(),
            )
        )
