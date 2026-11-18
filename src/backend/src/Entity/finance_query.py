# ===== AI GENERATED: TripFinanceFacts =====
# Purpose: Typed batch facts for financial pages and operational reports.
# Inputs: Repository entities for a bounded, already-authorized trip page.
# Returns: Lookup maps without additional per-row database reads.
# Flow: Keep data retrieval in repositories and readiness decisions in services.

from dataclasses import dataclass
from uuid import UUID

from .documents import OrDocument
from .finance import ExpenseSheet, TripFinancial
from .operations import DeliveryOrder


@dataclass(frozen=True)
class TripFinanceFacts:
    orders: dict[UUID, DeliveryOrder]
    financials: dict[UUID, TripFinancial]
    expenses: dict[UUID, ExpenseSheet]
    earned_trip_ids: set[UUID]
    documents: dict[UUID, list[OrDocument]]
    allocated_trip_ids: set[UUID]
    client_names: dict[UUID, str]
