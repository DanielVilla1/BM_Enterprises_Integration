# ===== AI GENERATED: FinancialRepository =====
# Purpose: Map normalized financial rows to immutable domain records.
# Inputs: One request-scoped SQLAlchemy session.
# Returns: Domain records; writes flush without committing.
# Flow: Serialize financial mutations; bind all filter values; map fields explicitly by record type.

from dataclasses import fields
from typing import TypeVar, cast
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..Entity import finance
from . import finance_models as tables

RecordType = TypeVar("RecordType", bound=finance.FinancialRecord)
RECORD_TABLES = {
    finance.ExpenseSheet: tables.ExpenseSheetRow,
    finance.RateVersion: tables.RateVersionRow,
    finance.TripFinancial: tables.TripFinancialRow,
    finance.Earning: tables.EarningRow,
    finance.Advance: tables.AdvanceRow,
    finance.AdvanceMovement: tables.AdvanceMovementRow,
    finance.PayAdjustment: tables.PayAdjustmentRow,
    finance.Payroll: tables.PayrollRow,
    finance.PayStatement: tables.PayStatementRow,
    finance.Invoice: tables.InvoiceRow,
    finance.InvoiceLine: tables.InvoiceLineRow,
    finance.FinancialPayment: tables.FinancialPaymentRow,
    finance.AdvanceDelegation: tables.AdvanceDelegationRow,
    finance.FinancialOperation: tables.FinancialOperationRow,
}


class FinancialRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def lock(self) -> None:
        """One short database write lock serializes money commands across workers.

        The UPDATE obtains a real write lock on SQLite too. This deliberately
        favors correctness at the specified small deployment size. Trip locks
        follow this lock, including receipt corrections, to avoid inverse order.
        """
        self._session.execute(
            update(tables.FinanceLockRow)
            .where(tables.FinanceLockRow.record_id == 1)
            .values(version=tables.FinanceLockRow.version + 1)
        )
        self._session.expire_all()

    @staticmethod
    def _entity(record_type: type[RecordType], row: object) -> RecordType:
        return record_type(**{column.name: getattr(row, column.name) for column in fields(record_type)})

    def get(self, record_type: type[RecordType], record_id: UUID) -> RecordType | None:
        row = self._session.get(RECORD_TABLES[record_type], record_id)
        return self._entity(record_type, row) if row is not None else None

    def find(self, record_type: type[RecordType], **filters: object) -> list[RecordType]:
        table = RECORD_TABLES[record_type]
        statement = select(table).filter_by(**filters).order_by(table.created_at, table.record_id)
        return [self._entity(record_type, row) for row in self._session.scalars(statement)]

    def find_many(
        self, record_type: type[RecordType], column: str, identifiers: list[UUID]
    ) -> list[RecordType]:
        if not identifiers:
            return []
        table = RECORD_TABLES[record_type]
        statement = (
            select(table)
            .where(getattr(table, column).in_(identifiers))
            .order_by(table.created_at, table.record_id)
        )
        return [self._entity(record_type, row) for row in self._session.scalars(statement)]

    def save(self, record: RecordType) -> RecordType:
        table = RECORD_TABLES[type(record)]
        row = self._session.get(table, record.record_id)
        if row is None:
            row = table()
            self._session.add(row)
        for column in fields(record):
            setattr(row, column.name, getattr(record, column.name))
        self._session.flush()
        return cast(RecordType, record)
