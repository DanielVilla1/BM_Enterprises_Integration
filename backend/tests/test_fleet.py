# ===== AI GENERATED: test_fleet =====
# Purpose: Trucks, maintenance and driver licenses with role and field rules
# Inputs: fake trucks, drivers and employees
# Returns: pass/fail
# Flow:
# 1. Truck records, plate rules, maintenance status transitions
# 2. License visibility by level: Full / View / Own / Ltd
# 3. License numbers never appear in audit records

from datetime import timedelta
from uuid import UUID

import pytest

from backend.src.Entity.access import RoleCode
from backend.src.Entity.clock import manila_today
from backend.src.Entity.fleet import LicenseValidity, TruckStatus, license_validity
from backend.src.Repository.fleet_repositories import TruckRepository

TRUCKS = "/api/v1/trucks"


@pytest.fixture
def fleet_manager(employees):
    return employees.create((RoleCode.FLEET_MANAGER,))


def _make_truck(client, headers, plate: str = "ABC 1234", capacity: float = 25) -> dict:
    response = client.post(
        TRUCKS,
        headers=headers,
        json={"plate_number": plate, "description": "10-wheeler", "capacity_tons": capacity},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_fleet_manager_creates_trucks_with_normalized_unique_plates(
    client, fleet_manager, headers_for
) -> None:
    headers = headers_for(fleet_manager)
    truck = _make_truck(client, headers, plate="abc  1234")
    assert truck["plate_number"] == "ABC 1234"
    assert truck["status"] == "AVAILABLE" and truck["is_active"] is True
    assert truck["capacity_tons"] == 25
    duplicate = client.post(TRUCKS, headers=headers, json={"plate_number": "ABC 1234", "capacity_tons": 10})
    assert duplicate.status_code == 409 and duplicate.json()["code"] == "PLATE_ALREADY_EXISTS"


@pytest.mark.parametrize("capacity", [0, -1, 100.5, 10.12345])
def test_invalid_capacities_are_rejected(client, fleet_manager, headers_for, capacity) -> None:
    response = client.post(
        TRUCKS,
        headers=headers_for(fleet_manager),
        json={"plate_number": "XYZ 999", "capacity_tons": capacity},
    )
    assert response.status_code == 422


def test_dispatcher_can_view_but_not_change_trucks(client, employees, fleet_manager, headers_for) -> None:
    truck = _make_truck(client, headers_for(fleet_manager))
    dispatcher = employees.create((RoleCode.DISPATCHER,))
    headers = headers_for(dispatcher)
    assert client.get(TRUCKS, headers=headers).status_code == 200
    assert client.get(f"{TRUCKS}/{truck['truck_id']}", headers=headers).status_code == 200
    assert (
        client.post(TRUCKS, headers=headers, json={"plate_number": "NEW 111", "capacity_tons": 5}).status_code
        == 403
    )
    assert (
        client.patch(f"{TRUCKS}/{truck['truck_id']}", headers=headers, json={"capacity_tons": 5}).status_code
        == 403
    )
    start = client.post(
        f"{TRUCKS}/{truck['truck_id']}/maintenance", headers=headers, json={"reason": "Brakes"}
    )
    assert start.status_code == 403
    for role in (RoleCode.DRIVER, RoleCode.HELPER, RoleCode.HR_PAYROLL, RoleCode.ACCOUNTING):
        assert client.get(TRUCKS, headers=headers_for(employees.create((role,)))).status_code == 403


def test_maintenance_cycle_updates_status_and_history(client, fleet_manager, headers_for) -> None:
    headers = headers_for(fleet_manager)
    truck = _make_truck(client, headers)
    base = f"{TRUCKS}/{truck['truck_id']}"
    started = client.post(f"{base}/maintenance", headers=headers, json={"reason": "Brake pads worn"})
    assert started.status_code == 201 and started.json()["ended_at"] is None
    assert client.get(base, headers=headers).json()["status"] == "MAINTENANCE"
    again = client.post(f"{base}/maintenance", headers=headers, json={"reason": "Second"})
    assert again.status_code == 409 and again.json()["code"] == "ALREADY_IN_MAINTENANCE"
    done = client.post(f"{base}/maintenance/complete", headers=headers)
    assert done.status_code == 200 and done.json()["ended_at"] is not None
    assert client.get(base, headers=headers).json()["status"] == "AVAILABLE"
    nothing = client.post(f"{base}/maintenance/complete", headers=headers)
    assert nothing.status_code == 409 and nothing.json()["code"] == "NOT_IN_MAINTENANCE"
    history = client.get(f"{base}/maintenance", headers=headers).json()
    assert len(history) == 1 and history[0]["reason"] == "Brake pads worn"
    in_maintenance = client.get(TRUCKS, headers=headers, params={"status": "MAINTENANCE"}).json()["items"]
    assert in_maintenance == []


def test_busy_trucks_cannot_enter_maintenance_or_be_retired(
    client, session_factory, fleet_manager, headers_for
) -> None:
    headers = headers_for(fleet_manager)
    truck = _make_truck(client, headers)
    with session_factory() as session:
        TruckRepository(session).set_status(UUID(truck["truck_id"]), TruckStatus.ASSIGNED)
        session.commit()
    base = f"{TRUCKS}/{truck['truck_id']}"
    start = client.post(f"{base}/maintenance", headers=headers, json={"reason": "Noise in engine"})
    assert start.status_code == 409 and start.json()["code"] == "TRUCK_BUSY"
    retire = client.patch(base, headers=headers, json={"is_active": False})
    assert retire.status_code == 409 and retire.json()["code"] == "TRUCK_BUSY"


def test_truck_updates_are_partial_and_audited(client, employees, fleet_manager, headers_for) -> None:
    headers = headers_for(fleet_manager)
    truck = _make_truck(client, headers)
    other = _make_truck(client, headers, plate="DEF 5678")
    base = f"{TRUCKS}/{truck['truck_id']}"
    assert client.patch(base, headers=headers, json={"capacity_tons": 30}).json()["capacity_tons"] == 30
    clash = client.patch(base, headers=headers, json={"plate_number": other["plate_number"].lower()})
    assert clash.status_code == 409
    assert client.patch(base, headers=headers, json={}).status_code == 422
    assert client.patch(base, headers=headers, json={"capacity_tons": None}).status_code == 422
    assert client.patch(base, headers=headers, json={"status": "IN_TRANSIT"}).status_code == 422
    owner = employees.create((RoleCode.OWNER,))
    audit = client.get("/api/v1/audit-logs", headers=headers_for(owner)).json()["items"]
    updated = [row for row in audit if row["action"] == "truck.updated"]
    assert updated[0]["details"] == {"fields": ["capacity_tons"]}


def test_missing_truck_is_a_problem_json_404(client, fleet_manager, headers_for) -> None:
    response = client.get(
        f"{TRUCKS}/00000000-0000-4000-8000-000000000009", headers=headers_for(fleet_manager)
    )
    assert response.status_code == 404 and response.json()["code"] == "TRUCK_NOT_FOUND"


def _license_url(employee_id) -> str:
    return f"/api/v1/employees/{employee_id}/driver-license"


def _save_license(client, headers, employee_id, number="N01-12-345678", days_ahead=400):
    expiry = (manila_today() + timedelta(days=days_ahead)).isoformat()
    return client.put(
        _license_url(employee_id), headers=headers, json={"license_number": number, "expiry_date": expiry}
    )


def test_fleet_manager_saves_a_license_and_validity_is_derived(
    client, employees, fleet_manager, headers_for
) -> None:
    driver = employees.create((RoleCode.DRIVER,))
    saved = _save_license(client, headers_for(fleet_manager), driver.employee_id, "n01-12-345678")
    assert saved.status_code == 200
    assert saved.json()["license_number"] == "N01-12-345678"
    assert saved.json()["validity"] == "VALID"
    soon = _save_license(
        client, headers_for(fleet_manager), driver.employee_id, "N01-12-345678", days_ahead=10
    )
    assert soon.json()["validity"] == "EXPIRING_SOON"
    expired = _save_license(
        client, headers_for(fleet_manager), driver.employee_id, "N01-12-345678", days_ahead=-1
    )
    assert expired.json()["validity"] == "EXPIRED"


def test_license_visibility_follows_the_matrix_levels(client, employees, fleet_manager, headers_for) -> None:
    driver = employees.create((RoleCode.DRIVER,))
    other_driver = employees.create((RoleCode.DRIVER,))
    _save_license(client, headers_for(fleet_manager), driver.employee_id)
    url = _license_url(driver.employee_id)

    own = client.get(url, headers=headers_for(driver))
    assert own.status_code == 200 and own.json()["license_number"] == "N01-12-345678"
    assert client.get(url, headers=headers_for(other_driver)).status_code == 404

    dispatcher = client.get(url, headers=headers_for(employees.create((RoleCode.DISPATCHER,))))
    assert dispatcher.status_code == 200
    assert set(dispatcher.json()) == {"employee_id", "validity"}
    assert "N01" not in dispatcher.text

    for role in (RoleCode.OWNER, RoleCode.HR_PAYROLL, RoleCode.FLEET_MANAGER):
        full = client.get(url, headers=headers_for(employees.create((role,))))
        assert full.status_code == 200 and full.json()["license_number"] == "N01-12-345678"

    for role in (RoleCode.HELPER, RoleCode.ACCOUNTING):
        assert client.get(url, headers=headers_for(employees.create((role,)))).status_code == 403


def test_only_owner_and_fleet_manager_can_write_licenses(client, employees, headers_for) -> None:
    driver = employees.create((RoleCode.DRIVER,))
    for role in (RoleCode.DISPATCHER, RoleCode.HR_PAYROLL, RoleCode.DRIVER):
        person = employees.create((role,))
        assert _save_license(client, headers_for(person), driver.employee_id).status_code == 403
    owner = employees.create((RoleCode.OWNER,))
    assert _save_license(client, headers_for(owner), driver.employee_id).status_code == 200


def test_license_rules_for_non_drivers_duplicates_and_bad_dates(
    client, employees, fleet_manager, headers_for
) -> None:
    headers = headers_for(fleet_manager)
    helper = employees.create((RoleCode.HELPER,))
    not_driver = _save_license(client, headers, helper.employee_id)
    assert not_driver.status_code == 409 and not_driver.json()["code"] == "NOT_A_DRIVER"
    first = employees.create((RoleCode.DRIVER,))
    second = employees.create((RoleCode.DRIVER,))
    assert _save_license(client, headers, first.employee_id).status_code == 200
    duplicate = _save_license(client, headers, second.employee_id)
    assert duplicate.status_code == 409 and duplicate.json()["code"] == "LICENSE_NUMBER_EXISTS"
    far = _save_license(client, headers, second.employee_id, "N02-00-000001", days_ahead=365 * 21)
    assert far.status_code == 422 and far.json()["code"] == "INVALID_EXPIRY_DATE"
    short = _save_license(client, headers, second.employee_id, "ab")
    assert short.status_code == 422
    missing = client.get(_license_url(second.employee_id), headers=headers)
    assert missing.status_code == 404 and missing.json()["code"] == "LICENSE_NOT_FOUND"


def test_license_numbers_never_reach_the_audit_log(client, employees, fleet_manager, headers_for) -> None:
    driver = employees.create((RoleCode.DRIVER,))
    _save_license(client, headers_for(fleet_manager), driver.employee_id, "N09-99-999999")
    owner = employees.create((RoleCode.OWNER,))
    response = client.get("/api/v1/audit-logs", headers=headers_for(owner))
    assert "N09-99-999999" not in response.text
    saved = [row for row in response.json()["items"] if row["action"] == "driver_license.saved"]
    assert saved and saved[0]["details"] == {"validity": "VALID"}


def test_license_validity_boundaries() -> None:
    today = manila_today()
    assert license_validity(today - timedelta(days=1), today) is LicenseValidity.EXPIRED
    assert license_validity(today, today) is LicenseValidity.EXPIRING_SOON
    assert license_validity(today + timedelta(days=30), today) is LicenseValidity.EXPIRING_SOON
    assert license_validity(today + timedelta(days=31), today) is LicenseValidity.VALID
