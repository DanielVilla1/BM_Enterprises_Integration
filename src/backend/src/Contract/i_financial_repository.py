# ===== AI GENERATED: IFinancialRepository =====
# Purpose: Typed financial persistence port; services never receive ORM objects.
# Inputs: Domain record types, identifiers and explicit equality filters.
# Returns: Financial records and serialized command results.
# Flow: Lock the finance transaction before checking balances or allocations.

from typing import Protocol, TypeVar
from uuid import UUID

from ..Entity.finance import FinancialRecord

RecordType = TypeVar("RecordType", bound=FinancialRecord)


class IFinancialRepository(Protocol):
    def lock(self) -> None: ...

    def get(self, record_type: type[RecordType], record_id: UUID) -> RecordType | None: ...

    def find(self, record_type: type[RecordType], **filters: object) -> list[RecordType]: ...

    def save(self, record: RecordType) -> RecordType: ...

    def find_many(
        self, record_type: type[RecordType], column: str, identifiers: list[UUID]
    ) -> list[RecordType]: ...


class ITripFinancialControls(Protocol):
    def lock_finances(self) -> None: ...

    def snapshot_departure(self, trip_id: UUID) -> None: ...

    def hold_receipt(self, trip_id: UUID, reason: str) -> None: ...

    def after_completion(self, trip_id: UUID, trace_id: str | None) -> None: ...
