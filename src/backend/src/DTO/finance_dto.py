# ===== AI GENERATED: financial_contract =====
# Purpose: Strict finance commands and explicit public response fields.
# Inputs: JSON decimal strings; extra fields are rejected.
# Returns: Validated requests and serialized peso strings, never binary floats.
# Flow: Validate money at the boundary; expose only the fields each workflow needs.

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, StringConstraints


def require_decimal_string(value: object) -> object:
    """Do not allow JSON floats to round before entering the money ledger."""
    if not isinstance(value, str):
        raise ValueError("Send money and percentages as decimal strings.")
    return value


MoneyInput = Annotated[
    Decimal,
    BeforeValidator(require_decimal_string),
    Field(gt=0, le=9999999999, max_digits=12, decimal_places=2),
]
PercentageInput = Annotated[
    Decimal, BeforeValidator(require_decimal_string), Field(gt=0, le=100, max_digits=7, decimal_places=4)
]
Reason = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=1000)]
Reference = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)]


class CommandRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ReasonRequest(CommandRequest):
    reason: Reason


class ExpenseLineRequest(CommandRequest):
    category: Literal["FUEL", "TOLL"]
    amount: MoneyInput
    description: Reason
    incurred_on: date
    evidence: Reference


class ExpenseRequest(CommandRequest):
    lines: list[ExpenseLineRequest] = Field(default_factory=list, max_length=100)
    declared_zero: bool = False
    reason: Reason


class ReviewRequest(CommandRequest):
    approved: bool
    reason: Reason


class ChargeRequest(CommandRequest):
    amount: MoneyInput
    agreed_amount: MoneyInput
    reference: Reference
    reason: Reason


class RateRequest(CommandRequest):
    effective_on: date
    driver_one: PercentageInput
    helper_one: PercentageInput
    driver_two: PercentageInput
    helper_two: PercentageInput
    reference: Reference


class AdvanceRequest(CommandRequest):
    employee_id: UUID
    amount: MoneyInput
    kind: Literal["PERSONAL", "OPERATING"] = "PERSONAL"
    trip_id: UUID | None = None
    reason: Reason


class AdvanceApprovalRequest(CommandRequest):
    amount: MoneyInput
    installment: MoneyInput
    start_on: date
    acknowledgment: Reference
    reason: Reason


class MovementRequest(CommandRequest):
    amount: MoneyInput
    occurred_on: date
    reference: Reference


class DelegationRequest(CommandRequest):
    employee_id: UUID
    expires_on: date
    reason: Reason


class AdjustmentRequest(CommandRequest):
    employee_id: UUID
    amount: MoneyInput
    kind: Literal["VOLUNTARY", "OVERPAYMENT", "CREDIT", "DEBIT"]
    period_start: date
    reason: Reason
    authorization: Reference


class PayrollRequest(CommandRequest):
    start_on: date


class InvoiceRequest(CommandRequest):
    client_id: UUID
    cutoff: date
    trip_ids: list[UUID] = Field(min_length=1, max_length=100)
    terms_days: int = Field(default=30, ge=0, le=365)


class PaymentRequest(CommandRequest):
    amount: MoneyInput
    paid_on: date
    method: Reference
    reference: Reference


class RecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    record_id: UUID
    created_at: datetime


class ExpenseResponse(RecordResponse):
    trip_id: UUID
    entered_by: UUID
    state: str
    lines: list[dict[str, str]]
    declared_zero: bool
    reason: str
    reviewed_by: UUID | None
    contributors: list[str]
    total: Decimal


class RateResponse(RecordResponse):
    effective_on: date
    driver_one: Decimal
    helper_one: Decimal
    driver_two: Decimal
    helper_two: Decimal
    reference: str


class ChargeResponse(RecordResponse):
    trip_id: UUID
    charge: Decimal | None
    agreed_amount: Decimal | None
    reference: str
    charge_state: str
    entered_by: UUID | None
    finalized_by: UUID | None
    reason: str
    held: bool
    hold_reason: str


class EarningResponse(RecordResponse):
    trip_id: UUID
    employee_id: UUID
    rate_id: UUID
    percentage: Decimal
    base: Decimal
    amount: Decimal
    original_date: date
    rounding_variance: Decimal
    state: str
    payroll_id: UUID | None


class AdvanceMovementResponse(RecordResponse):
    advance_id: UUID
    kind: str
    amount: Decimal
    actor_id: UUID
    reference: str
    occurred_on: date
    payroll_id: UUID | None
    reverses_id: UUID | None


class AdvanceResponse(RecordResponse):
    employee_id: UUID
    requested_by: UUID
    amount: Decimal
    reason: str
    kind: str
    trip_id: UUID | None
    state: str
    approved_by: UUID | None
    installment: Decimal
    start_on: date | None
    acknowledgment: str
    released: Decimal
    balance: Decimal
    movements: list[AdvanceMovementResponse]


class AdjustmentResponse(RecordResponse):
    employee_id: UUID
    entered_by: UUID
    amount: Decimal
    kind: str
    period_start: date
    reason: str
    authorization: str
    state: str
    approved_by: UUID | None
    payroll_id: UUID | None


class StatementResponse(RecordResponse):
    payroll_id: UUID
    employee_id: UUID
    gross: Decimal
    deductions: Decimal
    repayments: Decimal
    net: Decimal
    lines: list[dict[str, str]]
    paid: Decimal
    unpaid: Decimal
    remaining_advance: Decimal
    held: bool


class PayrollResponse(RecordResponse):
    start_on: date
    end_on: date
    prepared_by: UUID
    state: str
    finalized_by: UUID | None
    reason: str


class InvoiceLineResponse(RecordResponse):
    invoice_id: UUID
    trip_id: UUID
    amount: Decimal
    delivered_on: date
    active: bool


class InvoiceResponse(RecordResponse):
    client_id: UUID
    cutoff: date
    entered_by: UUID
    total: Decimal
    terms_days: int
    state: str
    issued_on: date | None
    due_on: date | None
    void_requested_by: UUID | None
    reason: str
    held: bool
    paid: Decimal
    outstanding: Decimal
    unallocated_credit: Decimal
    lines: list[InvoiceLineResponse]


class PaymentResponse(RecordResponse):
    amount: Decimal
    allocated: Decimal
    paid_on: date
    method: str
    reference: str
    actor_id: UUID
    statement_id: UUID | None
    invoice_id: UUID | None


class TripFinanceSummary(BaseModel):
    trip_id: UUID
    client_id: UUID
    client_name: str = ""
    driver_id: UUID
    helper_ids: list[UUID]
    status: str
    scheduled_date: date
    expense_state: str
    earnings_state: str
    billing_state: str | None = None
    charge: Decimal | None = None


class FinanceWorkspaceResponse(BaseModel):
    presentation_data: bool = False
    people: list[dict[str, str]] = Field(default_factory=list)
    delegations: list[dict[str, str]] = Field(default_factory=list)
    expenses: list[ExpenseResponse] = Field(default_factory=list)
    trips: list[TripFinanceSummary] = Field(default_factory=list)
    charges: list[ChargeResponse] = Field(default_factory=list)
    rates: list[RateResponse] = Field(default_factory=list)
    earnings: list[EarningResponse] = Field(default_factory=list)
    advances: list[AdvanceResponse] = Field(default_factory=list)
    adjustments: list[AdjustmentResponse] = Field(default_factory=list)
    payrolls: list[PayrollResponse] = Field(default_factory=list)
    statements: list[StatementResponse] = Field(default_factory=list)
    invoices: list[InvoiceResponse] = Field(default_factory=list)
    payments: list[PaymentResponse] = Field(default_factory=list)
    deductions_enabled: bool = False
    limit: int = 50
    offset: int = 0
    has_more: bool = False


class CommandResponse(BaseModel):
    record_id: UUID
    state: str
    detail: str = "Saved."


class ReportTripResponse(BaseModel):
    trip_id: UUID
    status: str
    scheduled_date: date
    truck_id: UUID
    driver_id: UUID
    helper_ids: list[UUID] = Field(default_factory=list)
    flags: list[str]


class ReportMaintenanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    record_id: UUID
    truck_id: UUID
    reason: str
    started_at: datetime
    ended_at: datetime | None


class ReportFleetResponse(BaseModel):
    truck_id: UUID
    plate_number: str
    status: str
    maintenance: list[ReportMaintenanceResponse]


class ReportReplacementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    replacement_id: UUID
    trip_id: UUID
    original_truck_id: UUID
    replacement_truck_id: UUID
    reason: str
    effective_at: datetime


class ReportsResponse(BaseModel):
    presentation_data: bool = False
    people: list[dict[str, str]] = Field(default_factory=list)
    fleet: list[ReportFleetResponse] = Field(default_factory=list)
    replacements: list[ReportReplacementResponse] = Field(default_factory=list)
    trips: list[ReportTripResponse]
    totals: dict[str, int]
    financial_totals: dict[str, Decimal]
    advances: list[AdvanceResponse] = Field(default_factory=list)
    statements: list[StatementResponse] = Field(default_factory=list)
    invoices: list[InvoiceResponse] = Field(default_factory=list)
    limit: int
    offset: int
    has_more: bool
