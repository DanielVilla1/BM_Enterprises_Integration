# ===== AI GENERATED: operations_entities =====
# Purpose: Clients and delivery orders
# Inputs: values mapped by repositories
# Returns: frozen dataclasses and the order status enum
# Flow:
# 1. OrderStatus follows the proposal; Sprint 2 uses PENDING and CANCELLED
# 2. Weights are metric tons held as Decimal

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


class OrderStatus(StrEnum):
    PENDING = "PENDING"
    PARTIALLY_ASSIGNED = "PARTIALLY_ASSIGNED"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class Client:
    client_id: UUID
    name: str
    address: str | None
    contact_person: str | None
    contact_phone: str | None
    is_active: bool
    created_at: datetime


@dataclass(frozen=True)
class DeliveryOrder:
    order_id: UUID
    client_id: UUID
    client_reference: str | None
    pickup_location: str
    delivery_location: str
    scheduled_date: date
    total_weight_tons: Decimal
    status: OrderStatus
    notes: str | None
    cancellation_reason: str | None
    created_by: UUID | None
    created_at: datetime
