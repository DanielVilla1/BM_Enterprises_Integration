# ===== AI GENERATED: dispatch_revalidation_tests =====
# Purpose: Ensure a reservation cannot retain stale permission to depart
# Inputs: Assigned trips and later changes to fleet, crew and licenses
# Returns: API regression assertions
# Flow:
# 1. Assign and accept a valid trip
# 2. Change eligibility before clearance or departure
# 3. Assert rejection leaves status and audit history unchanged


from datetime import timedelta

import pytest

from backend.src.Entity.clock import manila_today
from backend.src.Repository.employee_repository import EmployeeRepository
from backend.src.Repository.fleet_repositories import DriverLicenseRepository, TruckRepository
from backend.tests.dispatch_support import World


@pytest.mark.parametrize("action", ["clear-dispatch", "depart"])
@pytest.mark.parametrize(
    ("changed_resource", "expected_code"),
    [
        ("helper", "EMPLOYEE_INACTIVE"),
        ("license", "DRIVER_LICENSE_EXPIRED"),
        ("capacity", "CAPACITY_EXCEEDED"),
    ],
)
def test_dispatch_rechecks_current_eligibility(
    client, session_factory, employees, action: str, changed_resource: str, expected_code: str
) -> None:
    world = World(client, session_factory, employees)
    truck = world.make_truck()
    driver, helpers = world.crew()
    trip = world.assign_ok(world.make_order(), truck, driver, helpers)
    trip_url = f"/api/v1/trips/{trip['trip_id']}"
    assert world.post(f"{trip_url}/accept", driver).status_code == 200
    expected_status = "ACCEPTED"
    if action == "depart":
        assert world.post(f"{trip_url}/clear-dispatch", world.dispatcher).status_code == 200
        expected_status = "CLEARED_FOR_DISPATCH"
    with session_factory() as session:
        if changed_resource == "helper":
            EmployeeRepository(session).set_active(helpers[0].employee_id, False)
        elif changed_resource == "license":
            DriverLicenseRepository(session).upsert(
                driver.employee_id, "N01-00-999999", manila_today() - timedelta(days=1)
            )
        else:
            TruckRepository(session).update(truck.truck_id, {"capacity_tons": 10})
        session.commit()
    before_audit = world.get("/api/v1/audit-logs", world.owner).json()["items"]
    response = world.post(f"{trip_url}/{action}", driver if action == "depart" else world.dispatcher)
    assert response.status_code == 409
    assert response.json()["code"] == expected_code
    assert world.get(trip_url, world.dispatcher).json()["status"] == expected_status
    after_audit = world.get("/api/v1/audit-logs", world.owner).json()["items"]
    assert after_audit == before_audit


@pytest.mark.parametrize("unlinked_role", ["driver", "helper"])
def test_driver_needs_a_sign_in_link_but_helper_does_not(
    client, session_factory, employees, unlinked_role: str
) -> None:
    """A driver must be able to accept/confirm; non-operating helpers need no login."""
    world = World(client, session_factory, employees)
    driver, helpers = world.crew()
    selected = driver if unlinked_role == "driver" else helpers[0]
    with session_factory() as session:
        EmployeeRepository(session).set_clerk_user_id(selected.employee_id, None)
        session.commit()
    response = world.assign(world.make_order(), world.make_truck(), driver, helpers)
    if unlinked_role == "driver":
        assert response.status_code == 409
        assert response.json()["code"] == "DRIVER_ACCOUNT_REQUIRED"
        resources = world.get("/api/v1/dispatch/resources", world.dispatcher).json()
        listed = next(row for row in resources["drivers"] if row["resource_id"] == str(driver.employee_id))
        assert listed["can_receive_assignment"] is False
        assert listed["reason"] == "ACCOUNT_NOT_LINKED"
    else:
        assert response.status_code == 201
