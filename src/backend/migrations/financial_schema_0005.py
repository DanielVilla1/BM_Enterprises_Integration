# ===== AI GENERATED: financial_schema_snapshot_0005 =====
# Purpose: Freeze the financial schema used by migration 0005.
# Inputs: None; this snapshot has no application model dependencies.
# Returns: Metadata with financial tables and existing foreign-key targets.
# Flow: Preserve the original columns, constraints and indexes independently of future ORM changes.

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Independent registry for the immutable revision-0005 schema."""


# Foreign-key targets already created by earlier migrations are never created here.
Table("employees", Base.metadata, Column("employee_id", Uuid, primary_key=True))
Table("trips", Base.metadata, Column("trip_id", Uuid, primary_key=True))
Table("clients", Base.metadata, Column("client_id", Uuid, primary_key=True))


class RecordColumns:
    record_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class FinanceLockRow(Base):
    __tablename__ = "finance_lock"
    record_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)


class ExpenseSheetRow(RecordColumns, Base):
    __tablename__ = "expense_sheets"
    __table_args__ = (
        CheckConstraint("total >= 0", name="ck_expense_total"),
        CheckConstraint(
            "state IN ('ENTERING','AWAITING_REVIEW','FINALIZED','CONFIRMED_ZERO')", name="ck_expense_state"
        ),
        CheckConstraint("reviewed_by IS NULL OR reviewed_by <> entered_by", name="ck_expense_independent"),
    )
    trip_id: Mapped[UUID] = mapped_column(ForeignKey("trips.trip_id"), unique=True)
    entered_by: Mapped[UUID] = mapped_column(ForeignKey("employees.employee_id"))
    state: Mapped[str] = mapped_column(String(24))
    lines: Mapped[list] = mapped_column(JSON)
    declared_zero: Mapped[bool] = mapped_column(Boolean)
    reason: Mapped[str] = mapped_column(Text)
    reviewed_by: Mapped[UUID | None] = mapped_column(ForeignKey("employees.employee_id"))
    total: Mapped[Decimal] = mapped_column(Numeric(16, 2))


class RateVersionRow(RecordColumns, Base):
    __tablename__ = "earning_rates"
    __table_args__ = (
        CheckConstraint(
            "driver_one > 0 AND helper_one > 0 AND driver_two > 0 AND helper_two > 0 "
            "AND driver_one + helper_one <= 100 AND driver_two + helper_two * 2 <= 100",
            name="ck_earning_rates",
        ),
    )
    effective_on: Mapped[date] = mapped_column(Date, unique=True)
    driver_one: Mapped[Decimal] = mapped_column(Numeric(7, 4))
    helper_one: Mapped[Decimal] = mapped_column(Numeric(7, 4))
    driver_two: Mapped[Decimal] = mapped_column(Numeric(7, 4))
    helper_two: Mapped[Decimal] = mapped_column(Numeric(7, 4))
    reference: Mapped[str] = mapped_column(Text)
    entered_by: Mapped[UUID | None] = mapped_column(ForeignKey("employees.employee_id"))


class TripFinancialRow(RecordColumns, Base):
    __tablename__ = "trip_financials"
    __table_args__ = (
        CheckConstraint("charge IS NULL OR charge > 0", name="ck_trip_charge"),
        CheckConstraint("agreed_amount IS NULL OR agreed_amount > 0", name="ck_trip_agreed"),
        CheckConstraint("charge_state IN ('MISSING','AWAITING_REVIEW','FINALIZED')", name="ck_charge_state"),
    )
    trip_id: Mapped[UUID] = mapped_column(ForeignKey("trips.trip_id"), unique=True)
    rate_id: Mapped[UUID | None] = mapped_column(ForeignKey("earning_rates.record_id"))
    charge: Mapped[Decimal | None] = mapped_column(Numeric(16, 2))
    agreed_amount: Mapped[Decimal | None] = mapped_column(Numeric(16, 2))
    reference: Mapped[str] = mapped_column(Text)
    charge_state: Mapped[str] = mapped_column(String(24))
    entered_by: Mapped[UUID | None] = mapped_column(ForeignKey("employees.employee_id"))
    finalized_by: Mapped[UUID | None] = mapped_column(ForeignKey("employees.employee_id"))
    reason: Mapped[str] = mapped_column(Text)
    held: Mapped[bool] = mapped_column(Boolean)
    hold_reason: Mapped[str] = mapped_column(Text)


class PayrollRow(RecordColumns, Base):
    __tablename__ = "payrolls"
    __table_args__ = (
        UniqueConstraint("start_on", "end_on", name="uq_payroll_period"),
        CheckConstraint("end_on >= start_on", name="ck_payroll_dates"),
        CheckConstraint("state IN ('DRAFT','FINALIZED','REVERSED')", name="ck_payroll_state"),
    )
    start_on: Mapped[date] = mapped_column(Date)
    end_on: Mapped[date] = mapped_column(Date)
    prepared_by: Mapped[UUID] = mapped_column(ForeignKey("employees.employee_id"))
    state: Mapped[str] = mapped_column(String(16))
    finalized_by: Mapped[UUID | None] = mapped_column(ForeignKey("employees.employee_id"))
    reason: Mapped[str] = mapped_column(Text)


class EarningRow(RecordColumns, Base):
    __tablename__ = "earnings"
    __table_args__ = (
        UniqueConstraint("trip_id", "employee_id", name="uq_original_trip_earning"),
        CheckConstraint(
            "amount >= 0 AND base >= 0 AND percentage > 0 AND percentage <= 100", name="ck_earning_money"
        ),
    )
    trip_id: Mapped[UUID] = mapped_column(ForeignKey("trips.trip_id"), index=True)
    employee_id: Mapped[UUID] = mapped_column(ForeignKey("employees.employee_id"), index=True)
    rate_id: Mapped[UUID] = mapped_column(ForeignKey("earning_rates.record_id"))
    percentage: Mapped[Decimal] = mapped_column(Numeric(7, 4))
    base: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    original_date: Mapped[date] = mapped_column(Date)
    rounding_variance: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    state: Mapped[str] = mapped_column(String(16))
    payroll_id: Mapped[UUID | None] = mapped_column(ForeignKey("payrolls.record_id"), index=True)


class AdvanceRow(RecordColumns, Base):
    __tablename__ = "advances"
    __table_args__ = (
        CheckConstraint("amount > 0 AND installment >= 0", name="ck_advance_money"),
        CheckConstraint("kind IN ('PERSONAL','OPERATING')", name="ck_advance_kind"),
        CheckConstraint("kind <> 'OPERATING' OR trip_id IS NOT NULL", name="ck_operating_trip"),
        CheckConstraint(
            "approved_by IS NULL OR (approved_by <> requested_by AND approved_by <> employee_id)",
            name="ck_advance_independent",
        ),
    )
    employee_id: Mapped[UUID] = mapped_column(ForeignKey("employees.employee_id"), index=True)
    requested_by: Mapped[UUID] = mapped_column(ForeignKey("employees.employee_id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    reason: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(16))
    trip_id: Mapped[UUID | None] = mapped_column(ForeignKey("trips.trip_id"))
    state: Mapped[str] = mapped_column(String(16))
    approved_by: Mapped[UUID | None] = mapped_column(ForeignKey("employees.employee_id"))
    installment: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    start_on: Mapped[date | None] = mapped_column(Date)
    acknowledgment: Mapped[str] = mapped_column(Text)


class AdvanceMovementRow(RecordColumns, Base):
    __tablename__ = "advance_movements"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_advance_movement_money"),
        CheckConstraint(
            "kind IN ('RELEASE','RETURN','REPAYMENT','REVERSAL')", name="ck_advance_movement_kind"
        ),
        Index(
            "uq_advance_payroll_repayment",
            "advance_id",
            "payroll_id",
            unique=True,
            postgresql_where=text("kind = 'REPAYMENT'"),
            sqlite_where=text("kind = 'REPAYMENT'"),
        ),
    )
    advance_id: Mapped[UUID] = mapped_column(ForeignKey("advances.record_id"), index=True)
    kind: Mapped[str] = mapped_column(String(16))
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("employees.employee_id"))
    reference: Mapped[str] = mapped_column(Text)
    occurred_on: Mapped[date] = mapped_column(Date)
    payroll_id: Mapped[UUID | None] = mapped_column(ForeignKey("payrolls.record_id"))
    reverses_id: Mapped[UUID | None] = mapped_column(ForeignKey("advance_movements.record_id"), unique=True)


class PayAdjustmentRow(RecordColumns, Base):
    __tablename__ = "pay_adjustments"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_adjustment_money"),
        CheckConstraint("kind IN ('VOLUNTARY','OVERPAYMENT','CREDIT','DEBIT')", name="ck_adjustment_kind"),
        CheckConstraint(
            "approved_by IS NULL OR (approved_by <> entered_by AND approved_by <> employee_id)",
            name="ck_adjustment_independent",
        ),
    )
    employee_id: Mapped[UUID] = mapped_column(ForeignKey("employees.employee_id"))
    entered_by: Mapped[UUID] = mapped_column(ForeignKey("employees.employee_id"))
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    kind: Mapped[str] = mapped_column(String(16))
    period_start: Mapped[date] = mapped_column(Date)
    reason: Mapped[str] = mapped_column(Text)
    authorization: Mapped[str] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String(16))
    approved_by: Mapped[UUID | None] = mapped_column(ForeignKey("employees.employee_id"))
    payroll_id: Mapped[UUID | None] = mapped_column(ForeignKey("payrolls.record_id"))


class PayStatementRow(RecordColumns, Base):
    __tablename__ = "pay_statements"
    __table_args__ = (
        UniqueConstraint("payroll_id", "employee_id", name="uq_payroll_employee"),
        CheckConstraint(
            "gross >= 0 AND deductions >= 0 AND repayments >= 0 AND net >= 0 "
            "AND net = gross - deductions - repayments",
            name="ck_statement_money",
        ),
    )
    payroll_id: Mapped[UUID] = mapped_column(ForeignKey("payrolls.record_id"))
    employee_id: Mapped[UUID] = mapped_column(ForeignKey("employees.employee_id"), index=True)
    gross: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    deductions: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    repayments: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    net: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    lines: Mapped[list] = mapped_column(JSON)


class InvoiceRow(RecordColumns, Base):
    __tablename__ = "invoices"
    __table_args__ = (
        CheckConstraint("total > 0 AND terms_days >= 0 AND terms_days <= 365", name="ck_invoice_money"),
        CheckConstraint("state IN ('DRAFT','ISSUED','VOID_REQUESTED','VOID')", name="ck_invoice_state"),
    )
    client_id: Mapped[UUID] = mapped_column(ForeignKey("clients.client_id"), index=True)
    cutoff: Mapped[date] = mapped_column(Date)
    entered_by: Mapped[UUID] = mapped_column(ForeignKey("employees.employee_id"))
    total: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    terms_days: Mapped[int] = mapped_column(Integer)
    state: Mapped[str] = mapped_column(String(16))
    issued_on: Mapped[date | None] = mapped_column(Date)
    due_on: Mapped[date | None] = mapped_column(Date)
    void_requested_by: Mapped[UUID | None] = mapped_column(ForeignKey("employees.employee_id"))
    reason: Mapped[str] = mapped_column(Text)
    held: Mapped[bool] = mapped_column(Boolean)


class InvoiceLineRow(RecordColumns, Base):
    __tablename__ = "invoice_lines"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_invoice_line_money"),
        Index(
            "uq_active_trip_bill",
            "trip_id",
            unique=True,
            postgresql_where=text("active"),
            sqlite_where=text("active = 1"),
        ),
    )
    invoice_id: Mapped[UUID] = mapped_column(ForeignKey("invoices.record_id"), index=True)
    trip_id: Mapped[UUID] = mapped_column(ForeignKey("trips.trip_id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    delivered_on: Mapped[date] = mapped_column(Date)
    active: Mapped[bool] = mapped_column(Boolean)


class FinancialPaymentRow(RecordColumns, Base):
    __tablename__ = "financial_payments"
    __table_args__ = (
        CheckConstraint("amount > 0 AND allocated >= 0 AND allocated <= amount", name="ck_payment_money"),
        CheckConstraint(
            "(statement_id IS NOT NULL AND invoice_id IS NULL) "
            "OR (statement_id IS NULL AND invoice_id IS NOT NULL)",
            name="ck_payment_target",
        ),
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    allocated: Mapped[Decimal] = mapped_column(Numeric(16, 2))
    paid_on: Mapped[date] = mapped_column(Date)
    method: Mapped[str] = mapped_column(String(64))
    reference: Mapped[str] = mapped_column(Text)
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("employees.employee_id"))
    statement_id: Mapped[UUID | None] = mapped_column(ForeignKey("pay_statements.record_id"), index=True)
    invoice_id: Mapped[UUID | None] = mapped_column(ForeignKey("invoices.record_id"), index=True)


class AdvanceDelegationRow(RecordColumns, Base):
    __tablename__ = "advance_delegations"
    employee_id: Mapped[UUID] = mapped_column(ForeignKey("employees.employee_id"))
    delegated_by: Mapped[UUID] = mapped_column(ForeignKey("employees.employee_id"))
    expires_on: Mapped[date] = mapped_column(Date)
    reason: Mapped[str] = mapped_column(Text)
    revoked: Mapped[bool] = mapped_column(Boolean)


class FinancialOperationRow(RecordColumns, Base):
    __tablename__ = "financial_operations"
    __table_args__ = (UniqueConstraint("actor_id", "key", name="uq_finance_retry"),)
    actor_id: Mapped[UUID] = mapped_column(ForeignKey("employees.employee_id"))
    key: Mapped[str] = mapped_column(String(128))
    fingerprint: Mapped[str] = mapped_column(String(64))
    response: Mapped[dict] = mapped_column(JSON)


def finance_metadata() -> MetaData:
    """Return revision-0005 tables, marking only financial tables for DDL."""
    for table in Base.metadata.tables.values():
        table.info["financial"] = table.name not in {"employees", "trips", "clients"}
    return Base.metadata
