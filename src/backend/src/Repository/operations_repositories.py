# ===== AI GENERATED: operations_repositories =====
# Purpose: SQLAlchemy implementations for clients and delivery orders
# Inputs: Session
# Returns: operations entities (never ORM rows)
# Flow:
# 1. Query rows, map to entities
# 2. Updates only touch whitelisted columns
# 3. Flush writes; services commit

from collections.abc import Mapping
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..Entity.operations import Client, DeliveryOrder, OrderStatus
from .orm_models import ClientRow, DeliveryOrderRow

_CLIENT_FIELDS = {"name", "address", "contact_person", "contact_phone", "is_active"}
_ORDER_FIELDS = {
    "client_reference",
    "pickup_location",
    "delivery_location",
    "scheduled_date",
    "total_weight_tons",
    "notes",
}


def _client(row: ClientRow) -> Client:
    return Client(
        client_id=row.client_id,
        name=row.name,
        address=row.address,
        contact_person=row.contact_person,
        contact_phone=row.contact_phone,
        is_active=row.is_active,
        created_at=row.created_at,
    )


def _order(row: DeliveryOrderRow) -> DeliveryOrder:
    return DeliveryOrder(
        order_id=row.order_id,
        client_id=row.client_id,
        client_reference=row.client_reference,
        pickup_location=row.pickup_location,
        delivery_location=row.delivery_location,
        scheduled_date=row.scheduled_date,
        total_weight_tons=Decimal(row.total_weight_tons),
        status=OrderStatus(row.status),
        notes=row.notes,
        cancellation_reason=row.cancellation_reason,
        created_by=row.created_by,
        created_at=row.created_at,
    )


class ClientRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, client_id: UUID) -> Client | None:
        row = self._session.get(ClientRow, client_id)
        return _client(row) if row is not None else None

    def get_by_name(self, name: str) -> Client | None:
        statement = select(ClientRow).where(func.lower(ClientRow.name) == name.lower())
        row = self._session.scalars(statement).first()
        return _client(row) if row is not None else None

    def list_page(self, limit: int, offset: int, only_active: bool | None) -> list[Client]:
        statement = select(ClientRow).order_by(ClientRow.name, ClientRow.client_id)
        if only_active is not None:
            statement = statement.where(ClientRow.is_active == only_active)
        return [_client(row) for row in self._session.scalars(statement.limit(limit).offset(offset))]

    def create(
        self, name: str, address: str | None, contact_person: str | None, contact_phone: str | None
    ) -> Client:
        row = ClientRow(
            name=name,
            address=address,
            contact_person=contact_person,
            contact_phone=contact_phone,
            is_active=True,
        )
        self._session.add(row)
        self._session.flush()
        self._session.refresh(row)
        return _client(row)

    def update(self, client_id: UUID, changes: Mapping[str, object]) -> Client | None:
        row = self._session.get(ClientRow, client_id)
        if row is None:
            return None
        for field_name, value in changes.items():
            if field_name in _CLIENT_FIELDS:
                setattr(row, field_name, value)
        self._session.flush()
        self._session.refresh(row)
        return _client(row)


class DeliveryOrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, order_id: UUID) -> DeliveryOrder | None:
        row = self._session.get(DeliveryOrderRow, order_id)
        return _order(row) if row is not None else None

    def list_page(
        self,
        limit: int,
        offset: int,
        status: OrderStatus | None,
        client_id: UUID | None,
        date_from: date | None,
        date_to: date | None,
    ) -> list[DeliveryOrder]:
        statement = select(DeliveryOrderRow).order_by(
            DeliveryOrderRow.scheduled_date.desc(),
            DeliveryOrderRow.created_at.desc(),
            DeliveryOrderRow.order_id,
        )
        if status is not None:
            statement = statement.where(DeliveryOrderRow.status == status.value)
        if client_id is not None:
            statement = statement.where(DeliveryOrderRow.client_id == client_id)
        if date_from is not None:
            statement = statement.where(DeliveryOrderRow.scheduled_date >= date_from)
        if date_to is not None:
            statement = statement.where(DeliveryOrderRow.scheduled_date <= date_to)
        rows = self._session.scalars(statement.limit(limit).offset(offset)).all()
        return [_order(row) for row in rows]

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
    ) -> DeliveryOrder:
        row = DeliveryOrderRow(
            client_id=client_id,
            client_reference=client_reference,
            pickup_location=pickup_location,
            delivery_location=delivery_location,
            scheduled_date=scheduled_date,
            total_weight_tons=total_weight_tons,
            status=OrderStatus.PENDING.value,
            notes=notes,
            created_by=created_by,
        )
        self._session.add(row)
        self._session.flush()
        self._session.refresh(row)
        return _order(row)

    def update(self, order_id: UUID, changes: Mapping[str, object]) -> DeliveryOrder | None:
        row = self._session.get(DeliveryOrderRow, order_id)
        if row is None:
            return None
        for field_name, value in changes.items():
            if field_name in _ORDER_FIELDS:
                setattr(row, field_name, value)
        self._session.flush()
        self._session.refresh(row)
        return _order(row)

    def set_status(self, order_id: UUID, status: OrderStatus) -> DeliveryOrder | None:
        row = self._session.get(DeliveryOrderRow, order_id)
        if row is None:
            return None
        row.status = status.value
        self._session.flush()
        return _order(row)

    def cancel(self, order_id: UUID, reason: str) -> DeliveryOrder | None:
        row = self._session.get(DeliveryOrderRow, order_id)
        if row is None:
            return None
        row.status = OrderStatus.CANCELLED.value
        row.cancellation_reason = reason
        self._session.flush()
        return _order(row)
