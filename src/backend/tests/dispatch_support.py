# ===== AI GENERATED: dispatch_test_support =====
# Purpose: Builders shared by the dispatch tests (fake clients, orders, trucks, crews)
# Inputs: client, session factory, employee factory
# Returns: World helper with assignment and state-forcing methods
# Flow:
# 1. Create records directly through repositories (fast, fake data only)
# 2. Assign trips through the real API
# 3. Force later statuses (OR upload, completion) that arrive in Sprint 4

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from uuid import UUID

from backend.src.Entity.access import RoleCode
from backend.src.Entity.clock import manila_today
from backend.src.Entity.dispatch import TripStatus
from backend.src.Entity.employee import Employee
from backend.src.Entity.fleet import Truck, TruckStatus
from backend.src.Repository.fleet_repositories import DriverLicenseRepository, TruckRepository
from backend.src.Repository.operations_repositories import ClientRepository, DeliveryOrderRepository
from backend.src.Repository.trip_repository import TripRepository
from backend.tests.conftest import auth_headers


class World:
    def __init__(self, client, session_factory, employees) -> None:
        self.client = client
        self.session_factory = session_factory
        self.employees = employees
        self.dispatcher = employees.create((RoleCode.DISPATCHER,), name="Dee Dispatcher")
        self.owner = employees.create((RoleCode.OWNER,), name="Olive Owner")
        self._counter = 0
        with session_factory() as session:
            created = ClientRepository(session).create("Fake Steel Corp", None, None, None)
            session.commit()
        self.client_id = created.client_id

    def next_number(self) -> int:
        self._counter += 1
        return self._counter

    def make_order(self, weight: str = "100", days_ahead: int = 1) -> UUID:
        with self.session_factory() as session:
            order = DeliveryOrderRepository(session).create(
                self.client_id,
                None,
                "Plant gate 4",
                "Harbour warehouse 7",
                manila_today() + timedelta(days=days_ahead),
                Decimal(weight),
                None,
                self.dispatcher.employee_id,
            )
            session.commit()
        return order.order_id

    def make_truck(self, capacity: str = "25") -> Truck:
        with self.session_factory() as session:
            truck = TruckRepository(session).create(f"TRK {self.next_number():04d}", None, Decimal(capacity))
            session.commit()
        return truck

    def make_driver(self, license_days: int | None = 365) -> Employee:
        driver = self.employees.create((RoleCode.DRIVER,), name=f"Driver {self.next_number()}")
        if license_days is not None:
            with self.session_factory() as session:
                DriverLicenseRepository(session).upsert(
                    driver.employee_id,
                    f"N01-00-{self.next_number():06d}",
                    manila_today() + timedelta(days=license_days),
                )
                session.commit()
        return driver

    def make_helper(self) -> Employee:
        return self.employees.create((RoleCode.HELPER,), name=f"Helper {self.next_number()}")

    def crew(self) -> tuple[Employee, list[Employee]]:
        return self.make_driver(), [self.make_helper()]

    def assign(self, order_id, truck, driver, helpers, load: float = 20, actor=None):
        actor = actor or self.dispatcher
        return self.client.post(
            f"/api/v1/delivery-orders/{order_id}/trips",
            headers=auth_headers(actor),
            json={
                "truck_id": str(truck.truck_id),
                "driver_id": str(driver.employee_id),
                "helper_ids": [str(helper.employee_id) for helper in helpers],
                "load_tons": load,
            },
        )

    def assign_ok(self, order_id, truck, driver, helpers, load: float = 20) -> dict:
        response = self.assign(order_id, truck, driver, helpers, load)
        assert response.status_code == 201, response.text
        return response.json()

    def post(self, path: str, actor, body: dict | None = None):
        return self.client.post(path, headers=auth_headers(actor), json=body)

    def get(self, path: str, actor, **params):
        return self.client.get(path, headers=auth_headers(actor), params=params)

    def force_status(self, trip_id: str, status: TripStatus) -> None:
        with self.session_factory() as session:
            TripRepository(session).set_status(UUID(trip_id), status)
            session.commit()

    def truck_status(self, truck_id) -> str:
        with self.session_factory() as session:
            truck = TruckRepository(session).get_by_id(UUID(str(truck_id)))
        return truck.status.value

    def set_truck_status(self, truck_id, status: TruckStatus) -> None:
        with self.session_factory() as session:
            TruckRepository(session).set_status(UUID(str(truck_id)), status)
            session.commit()

    def delivered_trip(self, load: float = 20, order_weight: str = "20") -> "DeliveredTrip":
        """Assign a trip and drive it through the API to DELIVERED_OR_PENDING."""
        order_id = self.make_order(order_weight)
        truck, (driver, helpers) = self.make_truck(), self.crew()
        trip = self.assign_ok(order_id, truck, driver, helpers, load)
        base = f"/api/v1/trips/{trip['trip_id']}"
        assert self.post(f"{base}/accept", driver).status_code == 200
        assert self.post(f"{base}/clear-dispatch", self.dispatcher).status_code == 200
        assert self.post(f"{base}/depart", driver).status_code == 200
        delivered = self.post(f"{base}/deliver", driver)
        assert delivered.status_code == 200
        return DeliveredTrip(order_id, truck, driver, helpers, delivered.json())

    def order_status(self, order_id) -> str:
        with self.session_factory() as session:
            order = DeliveryOrderRepository(session).get_by_id(UUID(str(order_id)))
        return order.status.value


@dataclass
class DeliveredTrip:
    order_id: UUID
    truck: Truck
    driver: Employee
    helpers: list[Employee]
    trip: dict

    @property
    def trip_id(self) -> str:
        return self.trip["trip_id"]
