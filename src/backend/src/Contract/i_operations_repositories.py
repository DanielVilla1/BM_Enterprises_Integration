# ===== AI GENERATED: operations_repository_contracts =====
# Purpose: Ports for client and delivery order persistence
# Inputs: domain values
# Returns: operations entities
# Flow:
# 1. IClientRepository: CRUD with case-insensitive name lookup
# 2. IDeliveryOrderRepository: CRUD, filters, status changes

from collections.abc import Mapping
from datetime import date
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from ..Entity.operations import Client, DeliveryOrder, OrderStatus


class IClientRepository(Protocol):
    def get_many(self, identifiers: list[UUID]) -> list[Client]: ...
    def get_by_id(self, client_id: UUID) -> Client | None: ...

    def get_by_name(self, name: str) -> Client | None: ...

    def list_page(self, limit: int, offset: int, only_active: bool | None) -> list[Client]: ...

    def create(
        self, name: str, address: str | None, contact_person: str | None, contact_phone: str | None
    ) -> Client: ...

    def update(self, client_id: UUID, changes: Mapping[str, object]) -> Client | None: ...


class IDeliveryOrderRepository(Protocol):
    def get_many(self, identifiers: list[UUID]) -> list[DeliveryOrder]: ...
    def get_by_id(self, order_id: UUID) -> DeliveryOrder | None: ...

    def list_page(
        self,
        limit: int,
        offset: int,
        status: OrderStatus | None,
        client_id: UUID | None,
        date_from: date | None,
        date_to: date | None,
    ) -> list[DeliveryOrder]: ...

    def create(
        self,
        client_id: UUID,
        client_reference: str | None,
        pickup_location: str,
        delivery_location: str,
        scheduled_date: date,
        total_weight_tons: Decimal,
        notes: str | None,
        created_by: UUID | None,
    ) -> DeliveryOrder: ...

    def update(self, order_id: UUID, changes: Mapping[str, object]) -> DeliveryOrder | None: ...

    def cancel(self, order_id: UUID, reason: str) -> DeliveryOrder | None: ...

    def set_status(self, order_id: UUID, status: OrderStatus) -> DeliveryOrder | None: ...
