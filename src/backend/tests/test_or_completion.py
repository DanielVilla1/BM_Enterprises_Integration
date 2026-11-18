# ===== AI GENERATED: test_or_completion =====
# Purpose: Receipt confirmation completes the trip (TRIP-04, TXN-01, IDEM-01, FP-02)
# Inputs: delivered trips with uploaded ORs
# Returns: pass/fail
# 1. Only the assigned driver confirms; a stored signed OR is required
# 2. Repeats with the same Idempotency-Key have no extra effect
# 3. A failed commit changes nothing and a retry succeeds exactly once
# 4. The Owner can correct a mistaken confirmation, with limits

# AI MODIFIED: Standardize formatting and workflow documentation conventions.

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from fastapi import Depends
from sqlalchemy.exc import OperationalError

from backend.main import app
from backend.src.Entity.access import RoleCode
from backend.src.Entity.dispatch import TripStatus
from backend.src.providers import (
    get_image_sanitizer,
    get_object_storage,
    get_or_service,
    get_session,
)
from backend.tests.conftest import auth_headers
from backend.tests.dispatch_support import DeliveredTrip, World
from backend.tests.image_support import make_jpeg


@pytest.fixture
def world(client, session_factory, employees) -> World:
    return World(client, session_factory, employees)


def _upload(world: World, delivered: DeliveredTrip, kind: str = "SIGNED_OR"):
    return world.client.post(
        f"/api/v1/trips/{delivered.trip_id}/or-documents",
        headers=auth_headers(delivered.driver),
        files={"file": ("scan.jpg", make_jpeg(), "image/jpeg")},
        data={"kind": kind},
    )


def _uploaded(world: World, load: float = 20, order_weight: str = "20") -> DeliveredTrip:
    delivered = world.delivered_trip(load, order_weight)
    assert _upload(world, delivered).status_code == 201
    return delivered


def _confirm(
    world: World, delivered: DeliveredTrip, key: str = "confirm-key-0001", actor=None, received_at=None
):
    moment = received_at or datetime.now(UTC)
    return world.client.post(
        f"/api/v1/trips/{delivered.trip_id}/confirm-receipt",
        headers={**auth_headers(actor or delivered.driver), "Idempotency-Key": key},
        json={"received_at": moment.isoformat()},
    )


def test_driver_confirmation_completes_the_trip_and_frees_resources(world: World) -> None:
    delivered = _uploaded(world)
    response = _confirm(world, delivered)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "COMPLETED"
    assert body["receipt_confirmed_at"] is not None and body["receipt_received_at"] is not None
    assert world.truck_status(delivered.truck.truck_id) == "AVAILABLE"
    assert world.order_status(delivered.order_id) == "COMPLETED"
    audit = world.get("/api/v1/audit-logs", world.owner).json()["items"]
    confirmed = [row for row in audit if row["action"] == "trip.receipt_confirmed"]
    assert len(confirmed) == 1 and confirmed[0]["actor_employee_id"] == str(delivered.driver.employee_id)
    assert confirmed[0]["details"] == {"stamped_copy": False}


def test_a_partly_assigned_order_stays_in_progress_after_one_trip_completes(world: World) -> None:
    delivered = _uploaded(world, load=20, order_weight="50")
    assert _confirm(world, delivered).status_code == 200
    assert world.order_status(delivered.order_id) == "IN_PROGRESS"


def test_only_the_assigned_driver_can_confirm_receipt(world: World) -> None:
    delivered = _uploaded(world)
    assert _confirm(world, delivered, actor=world.make_driver()).status_code == 404
    for actor in (world.dispatcher, world.owner, delivered.helpers[0]):
        assert _confirm(world, delivered, actor=actor).status_code == 403
    assert world.get(f"/api/v1/trips/{delivered.trip_id}", delivered.driver).json()["status"] == "OR_UPLOADED"


def test_confirmation_requires_a_stored_signed_or(world: World) -> None:
    delivered = world.delivered_trip()
    response = _confirm(world, delivered)
    assert response.status_code == 409 and response.json()["code"] == "SIGNED_OR_REQUIRED"
    assert (
        world.get(f"/api/v1/trips/{delivered.trip_id}", delivered.driver).json()["status"]
        == "DELIVERED_OR_PENDING"
    )


def test_a_stamped_copy_is_optional_supporting_evidence(world: World) -> None:
    without = _uploaded(world)
    assert _confirm(world, without).status_code == 200
    with_copy = _uploaded(world)
    assert _upload(world, with_copy, "STAMPED_COPY").status_code == 201
    assert _confirm(world, with_copy, key="confirm-key-0002").status_code == 200
    audit = world.get("/api/v1/audit-logs", world.owner).json()["items"]
    flags = sorted(
        row["details"]["stamped_copy"] for row in audit if row["action"] == "trip.receipt_confirmed"
    )
    assert flags == [False, True]
    assert _upload(world, with_copy, "STAMPED_COPY").status_code == 201


def test_signed_or_cannot_change_after_completion(world: World) -> None:
    delivered = _uploaded(world)
    _confirm(world, delivered)
    response = _upload(world, delivered)
    assert response.status_code == 409 and response.json()["code"] == "TRIP_ALREADY_COMPLETED"


def test_idempotency_key_is_required_and_validated(world: World) -> None:
    delivered = _uploaded(world)
    url = f"/api/v1/trips/{delivered.trip_id}/confirm-receipt"
    body = {"received_at": datetime.now(UTC).isoformat()}
    missing = world.client.post(url, headers=auth_headers(delivered.driver), json=body)
    assert missing.status_code == 422 and missing.headers["content-type"].startswith(
        "application/problem+json"
    )
    short = world.client.post(
        url, headers={**auth_headers(delivered.driver), "Idempotency-Key": "abc"}, json=body
    )
    assert short.status_code == 422
    assert world.get(f"/api/v1/trips/{delivered.trip_id}", delivered.driver).json()["status"] == "OR_UPLOADED"


def test_repeating_a_confirmation_with_the_same_key_has_no_extra_effect(world: World) -> None:
    delivered = _uploaded(world)
    first = _confirm(world, delivered)
    again = _confirm(world, delivered)
    assert first.status_code == 200 and again.status_code == 200
    assert again.json()["receipt_confirmed_at"] == first.json()["receipt_confirmed_at"]
    audit = world.get("/api/v1/audit-logs", world.owner).json()["items"]
    assert len([row for row in audit if row["action"] == "trip.receipt_confirmed"]) == 1


def test_a_new_key_after_completion_is_a_conflict_not_a_second_completion(world: World) -> None:
    delivered = _uploaded(world)
    assert _confirm(world, delivered, key="confirm-key-aaaa").status_code == 200
    repeat = _confirm(world, delivered, key="confirm-key-bbbb")
    assert repeat.status_code == 409 and repeat.json()["code"] == "TRIP_ALREADY_COMPLETED"
    audit = world.get("/api/v1/audit-logs", world.owner).json()["items"]
    assert len([row for row in audit if row["action"] == "trip.receipt_confirmed"]) == 1


def test_a_key_already_used_for_another_trip_is_refused(world: World) -> None:
    first = _uploaded(world)
    assert _confirm(world, first, key="shared-key-0001").status_code == 200
    second_trip = world.assign_ok(world.make_order(), first.truck, first.driver, first.helpers)
    base = f"/api/v1/trips/{second_trip['trip_id']}"
    world.post(f"{base}/accept", first.driver)
    world.post(f"{base}/clear-dispatch", world.dispatcher)
    world.post(f"{base}/depart", first.driver)
    delivered_second = world.post(f"{base}/deliver", first.driver).json()
    second = DeliveredTrip(first.order_id, first.truck, first.driver, first.helpers, delivered_second)
    assert _upload(world, second).status_code == 201
    reused = _confirm(world, second, key="shared-key-0001")
    assert reused.status_code == 409 and reused.json()["code"] == "IDEMPOTENCY_KEY_REUSED"
    assert world.get(f"/api/v1/trips/{second.trip_id}", first.driver).json()["status"] == "OR_UPLOADED"
    assert _confirm(world, second, key="shared-key-0002").status_code == 200


def test_receipt_time_must_be_sensible(world: World) -> None:
    delivered = _uploaded(world)
    future = datetime.now(UTC) + timedelta(hours=1)
    response = _confirm(world, delivered, received_at=future)
    assert response.status_code == 422 and response.json()["code"] == "INVALID_RECEIPT_TIME"
    past = datetime.now(UTC) - timedelta(days=2)
    assert _confirm(world, delivered, received_at=past).json()["code"] == "INVALID_RECEIPT_TIME"
    naive = world.client.post(
        f"/api/v1/trips/{delivered.trip_id}/confirm-receipt",
        headers={**auth_headers(delivered.driver), "Idempotency-Key": "confirm-key-0009"},
        json={"received_at": "2030-01-01T10:00:00"},
    )
    assert naive.status_code == 422
    assert world.get(f"/api/v1/trips/{delivered.trip_id}", delivered.driver).json()["status"] == "OR_UPLOADED"


def test_a_failed_commit_changes_nothing_and_the_retry_succeeds_exactly_once(world: World) -> None:
    delivered = _uploaded(world)
    attempts = {"failures_left": 1}

    def flaky_service(
        session=Depends(get_session),
        storage=Depends(get_object_storage),
        sanitizer=Depends(get_image_sanitizer),
    ):
        service = get_or_service(session, storage, sanitizer)
        real_commit = service._unit_of_work.commit

        def commit() -> None:
            if attempts["failures_left"]:
                attempts["failures_left"] -= 1
                raise OperationalError("COMMIT", {}, Exception("connection lost"))
            real_commit()

        service._unit_of_work = SimpleNamespace(commit=commit, rollback=lambda: None)
        return service

    app.dependency_overrides[get_or_service] = flaky_service
    failed = _confirm(world, delivered)
    assert failed.status_code == 503 and failed.json()["code"] == "DATABASE_UNAVAILABLE"
    trip = world.get(f"/api/v1/trips/{delivered.trip_id}", delivered.driver).json()
    assert trip["status"] == "OR_UPLOADED" and trip["receipt_confirmed_at"] is None
    assert world.truck_status(delivered.truck.truck_id) == "ASSIGNED"
    audit = world.get("/api/v1/audit-logs", world.owner).json()["items"]
    assert not [row for row in audit if row["action"] == "trip.receipt_confirmed"]
    retried = _confirm(world, delivered)
    assert retried.status_code == 200 and retried.json()["status"] == "COMPLETED"
    audit = world.get("/api/v1/audit-logs", world.owner).json()["items"]
    assert len([row for row in audit if row["action"] == "trip.receipt_confirmed"]) == 1
    assert _confirm(world, delivered).status_code == 200


def test_the_block_lifts_when_the_driver_confirms_the_previous_trip(world: World) -> None:
    first = _uploaded(world)
    order_id = world.make_order()
    second = world.assign_ok(order_id, first.truck, first.driver, first.helpers)
    second_base = f"/api/v1/trips/{second['trip_id']}"
    assert world.post(f"{second_base}/accept", first.driver).status_code == 200
    blocked = world.post(f"{second_base}/clear-dispatch", world.dispatcher)
    assert blocked.status_code == 409 and blocked.json()["blocking_trip_ids"] == [first.trip_id]
    assert _confirm(world, first).status_code == 200
    assert world.post(f"{second_base}/clear-dispatch", world.dispatcher).status_code == 200
    assert world.truck_status(first.truck.truck_id) == "ASSIGNED"


def _correct(world: World, delivered: DeliveredTrip, actor=None, reason: str = "Receipt was never stamped"):
    return world.client.post(
        f"/api/v1/trips/{delivered.trip_id}/receipt-correction",
        headers=auth_headers(actor or world.owner),
        json={"reason": reason},
    )


def test_owner_can_reopen_a_mistaken_confirmation(world: World) -> None:
    delivered = _uploaded(world)
    assert _correct(world, delivered).json()["code"] == "NOT_COMPLETED"
    _confirm(world, delivered)
    response = _correct(world, delivered)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "OR_UPLOADED"
    assert body["receipt_confirmed_at"] is None and body["receipt_received_at"] is None
    assert world.truck_status(delivered.truck.truck_id) == "ASSIGNED"
    assert world.order_status(delivered.order_id) == "IN_PROGRESS"
    audit = world.get("/api/v1/audit-logs", world.owner).json()["items"]
    correction = next(row for row in audit if row["action"] == "trip.receipt_correction")
    assert correction["details"]["reason"] == "Receipt was never stamped"
    assert _confirm(world, delivered, key="confirm-key-0777").status_code == 200


def test_only_the_owner_can_correct_and_a_reason_is_required(world: World) -> None:
    delivered = _uploaded(world)
    _confirm(world, delivered)
    for actor in (world.dispatcher, delivered.driver, world.employees.create((RoleCode.ACCOUNTING,))):
        assert _correct(world, delivered, actor=actor).status_code == 403
    assert _correct(world, delivered, reason="no").status_code == 422
    assert world.get(f"/api/v1/trips/{delivered.trip_id}", delivered.driver).json()["status"] == "COMPLETED"


def test_correction_reopens_a_later_clearance_but_not_a_departed_trip(world: World) -> None:
    first = _uploaded(world)
    second = world.assign_ok(world.make_order(), first.truck, first.driver, first.helpers)
    second_base = f"/api/v1/trips/{second['trip_id']}"
    world.post(f"{second_base}/accept", first.driver)
    _confirm(world, first)
    assert world.post(f"{second_base}/clear-dispatch", world.dispatcher).status_code == 200
    reopened = _correct(world, first)
    assert reopened.status_code == 200
    later = world.get(second_base, world.dispatcher).json()
    assert later["status"] == "ACCEPTED" and later["cleared_at"] is None
    assert _confirm(world, first, key="confirm-key-0888").status_code == 200
    world.post(f"{second_base}/clear-dispatch", world.dispatcher)
    assert world.post(f"{second_base}/depart", first.driver).status_code == 200
    refused = _correct(world, first)
    assert refused.status_code == 409 and refused.json()["code"] == "CORRECTION_NOT_POSSIBLE"
    assert refused.json()["blocking_trip_ids"] == [second["trip_id"]]
    assert (
        world.get(f"/api/v1/trips/{first.trip_id}", world.owner).json()["status"]
        == TripStatus.COMPLETED.value
    )


@pytest.mark.parametrize("later_status", [TripStatus.COMPLETED, TripStatus.FAILED])
def test_correction_remains_blocked_after_later_trip_closes(world: World, later_status: TripStatus) -> None:
    """Closing a later trip must not erase the fact that these resources departed."""
    first = _uploaded(world)
    assert _confirm(world, first).status_code == 200
    second = world.assign_ok(world.make_order(), first.truck, first.driver, first.helpers)
    second_base = f"/api/v1/trips/{second['trip_id']}"
    assert world.post(f"{second_base}/accept", first.driver).status_code == 200
    assert world.post(f"{second_base}/clear-dispatch", world.dispatcher).status_code == 200
    assert world.post(f"{second_base}/depart", first.driver).status_code == 200
    world.force_status(second["trip_id"], later_status)
    refused = _correct(world, first)
    assert refused.status_code == 409
    assert refused.json()["code"] == "CORRECTION_NOT_POSSIBLE"
    assert second["trip_id"] in refused.json()["blocking_trip_ids"]


def test_correction_checks_a_truck_replaced_on_a_later_closed_trip(world: World) -> None:
    """Truck history matters even when no crew member links the two trips."""
    first = _uploaded(world)
    assert _confirm(world, first).status_code == 200
    other_driver, other_helpers = world.crew()
    second = world.assign_ok(world.make_order(), first.truck, other_driver, other_helpers)
    second_base = f"/api/v1/trips/{second['trip_id']}"
    assert world.post(f"{second_base}/accept", other_driver).status_code == 200
    assert world.post(f"{second_base}/clear-dispatch", world.dispatcher).status_code == 200
    assert world.post(f"{second_base}/depart", other_driver).status_code == 200
    replacement = world.make_truck()
    response = world.post(
        f"{second_base}/truck-replacement",
        world.dispatcher,
        {
            "replacement_truck_id": str(replacement.truck_id),
            "reason": "Operational truck change",
            "original_truck_needs_maintenance": False,
        },
    )
    assert response.status_code == 200
    world.force_status(second["trip_id"], TripStatus.COMPLETED)
    refused = _correct(world, first)
    assert refused.status_code == 409
    assert second["trip_id"] in refused.json()["blocking_trip_ids"]
