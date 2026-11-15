# ===== AI GENERATED: operations_dto =====
# Purpose: Request / response shapes for clients and delivery orders
# Inputs: validated JSON bodies and entities
# Returns: strict Pydantic models (extra fields forbidden on input)
# Flow:
# 1. Weights are Decimal tons serialized as JSON numbers
# 2. Responses list allowed fields explicitly (API3)

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, StringConstraints

from ..Entity.operations import Client, DeliveryOrder, OrderStatus
from .partial_update import PartialUpdateRequest

Text160 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=160)]
Text300 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=300)]
Text120 = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
PhoneText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=32)]
ReferenceText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]
NotesText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
ReasonText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=500)]

OrderWeightTons = Annotated[
    Decimal,
    Field(gt=0, le=100000, max_digits=9, decimal_places=3),
    PlainSerializer(float, return_type=float, when_used="json"),
]


class ClientCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: Text160
    address: Text300 | None = None
    contact_person: Text120 | None = None
    contact_phone: PhoneText | None = None


class ClientUpdateRequest(PartialUpdateRequest):
    required_fields = frozenset({"name", "is_active"})

    name: Text160 | None = None
    address: Text300 | None = None
    contact_person: Text120 | None = None
    contact_phone: PhoneText | None = None
    is_active: bool | None = None


class ClientResponse(BaseModel):
    client_id: UUID
    name: str
    address: str | None
    contact_person: str | None
    contact_phone: str | None
    is_active: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, client: Client) -> "ClientResponse":
        return cls(
            client_id=client.client_id,
            name=client.name,
            address=client.address,
            contact_person=client.contact_person,
            contact_phone=client.contact_phone,
            is_active=client.is_active,
            created_at=client.created_at,
        )


class ClientPageResponse(BaseModel):
    items: list[ClientResponse]
    limit: int
    offset: int


class DeliveryOrderCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    client_id: UUID
    client_reference: ReferenceText | None = None
    pickup_location: Text300
    delivery_location: Text300
    scheduled_date: date
    total_weight_tons: OrderWeightTons
    notes: NotesText | None = None


class DeliveryOrderUpdateRequest(PartialUpdateRequest):
    required_fields = frozenset(
        {"pickup_location", "delivery_location", "scheduled_date", "total_weight_tons"}
    )

    client_reference: ReferenceText | None = None
    pickup_location: Text300 | None = None
    delivery_location: Text300 | None = None
    scheduled_date: date | None = None
    total_weight_tons: OrderWeightTons | None = None
    notes: NotesText | None = None


class DeliveryOrderCancelRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reason: ReasonText


class DeliveryOrderResponse(BaseModel):
    order_id: UUID
    client_id: UUID
    client_reference: str | None
    pickup_location: str
    delivery_location: str
    scheduled_date: date
    total_weight_tons: Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]
    status: OrderStatus
    notes: str | None
    cancellation_reason: str | None
    created_at: datetime

    @classmethod
    def from_entity(cls, order: DeliveryOrder) -> "DeliveryOrderResponse":
        return cls(
            order_id=order.order_id,
            client_id=order.client_id,
            client_reference=order.client_reference,
            pickup_location=order.pickup_location,
            delivery_location=order.delivery_location,
            scheduled_date=order.scheduled_date,
            total_weight_tons=order.total_weight_tons,
            status=order.status,
            notes=order.notes,
            cancellation_reason=order.cancellation_reason,
            created_at=order.created_at,
        )


class DeliveryOrderPageResponse(BaseModel):
    items: list[DeliveryOrderResponse]
    limit: int
    offset: int
