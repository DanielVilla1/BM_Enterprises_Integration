# ===== AI GENERATED: test_dispatch_flow =====
# Purpose: Trip workflow, OR dispatch block, cancel/fail, crew change, truck replacement
# Inputs: fake orders, trucks and crews
# Returns: pass/fail
# Flow:
# 1. Driver-only progress and ownership (API1)
# 2. Outstanding-OR block identifies the blocking trip and preserves reservations
# 3. Crew and truck changes never bypass restrictions or create extra charges

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

import pytest
from sqlalchemy import func, select

from backend.src.Entity.access import RoleCode
from backend.src.Entity.dispatch import Trip, TripStatus, derive_order_status, derive_truck_status
from backend.src.Entity.fleet import TruckStatus
from backend.src.Entity.operations import OrderStatus
from backend.src.Repository.orm_models import TripCrewRow, TripRow, TruckReplacementRow
from backend.tests.conftest import auth_headers
from backend.tests.dispatch_support import World

BLOCK_MESSAGE = (
    "Dispatch blocked: The previous trip's OR has not yet been marked as received by the steel company."
)


@pytest.fixture
def world(client, session_factory, employees) -> World:
    return World(client, session_factory, employees)


def _scheduled(world: World, load: float = 20):
    order_id = world.make_order("100")
    truck, (driver, helpers) = world.make_truck(), world.crew()
    trip = world.assign_ok(order_id, truck, driver, helpers, load)
    return order_id, truck, driver, helpers, trip


def _trip_url(trip: dict, action: str) -> str:
    return f"/api/v1/trips/{trip['trip_id']}/{action}"


def test_full_progress_from_acceptance_to_delivery(world: World) -> None:
    order_id, truck, driver, _helpers, trip = _scheduled(world)
    accepted = world.post(_trip_url(trip, "accept"), driver)
    assert accepted.status_code == 200 and accepted.json()["status"] == "ACCEPTED"
    assert accepted.json()["accepted_at"] is not None
    cleared = world.post(_trip_url(trip, "clear-dispatch"), world.dispatcher)
    assert cleared.status_code == 200 and cleared.json()["status"] == "CLEARED_FOR_DISPATCH"
    departed = world.post(_trip_url(trip, "depart"), driver)
    assert departed.status_code == 200 and departed.json()["status"] == "IN_TRANSIT"
    assert world.truck_status(truck.truck_id) == "IN_TRANSIT"
    assert world.order_status(order_id) == "IN_PROGRESS"
    delivered = world.post(_trip_url(trip, "deliver"), driver)
    assert delivered.status_code == 200 and delivered.json()["status"] == "DELIVERED_OR_PENDING"
    assert delivered.json()["delivered_at"] is not None
    assert world.truck_status(truck.truck_id) == "ASSIGNED"


def test_steps_cannot_be_skipped_or_repeated(world: World) -> None:
    _order, _truck, driver, _helpers, trip = _scheduled(world)
    assert (
        world.post(_trip_url(trip, "clear-dispatch"), world.dispatcher).json()["code"] == "TRIP_NOT_ACCEPTED"
    )
    assert world.post(_trip_url(trip, "depart"), driver).json()["code"] == "TRIP_NOT_CLEARED"
    assert world.post(_trip_url(trip, "deliver"), driver).json()["code"] == "TRIP_NOT_IN_TRANSIT"
    world.post(_trip_url(trip, "accept"), driver)
    assert world.post(_trip_url(trip, "accept"), driver).json()["code"] == "TRIP_NOT_SCHEDULED"


def test_only_the_assigned_driver_can_progress_a_trip(world: World) -> None:
    _order, _truck, driver, helpers, trip = _scheduled(world)
    other_driver = world.make_driver()
    assert world.post(_trip_url(trip, "accept"), other_driver).status_code == 404
    assert world.post(_trip_url(trip, "accept"), world.dispatcher).status_code == 403
    assert world.post(_trip_url(trip, "accept"), world.owner).status_code == 403
    assert world.post(_trip_url(trip, "accept"), helpers[0]).status_code == 403
    assert world.post(_trip_url(trip, "accept"), driver).status_code == 200


def test_outstanding_or_blocks_dispatch_and_names_the_blocking_trip(world: World) -> None:
    truck, (driver, helpers) = world.make_truck(), world.crew()
    first_order, second_order = world.make_order(), world.make_order()
    first = world.assign_ok(first_order, truck, driver, helpers)
    world.force_status(first["trip_id"], TripStatus.OR_UPLOADED)
    second = world.assign_ok(second_order, truck, driver, helpers)
    assert world.post(_trip_url(second, "accept"), driver).status_code == 200
    blocked = world.post(_trip_url(second, "clear-dispatch"), world.dispatcher)
    assert blocked.status_code == 409
    body = blocked.json()
    assert body["code"] == "DISPATCH_BLOCKED" and body["detail"] == BLOCK_MESSAGE
    assert body["blocking_trip_ids"] == [first["trip_id"]]
    world.force_status(first["trip_id"], TripStatus.COMPLETED)
    assert world.post(_trip_url(second, "clear-dispatch"), world.dispatcher).status_code == 200
    assert world.truck_status(truck.truck_id) == "ASSIGNED"


def test_a_blocked_crew_member_blocks_even_with_a_different_truck(world: World) -> None:
    driver, helpers = world.crew()
    first = world.assign_ok(world.make_order(), world.make_truck(), driver, helpers)
    world.force_status(first["trip_id"], TripStatus.OR_UPLOADED)
    other_truck, (other_driver, _unused) = world.make_truck(), world.crew()
    second = world.assign_ok(world.make_order(), other_truck, other_driver, helpers)
    world.post(_trip_url(second, "accept"), other_driver)
    blocked = world.post(_trip_url(second, "clear-dispatch"), world.dispatcher)
    assert blocked.status_code == 409 and blocked.json()["blocking_trip_ids"] == [first["trip_id"]]


def test_departure_rechecks_the_restriction(world: World) -> None:
    truck, (driver, helpers) = world.make_truck(), world.crew()
    first = world.assign_ok(world.make_order(), truck, driver, helpers)
    world.force_status(first["trip_id"], TripStatus.OR_UPLOADED)
    second = world.assign_ok(world.make_order(), truck, driver, helpers)
    world.post(_trip_url(second, "accept"), driver)
    world.force_status(second["trip_id"], TripStatus.CLEARED_FOR_DISPATCH)
    departure = world.post(_trip_url(second, "depart"), driver)
    assert departure.status_code == 409 and departure.json()["code"] == "DISPATCH_BLOCKED"


def test_cancel_before_departure_frees_the_resources_and_the_order_load(world: World) -> None:
    order_id, truck, driver, helpers, trip = _scheduled(world)
    cancelled = world.post(_trip_url(trip, "cancel"), world.dispatcher, {"reason": "Client moved the date"})
    assert cancelled.status_code == 200
    assert (
        cancelled.json()["status"] == "CANCELLED"
        and cancelled.json()["closed_reason"] == "Client moved the date"
    )
    assert world.truck_status(truck.truck_id) == "AVAILABLE"
    assert world.order_status(order_id) == "PENDING"
    assert world.assign(order_id, truck, driver, helpers).status_code == 201


def test_cancel_and_fail_are_limited_to_the_right_stages_and_roles(world: World) -> None:
    order_id, truck, driver, _helpers, trip = _scheduled(world)
    assert (
        world.post(_trip_url(trip, "fail"), world.dispatcher, {"reason": "Truck broke"}).json()["code"]
        == "TRIP_NOT_FAILABLE"
    )
    world.post(_trip_url(trip, "accept"), driver)
    world.post(_trip_url(trip, "clear-dispatch"), world.dispatcher)
    world.post(_trip_url(trip, "depart"), driver)
    assert (
        world.post(_trip_url(trip, "cancel"), world.dispatcher, {"reason": "Too late now"}).json()["code"]
        == "TRIP_NOT_CANCELLABLE"
    )
    assert world.post(_trip_url(trip, "fail"), driver, {"reason": "Truck broke"}).status_code == 403
    failed = world.post(_trip_url(trip, "fail"), world.owner, {"reason": "Truck broke down"})
    assert failed.status_code == 200 and failed.json()["status"] == "FAILED"
    assert world.order_status(order_id) == "PENDING"
    assert world.truck_status(truck.truck_id) == "AVAILABLE"
    assert world.post(_trip_url(trip, "fail"), world.owner, {"reason": "Again please"}).status_code == 409


def test_crew_can_change_before_departure_and_history_is_retained(world: World, session_factory) -> None:
    _order, _truck, driver, _helpers, trip = _scheduled(world)
    new_helper = world.make_helper()
    response = _change_crew(world, trip, driver, [new_helper])
    assert response.status_code == 200
    assert response.json()["helper_ids"] == [str(new_helper.employee_id)]
    trip_id = UUID(trip["trip_id"])
    with session_factory() as session:
        crew_rows = select(func.count()).select_from(TripCrewRow).where(TripCrewRow.trip_id == trip_id)
        total = session.scalar(crew_rows)
        active = session.scalar(crew_rows.where(TripCrewRow.removed_at.is_(None)))
    assert total == 4 and active == 2


def _change_crew(world: World, trip: dict, driver, helpers, actor=None):
    return world.client.put(
        f"/api/v1/trips/{trip['trip_id']}/crew",
        headers=auth_headers(actor or world.dispatcher),
        json={"driver_id": str(driver.employee_id), "helper_ids": [str(one.employee_id) for one in helpers]},
    )


def test_changing_the_driver_requires_a_new_acceptance(world: World) -> None:
    _order, _truck, driver, helpers, trip = _scheduled(world)
    world.post(_trip_url(trip, "accept"), driver)
    world.post(_trip_url(trip, "clear-dispatch"), world.dispatcher)
    new_driver = world.make_driver()
    changed = _change_crew(world, trip, new_driver, helpers)
    assert changed.status_code == 200
    assert changed.json()["status"] == "SCHEDULED" and changed.json()["accepted_at"] is None
    assert world.post(_trip_url(trip, "accept"), driver).status_code == 404
    assert world.post(_trip_url(trip, "accept"), new_driver).status_code == 200


def test_changing_helpers_after_clearance_requires_clearing_again(world: World) -> None:
    _order, _truck, driver, _helpers, trip = _scheduled(world)
    world.post(_trip_url(trip, "accept"), driver)
    world.post(_trip_url(trip, "clear-dispatch"), world.dispatcher)
    changed = _change_crew(world, trip, driver, [world.make_helper()])
    assert changed.status_code == 200 and changed.json()["status"] == "ACCEPTED"
    assert changed.json()["cleared_at"] is None


def test_crew_is_locked_after_departure_and_new_crew_must_be_available(world: World) -> None:
    _order, _truck, driver, helpers, trip = _scheduled(world)
    busy_driver, busy_helpers = world.crew()
    world.assign_ok(world.make_order(), world.make_truck(), busy_driver, busy_helpers)
    clash = _change_crew(world, trip, busy_driver, helpers)
    assert clash.status_code == 409 and clash.json()["code"] == "RESOURCE_UNAVAILABLE"
    same = _change_crew(world, trip, driver, helpers)
    assert same.status_code == 200 and same.json()["status"] == "SCHEDULED"
    world.post(_trip_url(trip, "accept"), driver)
    world.post(_trip_url(trip, "clear-dispatch"), world.dispatcher)
    world.post(_trip_url(trip, "depart"), driver)
    locked = _change_crew(world, trip, driver, [world.make_helper()])
    assert locked.status_code == 409 and locked.json()["code"] == "CREW_LOCKED"


def _replace(world: World, trip: dict, replacement, needs_maintenance: bool, actor=None):
    return world.client.post(
        f"/api/v1/trips/{trip['trip_id']}/truck-replacement",
        headers=auth_headers(actor or world.dispatcher),
        json={
            "replacement_truck_id": str(replacement.truck_id),
            "reason": "Engine overheating",
            "original_truck_needs_maintenance": needs_maintenance,
        },
    )


def test_truck_replacement_keeps_one_trip_and_records_history(world: World, session_factory) -> None:
    order_id, original, _driver, _helpers, trip = _scheduled(world)
    replacement = world.make_truck("30")
    response = _replace(world, trip, replacement, needs_maintenance=False)
    assert response.status_code == 200 and response.json()["truck_id"] == str(replacement.truck_id)
    assert world.truck_status(original.truck_id) == "AVAILABLE"
    assert world.truck_status(replacement.truck_id) == "ASSIGNED"
    with session_factory() as session:
        trips = session.scalar(select(func.count()).select_from(TripRow))
        history = session.scalar(select(func.count()).select_from(TruckReplacementRow))
    assert trips == 1 and history == 1
    assert world.order_status(order_id) == "PARTIALLY_ASSIGNED"


def test_a_broken_original_truck_is_never_released_automatically(world: World) -> None:
    _order, original, driver, _helpers, trip = _scheduled(world)
    world.post(_trip_url(trip, "accept"), driver)
    world.post(_trip_url(trip, "clear-dispatch"), world.dispatcher)
    world.post(_trip_url(trip, "depart"), driver)
    replacement = world.make_truck()
    assert _replace(world, trip, replacement, needs_maintenance=True).status_code == 200
    assert world.truck_status(original.truck_id) == "MAINTENANCE"
    assert world.truck_status(replacement.truck_id) == "IN_TRANSIT"
    world.post(_trip_url(trip, "deliver"), driver)
    world.force_status(trip["trip_id"], TripStatus.COMPLETED)
    assert world.truck_status(original.truck_id) == "MAINTENANCE"


def test_replacement_must_fit_the_load_and_be_free_and_different(world: World) -> None:
    _order, original, _driver, _helpers, trip = _scheduled(world, load=20)
    assert _replace(world, trip, original, False).json()["code"] == "SAME_TRUCK"
    small = world.make_truck("10")
    assert _replace(world, trip, small, False).json()["code"] == "CAPACITY_EXCEEDED"
    busy = world.make_truck()
    busy_driver, busy_helpers = world.crew()
    world.assign_ok(world.make_order(), busy, busy_driver, busy_helpers)
    assert _replace(world, trip, busy, False).json()["code"] == "RESOURCE_UNAVAILABLE"
    maintenance = world.make_truck()
    world.set_truck_status(maintenance.truck_id, TruckStatus.MAINTENANCE)
    assert _replace(world, trip, maintenance, False).json()["code"] == "TRUCK_UNAVAILABLE"


def test_replacement_cannot_bypass_the_outstanding_or_restriction(world: World) -> None:
    _order, _original, driver, _helpers, trip = _scheduled(world)
    world.post(_trip_url(trip, "accept"), driver)
    world.post(_trip_url(trip, "clear-dispatch"), world.dispatcher)
    waiting = world.make_truck()
    other_driver, other_helpers = world.crew()
    earlier = world.assign_ok(world.make_order(), waiting, other_driver, other_helpers)
    world.force_status(earlier["trip_id"], TripStatus.OR_UPLOADED)
    blocked = _replace(world, trip, waiting, False)
    assert blocked.status_code == 409 and blocked.json()["code"] == "DISPATCH_BLOCKED"
    assert blocked.json()["blocking_trip_ids"] == [earlier["trip_id"]]


def test_replacement_is_limited_by_stage_and_role(world: World) -> None:
    _order, _original, _driver, _helpers, trip = _scheduled(world)
    replacement = world.make_truck()
    for role in (RoleCode.FLEET_MANAGER, RoleCode.DRIVER, RoleCode.ACCOUNTING):
        assert (
            _replace(world, trip, replacement, False, actor=world.employees.create((role,))).status_code
            == 403
        )
    world.force_status(trip["trip_id"], TripStatus.DELIVERED_OR_PENDING)
    late = _replace(world, trip, replacement, False, actor=world.owner)
    assert late.status_code == 409 and late.json()["code"] == "TRIP_NOT_REPLACEABLE"


def test_crew_see_only_their_own_trips(world: World) -> None:
    _order, _truck, driver, helpers, trip = _scheduled(world)
    _o2, _t2, other_driver, _h2, other_trip = _scheduled(world)
    own = world.get("/api/v1/trips/assigned", driver).json()["items"]
    assert [row["trip_id"] for row in own] == [trip["trip_id"]]
    helper_view = world.get("/api/v1/trips/assigned", helpers[0]).json()["items"]
    assert [row["trip_id"] for row in helper_view] == [trip["trip_id"]]
    assert world.get(f"/api/v1/trips/{trip['trip_id']}", driver).status_code == 200
    assert world.get(f"/api/v1/trips/{other_trip['trip_id']}", driver).status_code == 404
    assert world.get(f"/api/v1/trips/{trip['trip_id']}", other_driver).status_code == 404
    assert world.get("/api/v1/trips", driver).status_code == 403
    assert world.get("/api/v1/trips", helpers[0]).status_code == 403
    everything = world.get("/api/v1/trips/assigned", world.dispatcher).json()["items"]
    assert len(everything) == 2
    assert world.get("/api/v1/trips", world.owner).status_code == 200
    assert (
        world.get("/api/v1/trips/assigned", world.employees.create((RoleCode.ACCOUNTING,))).status_code == 403
    )


def test_trip_list_filters(world: World) -> None:
    _order, truck, driver, _helpers, trip = _scheduled(world)
    _o2, _t2, _d2, _h2, other_trip = _scheduled(world)
    world.post(_trip_url(trip, "accept"), driver)
    accepted = world.get("/api/v1/trips", world.dispatcher, status="ACCEPTED").json()["items"]
    assert [row["trip_id"] for row in accepted] == [trip["trip_id"]]
    by_truck = world.get("/api/v1/trips", world.dispatcher, truck_id=str(truck.truck_id)).json()["items"]
    assert [row["trip_id"] for row in by_truck] == [trip["trip_id"]]
    by_order = world.get("/api/v1/trips", world.dispatcher, order_id=other_trip["order_id"]).json()["items"]
    assert [row["trip_id"] for row in by_order] == [other_trip["trip_id"]]
    assert world.get("/api/v1/trips", world.dispatcher, limit=101).status_code == 422


def test_dispatch_resources_show_who_can_take_work_and_why_not(world: World) -> None:
    free_truck = world.make_truck()
    broken = world.make_truck()
    world.set_truck_status(broken.truck_id, TruckStatus.MAINTENANCE)
    busy_truck, (busy_driver, busy_helpers) = world.make_truck(), world.crew()
    trip = world.assign_ok(world.make_order(), busy_truck, busy_driver, busy_helpers)
    expired_driver = world.make_driver(license_days=-3)
    free_driver = world.make_driver()
    body = world.get("/api/v1/dispatch/resources", world.dispatcher).json()
    trucks = {row["resource_id"]: row for row in body["trucks"]}
    assert trucks[str(free_truck.truck_id)]["can_receive_assignment"] is True
    assert trucks[str(broken.truck_id)]["reason"] == "MAINTENANCE"
    assert trucks[str(busy_truck.truck_id)]["blocking_trip_id"] == trip["trip_id"]
    assert trucks[str(free_truck.truck_id)]["capacity_tons"] == 25
    drivers = {row["resource_id"]: row for row in body["drivers"]}
    assert drivers[str(expired_driver.employee_id)]["reason"] == "LICENSE_EXPIRED"
    assert drivers[str(free_driver.employee_id)]["can_receive_assignment"] is True
    assert drivers[str(busy_driver.employee_id)]["reason"] == "IN_PROGRESS_TRIP"
    helpers = {row["resource_id"]: row for row in body["helpers"]}
    assert helpers[str(busy_helpers[0].employee_id)]["can_receive_assignment"] is False
    assert world.get("/api/v1/dispatch/resources", world.owner).status_code == 200
    assert (
        world.get("/api/v1/dispatch/resources", world.employees.create((RoleCode.DRIVER,))).status_code == 403
    )


def _trip(status: TripStatus, load: str) -> Trip:
    return Trip(
        trip_id=UUID(int=1),
        order_id=UUID(int=2),
        truck_id=UUID(int=3),
        load_tons=Decimal(load),
        status=status,
        driver_id=UUID(int=4),
        helper_ids=(UUID(int=5),),
        accepted_at=None,
        cleared_at=None,
        departed_at=None,
        delivered_at=None,
        closed_reason=None,
        created_by=None,
        created_at=datetime.now(UTC),
    )


def test_order_status_is_derived_from_its_trips() -> None:
    total = Decimal("100")
    assert derive_order_status(total, []) is OrderStatus.PENDING
    assert derive_order_status(total, [_trip(TripStatus.SCHEDULED, "40")]) is OrderStatus.PARTIALLY_ASSIGNED
    assert derive_order_status(total, [_trip(TripStatus.SCHEDULED, "100")]) is OrderStatus.SCHEDULED
    assert derive_order_status(total, [_trip(TripStatus.IN_TRANSIT, "40")]) is OrderStatus.IN_PROGRESS
    assert derive_order_status(total, [_trip(TripStatus.CANCELLED, "100")]) is OrderStatus.PENDING
    assert (
        derive_order_status(total, [_trip(TripStatus.FAILED, "60"), _trip(TripStatus.SCHEDULED, "40")])
        is OrderStatus.PARTIALLY_ASSIGNED
    )
    assert derive_order_status(total, [_trip(TripStatus.COMPLETED, "100")]) is OrderStatus.COMPLETED
    partial = [_trip(TripStatus.COMPLETED, "60")]
    assert derive_order_status(total, partial) is OrderStatus.IN_PROGRESS


def test_truck_status_is_derived_from_open_trips() -> None:
    assert derive_truck_status([]) is TruckStatus.AVAILABLE
    assert derive_truck_status([TripStatus.SCHEDULED]) is TruckStatus.ASSIGNED
    assert derive_truck_status([TripStatus.OR_UPLOADED, TripStatus.SCHEDULED]) is TruckStatus.ASSIGNED
    assert derive_truck_status([TripStatus.IN_TRANSIT]) is TruckStatus.IN_TRANSIT
