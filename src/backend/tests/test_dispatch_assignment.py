# ===== AI GENERATED: test_dispatch_assignment =====
# Purpose: Trip assignment rules: capacity, load, crew, license, availability
# Inputs: fake orders, trucks and crews
# Returns: pass/fail
# Flow:
# 1. FP-01: overloading is refused and nothing is created
# 2. Crew and license rules (spec 5.1)
# 3. Advance reservation after OR upload, but never a double reservation

from uuid import UUID

import pytest
from sqlalchemy.exc import IntegrityError

from backend.src.Entity.access import RoleCode
from backend.src.Entity.dispatch import TripStatus
from backend.src.Entity.fleet import TruckStatus
from backend.src.Repository.orm_models import TripCrewRow
from backend.tests.conftest import auth_headers
from backend.tests.dispatch_support import World


@pytest.fixture
def world(client, session_factory, employees) -> World:
    return World(client, session_factory, employees)


def test_valid_assignment_creates_a_scheduled_trip_and_updates_order_and_truck(world: World) -> None:
    order_id = world.make_order("100")
    truck = world.make_truck("25")
    driver, helpers = world.crew()
    trip = world.assign_ok(order_id, truck, driver, helpers, load=20)
    assert trip["status"] == "SCHEDULED"
    assert trip["driver_id"] == str(driver.employee_id)
    assert trip["helper_ids"] == [str(helpers[0].employee_id)]
    assert trip["load_tons"] == 20
    assert trip["pickup_location"] == "Plant gate 4"
    assert world.truck_status(truck.truck_id) == "ASSIGNED"
    assert world.order_status(order_id) == "PARTIALLY_ASSIGNED"


def test_order_becomes_scheduled_when_the_whole_load_is_assigned(world: World) -> None:
    order_id = world.make_order("40")
    first_driver, first_helpers = world.crew()
    second_driver, second_helpers = world.crew()
    world.assign_ok(order_id, world.make_truck(), first_driver, first_helpers, load=20)
    assert world.order_status(order_id) == "PARTIALLY_ASSIGNED"
    world.assign_ok(order_id, world.make_truck(), second_driver, second_helpers, load=20)
    assert world.order_status(order_id) == "SCHEDULED"


def test_overloading_a_truck_is_refused_and_creates_nothing(world: World) -> None:
    order_id = world.make_order("100")
    truck = world.make_truck("20")
    driver, helpers = world.crew()
    response = world.assign(order_id, truck, driver, helpers, load=25)
    assert response.status_code == 409
    assert response.json()["code"] == "CAPACITY_EXCEEDED"
    assert response.headers["content-type"].startswith("application/problem+json")
    assert world.get("/api/v1/trips", world.dispatcher).json()["items"] == []
    assert world.order_status(order_id) == "PENDING"
    assert world.truck_status(truck.truck_id) == "AVAILABLE"
    at_limit = world.assign(order_id, truck, driver, helpers, load=20)
    assert at_limit.status_code == 201


def test_load_cannot_exceed_the_unassigned_order_weight(world: World) -> None:
    order_id = world.make_order("30")
    first_driver, first_helpers = world.crew()
    second_driver, second_helpers = world.crew()
    world.assign_ok(order_id, world.make_truck(), first_driver, first_helpers, load=20)
    response = world.assign(order_id, world.make_truck(), second_driver, second_helpers, load=11)
    assert response.status_code == 409 and response.json()["code"] == "LOAD_EXCEEDS_ORDER"
    assert (
        world.assign(order_id, world.make_truck(), second_driver, second_helpers, load=10).status_code == 201
    )


def test_cancelled_and_unknown_orders_cannot_receive_trips(world: World) -> None:
    driver, helpers = world.crew()
    truck = world.make_truck()
    order_id = world.make_order()
    cancel = world.post(
        f"/api/v1/delivery-orders/{order_id}/cancel", world.dispatcher, {"reason": "Client withdrew"}
    )
    assert cancel.status_code == 200
    response = world.assign(order_id, truck, driver, helpers)
    assert response.status_code == 409 and response.json()["code"] == "ORDER_NOT_ASSIGNABLE"
    unknown = world.assign("00000000-0000-4000-8000-000000000001", truck, driver, helpers)
    assert unknown.status_code == 404 and unknown.json()["code"] == "ORDER_NOT_FOUND"


def test_trucks_in_maintenance_or_retired_cannot_be_assigned(world: World) -> None:
    order_id = world.make_order()
    driver, helpers = world.crew()
    broken = world.make_truck()
    world.set_truck_status(broken.truck_id, TruckStatus.MAINTENANCE)
    response = world.assign(order_id, broken, driver, helpers)
    assert response.status_code == 409 and response.json()["code"] == "TRUCK_UNAVAILABLE"
    fleet_manager = world.employees.create((RoleCode.FLEET_MANAGER,))
    retired = world.make_truck()
    world.client.patch(
        f"/api/v1/trucks/{retired.truck_id}",
        headers=auth_headers(fleet_manager),
        json={"is_active": False},
    )
    assert world.assign(order_id, retired, driver, helpers).json()["code"] == "TRUCK_UNAVAILABLE"
    missing = world.client.post(
        f"/api/v1/delivery-orders/{order_id}/trips",
        headers=auth_headers(world.dispatcher),
        json={
            "truck_id": "00000000-0000-4000-8000-000000000002",
            "driver_id": str(driver.employee_id),
            "helper_ids": [str(helpers[0].employee_id)],
            "load_tons": 5,
        },
    )
    assert missing.status_code == 404 and missing.json()["code"] == "TRUCK_NOT_FOUND"


def test_crew_must_be_one_driver_and_one_or_two_distinct_helpers(world: World) -> None:
    order_id = world.make_order()
    truck = world.make_truck()
    driver = world.make_driver()
    helper_a, helper_b, helper_c = world.make_helper(), world.make_helper(), world.make_helper()
    assert world.assign(order_id, truck, driver, []).status_code == 422
    assert world.assign(order_id, truck, driver, [helper_a, helper_b, helper_c]).status_code == 422
    assert world.assign(order_id, truck, driver, [helper_a, helper_a]).json()["code"] == "CREW_DUPLICATE"
    assert world.assign(order_id, truck, driver, [driver]).json()["code"] == "CREW_DUPLICATE"
    assert world.assign(order_id, truck, driver, [helper_a, helper_b]).status_code == 201


def test_roles_and_active_status_of_the_crew_are_enforced(world: World) -> None:
    order_id = world.make_order()
    truck = world.make_truck()
    driver, helpers = world.crew()
    not_a_driver = world.assign(order_id, truck, helpers[0], [world.make_helper()])
    assert not_a_driver.json()["code"] == "NOT_A_DRIVER"
    fake_helper = world.make_driver()
    not_a_helper = world.assign(order_id, truck, driver, [fake_helper])
    assert not_a_helper.json()["code"] == "NOT_A_HELPER"
    inactive = world.employees.create((RoleCode.HELPER,), active=False)
    assert world.assign(order_id, truck, driver, [inactive]).json()["code"] == "EMPLOYEE_INACTIVE"
    unknown = world.client.post(
        f"/api/v1/delivery-orders/{order_id}/trips",
        headers=auth_headers(world.dispatcher),
        json={
            "truck_id": str(truck.truck_id),
            "driver_id": "00000000-0000-4000-8000-000000000003",
            "helper_ids": [str(helpers[0].employee_id)],
            "load_tons": 5,
        },
    )
    assert unknown.status_code == 404 and unknown.json()["code"] == "EMPLOYEE_NOT_FOUND"


def test_driver_license_must_exist_and_be_valid_for_the_trip_date(world: World) -> None:
    truck = world.make_truck()
    helper = world.make_helper()
    order_id = world.make_order()
    assert (
        world.assign(order_id, truck, world.make_driver(license_days=None), [helper]).json()["code"]
        == "DRIVER_LICENSE_MISSING"
    )
    assert (
        world.assign(order_id, truck, world.make_driver(license_days=-1), [helper]).json()["code"]
        == "DRIVER_LICENSE_EXPIRED"
    )
    expiring = world.make_driver(license_days=5)
    assert world.assign(order_id, truck, expiring, [helper]).status_code == 201
    later_order = world.make_order(days_ahead=10)
    other_driver = world.make_driver(license_days=5)
    other_truck = world.make_truck()
    expired_by_then = world.assign(later_order, other_truck, other_driver, [world.make_helper()])
    assert expired_by_then.status_code == 409 and expired_by_then.json()["code"] == "DRIVER_LICENSE_EXPIRED"


@pytest.mark.parametrize("busy", ["truck", "driver", "helper"])
def test_resources_with_an_assigned_trip_cannot_be_double_booked(world: World, busy: str) -> None:
    first_order = world.make_order()
    second_order = world.make_order()
    truck, (driver, helpers) = world.make_truck(), world.crew()
    first = world.assign_ok(first_order, truck, driver, helpers)
    other_truck, (other_driver, other_helpers) = world.make_truck(), world.crew()
    second_truck = truck if busy == "truck" else other_truck
    second_driver = driver if busy == "driver" else other_driver
    second_helpers = helpers if busy == "helper" else other_helpers
    response = world.assign(second_order, second_truck, second_driver, second_helpers)
    assert response.status_code == 409
    assert response.json()["code"] == "RESOURCE_UNAVAILABLE"
    assert response.json()["blocking_trip_ids"] == [first["trip_id"]]


def test_uploading_the_or_allows_one_advance_reservation_but_not_two(world: World) -> None:
    first_order, second_order, third_order = world.make_order(), world.make_order(), world.make_order()
    truck, (driver, helpers) = world.make_truck(), world.crew()
    first = world.assign_ok(first_order, truck, driver, helpers)
    world.force_status(first["trip_id"], TripStatus.DELIVERED_OR_PENDING)
    still_blocked = world.assign(second_order, truck, driver, helpers)
    assert still_blocked.status_code == 409
    world.force_status(first["trip_id"], TripStatus.OR_UPLOADED)
    reserved = world.assign(second_order, truck, driver, helpers)
    assert reserved.status_code == 201 and reserved.json()["status"] == "SCHEDULED"
    double = world.assign(third_order, truck, driver, helpers)
    assert double.status_code == 409 and double.json()["code"] == "RESOURCE_UNAVAILABLE"
    assert double.json()["blocking_trip_ids"] == [reserved.json()["trip_id"]]


def test_a_completed_trip_frees_the_resources_completely(world: World) -> None:
    first_order, second_order = world.make_order(), world.make_order()
    truck, (driver, helpers) = world.make_truck(), world.crew()
    first = world.assign_ok(first_order, truck, driver, helpers)
    world.force_status(first["trip_id"], TripStatus.COMPLETED)
    assert world.assign(second_order, truck, driver, helpers).status_code == 201


def test_only_owner_and_dispatcher_can_assign_trips(world: World) -> None:
    order_id = world.make_order()
    truck, (driver, helpers) = world.make_truck(), world.crew()
    for role in (
        RoleCode.FLEET_MANAGER,
        RoleCode.DRIVER,
        RoleCode.HELPER,
        RoleCode.HR_PAYROLL,
        RoleCode.ACCOUNTING,
    ):
        actor = world.employees.create((role,))
        assert world.assign(order_id, truck, driver, helpers, actor=actor).status_code == 403
    assert world.assign(order_id, truck, driver, helpers, actor=world.owner).status_code == 201


def test_unknown_fields_and_bad_loads_are_rejected(world: World) -> None:
    order_id = world.make_order()
    truck, (driver, helpers) = world.make_truck(), world.crew()
    body = {
        "truck_id": str(truck.truck_id),
        "driver_id": str(driver.employee_id),
        "helper_ids": [str(helpers[0].employee_id)],
        "load_tons": 10,
    }
    headers = auth_headers(world.dispatcher)
    url = f"/api/v1/delivery-orders/{order_id}/trips"
    assert world.client.post(url, headers=headers, json={**body, "status": "COMPLETED"}).status_code == 422
    assert world.client.post(url, headers=headers, json={**body, "load_tons": 0}).status_code == 422
    assert world.client.post(url, headers=headers, json={**body, "load_tons": -3}).status_code == 422


def test_the_database_allows_only_one_active_driver_per_trip(world: World, session_factory) -> None:
    order_id = world.make_order()
    truck, (driver, helpers) = world.make_truck(), world.crew()
    trip = world.assign_ok(order_id, truck, driver, helpers)
    other_driver = world.make_driver()
    with session_factory() as session, pytest.raises(IntegrityError):
        session.add(
            TripCrewRow(
                trip_id=UUID(trip["trip_id"]), employee_id=other_driver.employee_id, crew_role="DRIVER"
            )
        )
        session.commit()


def test_assignment_is_audited(world: World) -> None:
    order_id = world.make_order()
    truck, (driver, helpers) = world.make_truck(), world.crew()
    trip = world.assign_ok(order_id, truck, driver, helpers)
    audit = world.get("/api/v1/audit-logs", world.owner).json()["items"]
    created = [row for row in audit if row["action"] == "trip.created"]
    assert created and created[0]["entity_id"] == trip["trip_id"]
    assert created[0]["actor_employee_id"] == str(world.dispatcher.employee_id)
