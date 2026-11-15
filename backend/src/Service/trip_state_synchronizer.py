# ===== AI GENERATED: TripStateSynchronizer =====
# Purpose: Re-derive truck and order statuses from trips after any trip change
# Inputs: trip, truck and order repositories
# Returns: nothing; writes only when the derived status differs
# Flow:
# 1. Truck: never touches a truck in MAINTENANCE (a broken truck is not auto-released)
# 2. Order: never touches a CANCELLED order
# 3. Shared by dispatch and OR/completion services

from uuid import UUID

from ..Contract.i_fleet_repositories import ITruckRepository
from ..Contract.i_operations_repositories import IDeliveryOrderRepository
from ..Contract.i_trip_repository import ITripRepository
from ..Entity.dispatch import derive_order_status, derive_truck_status
from ..Entity.fleet import TruckStatus
from ..Entity.operations import OrderStatus


class TripStateSynchronizer:
    def __init__(
        self, trips: ITripRepository, orders: IDeliveryOrderRepository, trucks: ITruckRepository
    ) -> None:
        self._trips = trips
        self._orders = orders
        self._trucks = trucks

    def refresh_truck(self, truck_id: UUID) -> None:
        truck = self._trucks.get_by_id(truck_id)
        if truck is None or truck.status is TruckStatus.MAINTENANCE:
            return
        derived = derive_truck_status(self._trips.open_truck_statuses(truck_id))
        if derived is not truck.status:
            self._trucks.set_status(truck_id, derived)

    def refresh_order(self, order_id: UUID) -> None:
        order = self._orders.get_by_id(order_id)
        if order is None or order.status is OrderStatus.CANCELLED:
            return
        derived = derive_order_status(order.total_weight_tons, self._trips.list_for_order(order_id))
        if derived is not order.status:
            self._orders.set_status(order_id, derived)
