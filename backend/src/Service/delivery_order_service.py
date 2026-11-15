# ===== AI GENERATED: DeliveryOrderService =====
# Purpose: Encode, edit, list and cancel delivery orders (DO-01)
# Inputs: order + client repositories, audit, unit of work, date provider
# Returns: DeliveryOrder entities or BusinessRuleError
# Flow:
# 1. Validate client (exists, active) and schedule date (not in the past)
# 2. New orders are PENDING; only PENDING orders can be edited or cancelled
# 3. Audit every change, commit once

from collections.abc import Callable, Mapping
from datetime import date
from decimal import Decimal
from uuid import UUID

from ..Contract.i_audit_repository import IAuditRepository
from ..Contract.i_operations_repositories import IClientRepository, IDeliveryOrderRepository
from ..Contract.i_unit_of_work import IUnitOfWork
from ..Entity.business_rule_error import BusinessRuleError
from ..Entity.clock import manila_today
from ..Entity.employee import Principal
from ..Entity.operations import DeliveryOrder, OrderStatus


def _order_not_found() -> BusinessRuleError:
    return BusinessRuleError(404, "ORDER_NOT_FOUND", "Not found", "The delivery order was not found.")


class DeliveryOrderService:
    def __init__(
        self,
        orders: IDeliveryOrderRepository,
        clients: IClientRepository,
        audit: IAuditRepository,
        unit_of_work: IUnitOfWork,
        today_provider: Callable[[], date] = manila_today,
    ) -> None:
        self._orders = orders
        self._clients = clients
        self._audit = audit
        self._unit_of_work = unit_of_work
        self._today_provider = today_provider

    def list_orders(
        self,
        limit: int,
        offset: int,
        status: OrderStatus | None,
        client_id: UUID | None,
        date_from: date | None,
        date_to: date | None,
    ) -> list[DeliveryOrder]:
        return self._orders.list_page(limit, offset, status, client_id, date_from, date_to)

    def get_order(self, order_id: UUID) -> DeliveryOrder:
        order = self._orders.get_by_id(order_id)
        if order is None:
            raise _order_not_found()
        return order

    def create_order(
        self,
        principal: Principal,
        client_id: UUID,
        client_reference: str | None,
        pickup_location: str,
        delivery_location: str,
        scheduled_date: date,
        total_weight_tons: Decimal,
        notes: str | None,
        trace_id: str | None,
    ) -> DeliveryOrder:
        client = self._clients.get_by_id(client_id)
        if client is None:
            raise BusinessRuleError(404, "CLIENT_NOT_FOUND", "Not found", "The client was not found.")
        if not client.is_active:
            raise BusinessRuleError(
                409, "CLIENT_INACTIVE", "Conflict", "The client is inactive; orders cannot be recorded."
            )
        self._require_not_past(scheduled_date)
        order = self._orders.create(
            client_id,
            client_reference,
            pickup_location,
            delivery_location,
            scheduled_date,
            total_weight_tons,
            notes,
            principal.employee_id,
        )
        self._record(principal, "delivery_order.created", order.order_id, {}, trace_id)
        self._unit_of_work.commit()
        return order

    def update_order(
        self, principal: Principal, order_id: UUID, changes: Mapping[str, object], trace_id: str | None
    ) -> DeliveryOrder:
        order = self.get_order(order_id)
        if order.status is not OrderStatus.PENDING:
            raise BusinessRuleError(
                409, "ORDER_NOT_EDITABLE", "Conflict", "Only pending orders can be edited."
            )
        new_date = changes.get("scheduled_date")
        if isinstance(new_date, date):
            self._require_not_past(new_date)
        updated = self._orders.update(order_id, changes)
        if updated is None:
            raise _order_not_found()
        self._record(principal, "delivery_order.updated", order_id, {"fields": sorted(changes)}, trace_id)
        self._unit_of_work.commit()
        return updated

    def cancel_order(
        self, principal: Principal, order_id: UUID, reason: str, trace_id: str | None
    ) -> DeliveryOrder:
        order = self.get_order(order_id)
        if order.status is not OrderStatus.PENDING:
            raise BusinessRuleError(
                409, "ORDER_NOT_CANCELLABLE", "Conflict", "Only pending orders can be cancelled."
            )
        cancelled = self._orders.cancel(order_id, reason)
        if cancelled is None:
            raise _order_not_found()
        self._record(principal, "delivery_order.cancelled", order_id, {}, trace_id)
        self._unit_of_work.commit()
        return cancelled

    def _require_not_past(self, scheduled_date: date) -> None:
        if scheduled_date < self._today_provider():
            raise BusinessRuleError(
                422,
                "SCHEDULED_DATE_IN_PAST",
                "Validation failed",
                "The scheduled date cannot be in the past.",
            )

    def _record(
        self,
        principal: Principal,
        action: str,
        order_id: UUID,
        details: dict[str, object],
        trace_id: str | None,
    ) -> None:
        self._audit.append(principal.employee_id, action, "delivery_order", str(order_id), details, trace_id)
