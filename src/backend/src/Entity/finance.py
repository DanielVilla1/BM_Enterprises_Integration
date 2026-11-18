# ===== AI GENERATED: financial_entities =====
# Purpose: Persistence-independent financial records and exact peso calculations.
# Inputs: Validated amounts, immutable rate versions and workflow records.
# Returns: Typed records, rounded money and Manila payroll periods.
# Flow: Keep each ledger separate; retain original dates and historical snapshots.

from calendar import monthrange
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID, uuid4

CENTAVO = Decimal("0.01")
ZERO = Decimal("0.00")


def money(amount: Decimal) -> Decimal:
    """Round each employee or ledger amount independently, half up."""
    return amount.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def payroll_period(moment: date) -> tuple[date, date]:
    """The inclusive semi-monthly period containing a Manila business date."""
    last_day = 15 if moment.day <= 15 else monthrange(moment.year, moment.month)[1]
    return moment.replace(day=1 if moment.day <= 15 else 16), moment.replace(day=last_day)


@dataclass(frozen=True, kw_only=True)
class FinancialRecord:
    record_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, kw_only=True)
class ExpenseSheet(FinancialRecord):
    trip_id: UUID
    entered_by: UUID
    state: str = "ENTERING"
    lines: list[dict[str, str]] = field(default_factory=list)
    declared_zero: bool = False
    reason: str = ""
    reviewed_by: UUID | None = None
    contributors: list[str] = field(default_factory=list)
    total: Decimal = ZERO


@dataclass(frozen=True, kw_only=True)
class RateVersion(FinancialRecord):
    effective_on: date
    driver_one: Decimal = Decimal("8")
    helper_one: Decimal = Decimal("4")
    driver_two: Decimal = Decimal("6")
    helper_two: Decimal = Decimal("3")
    reference: str = "Initial D6 policy"
    entered_by: UUID | None = None


@dataclass(frozen=True, kw_only=True)
class TripFinancial(FinancialRecord):
    trip_id: UUID
    rate_id: UUID | None = None
    charge: Decimal | None = None
    agreed_amount: Decimal | None = None
    reference: str = ""
    charge_state: str = "MISSING"
    entered_by: UUID | None = None
    finalized_by: UUID | None = None
    reason: str = ""
    held: bool = False
    hold_reason: str = ""


@dataclass(frozen=True, kw_only=True)
class Earning(FinancialRecord):
    trip_id: UUID
    employee_id: UUID
    rate_id: UUID
    percentage: Decimal
    base: Decimal
    amount: Decimal
    original_date: date
    rounding_variance: Decimal = ZERO
    state: str = "READY"
    payroll_id: UUID | None = None


@dataclass(frozen=True, kw_only=True)
class Advance(FinancialRecord):
    employee_id: UUID
    requested_by: UUID
    amount: Decimal
    reason: str
    kind: str = "PERSONAL"
    trip_id: UUID | None = None
    state: str = "REQUESTED"
    approved_by: UUID | None = None
    installment: Decimal = ZERO
    start_on: date | None = None
    acknowledgment: str = ""


@dataclass(frozen=True, kw_only=True)
class AdvanceMovement(FinancialRecord):
    advance_id: UUID
    kind: str
    amount: Decimal
    actor_id: UUID
    reference: str
    occurred_on: date
    payroll_id: UUID | None = None
    reverses_id: UUID | None = None


@dataclass(frozen=True, kw_only=True)
class PayAdjustment(FinancialRecord):
    employee_id: UUID
    entered_by: UUID
    amount: Decimal
    kind: str
    period_start: date
    reason: str
    authorization: str
    state: str = "PENDING"
    approved_by: UUID | None = None
    payroll_id: UUID | None = None


@dataclass(frozen=True, kw_only=True)
class Payroll(FinancialRecord):
    start_on: date
    end_on: date
    prepared_by: UUID
    state: str = "DRAFT"
    finalized_by: UUID | None = None
    reason: str = ""


@dataclass(frozen=True, kw_only=True)
class PayStatement(FinancialRecord):
    payroll_id: UUID
    employee_id: UUID
    gross: Decimal
    deductions: Decimal
    repayments: Decimal
    net: Decimal
    lines: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True)
class Invoice(FinancialRecord):
    client_id: UUID
    cutoff: date
    entered_by: UUID
    total: Decimal
    terms_days: int = 30
    state: str = "DRAFT"
    issued_on: date | None = None
    due_on: date | None = None
    void_requested_by: UUID | None = None
    reason: str = ""
    held: bool = False


@dataclass(frozen=True, kw_only=True)
class InvoiceLine(FinancialRecord):
    invoice_id: UUID
    trip_id: UUID
    amount: Decimal
    delivered_on: date
    active: bool = True


@dataclass(frozen=True, kw_only=True)
class FinancialPayment(FinancialRecord):
    amount: Decimal
    allocated: Decimal
    paid_on: date
    method: str
    reference: str
    actor_id: UUID
    statement_id: UUID | None = None
    invoice_id: UUID | None = None


@dataclass(frozen=True, kw_only=True)
class AdvanceDelegation(FinancialRecord):
    employee_id: UUID
    delegated_by: UUID
    expires_on: date
    reason: str
    revoked: bool = False


@dataclass(frozen=True, kw_only=True)
class FinancialOperation(FinancialRecord):
    actor_id: UUID
    key: str
    fingerprint: str
    response: dict[str, object]
