# ===== AI GENERATED: test_employees =====
# Purpose: Employee rules, object-level access, separation of duties, audit
# Inputs: fake employees and tokens
# Returns: pass/fail
# Flow:
# 1. Ownership and field-level projections (API1, API3)
# 2. Forbidden role pairs, exceptions, self lock-out guards
# 3. Activation, deactivation, identity link and audit trail

from uuid import uuid4

from backend.src.Entity.access import RoleCode


def _roles_body(*roles: RoleCode, reason: str | None = None) -> dict[str, object]:
    body: dict[str, object] = {"role_codes": [role.value for role in roles]}
    if reason is not None:
        body["exception_reason"] = reason
    return body


def test_driver_reads_only_their_own_record(client, employees, headers_for) -> None:
    driver = employees.create((RoleCode.DRIVER,))
    colleague = employees.create((RoleCode.DRIVER,))
    own = client.get(f"/api/v1/employees/{driver.employee_id}", headers=headers_for(driver))
    other = client.get(f"/api/v1/employees/{colleague.employee_id}", headers=headers_for(driver))
    assert own.status_code == 200
    assert other.status_code == 404
    listing = client.get("/api/v1/employees", headers=headers_for(driver)).json()
    assert [row["employee_id"] for row in listing["items"]] == [str(driver.employee_id)]


def test_dispatcher_sees_limited_fields_only(client, employees, headers_for) -> None:
    dispatcher = employees.create((RoleCode.DISPATCHER,))
    target = employees.create((RoleCode.DRIVER,), email="private@bm-test.example")
    response = client.get(f"/api/v1/employees/{target.employee_id}", headers=headers_for(dispatcher))
    assert response.status_code == 200
    assert set(response.json()) == {"employee_id", "full_name", "is_active"}


def test_hr_sees_full_detail_without_the_clerk_id(client, employees, headers_for) -> None:
    hr_user = employees.create((RoleCode.HR_PAYROLL,))
    target = employees.create((RoleCode.DRIVER,))
    body = client.get(f"/api/v1/employees/{target.employee_id}", headers=headers_for(hr_user)).json()
    assert "email" in body and "role_codes" in body
    assert "clerk_user_id" not in body


def test_unknown_fields_are_rejected_on_input(client, employees, headers_for) -> None:
    owner = employees.create((RoleCode.OWNER,))
    response = client.post(
        "/api/v1/employees",
        headers=headers_for(owner),
        json={"full_name": "A B", "email": "a@b.example", "is_active": True},
    )
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")


def test_new_employees_start_inactive_and_only_owner_activates(client, employees, headers_for) -> None:
    owner = employees.create((RoleCode.OWNER,))
    hr_user = employees.create((RoleCode.HR_PAYROLL,))
    created = client.post(
        "/api/v1/employees",
        headers=headers_for(hr_user),
        json={"full_name": "New Driver", "email": "new.driver@bm-test.example"},
    )
    assert created.status_code == 201
    new_id = created.json()["employee_id"]
    assert created.json()["is_active"] is False
    assert (
        client.post(f"/api/v1/employees/{new_id}/activate", headers=headers_for(hr_user)).status_code == 403
    )
    activated = client.post(f"/api/v1/employees/{new_id}/activate", headers=headers_for(owner))
    assert activated.status_code == 200 and activated.json()["is_active"] is True


def test_duplicate_email_is_a_conflict_ignoring_case(client, employees, headers_for) -> None:
    owner = employees.create((RoleCode.OWNER,))
    employees.create((RoleCode.DRIVER,), email="same@bm-test.example")
    response = client.post(
        "/api/v1/employees",
        headers=headers_for(owner),
        json={"full_name": "Dup", "email": "SAME@bm-test.example"},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "EMAIL_ALREADY_EXISTS"


def test_forbidden_role_pairs_need_an_owner_reason(client, employees, headers_for) -> None:
    owner = employees.create((RoleCode.OWNER,))
    target = employees.create((RoleCode.HR_PAYROLL,))
    url = f"/api/v1/employees/{target.employee_id}/roles"
    rejected = client.put(
        url, headers=headers_for(owner), json=_roles_body(RoleCode.HR_PAYROLL, RoleCode.ACCOUNTING)
    )
    assert rejected.status_code == 409
    assert rejected.json()["code"] == "ROLE_PAIR_FORBIDDEN"
    unchanged = client.get(f"/api/v1/employees/{target.employee_id}", headers=headers_for(owner)).json()
    assert unchanged["role_codes"] == ["HR_PAYROLL"]
    accepted = client.put(
        url,
        headers=headers_for(owner),
        json=_roles_body(
            RoleCode.HR_PAYROLL, RoleCode.ACCOUNTING, reason="Temporary cover while accounting is on leave"
        ),
    )
    assert accepted.status_code == 200
    audit = client.get("/api/v1/audit-logs", headers=headers_for(owner)).json()["items"]
    changed = [row for row in audit if row["action"] == "employee.roles_changed"]
    assert changed[0]["details"]["exception_reason"].startswith("Temporary cover")


def test_each_forbidden_pair_family_is_rejected(client, employees, headers_for) -> None:
    owner = employees.create((RoleCode.OWNER,))
    target = employees.create((RoleCode.HELPER,))
    url = f"/api/v1/employees/{target.employee_id}/roles"
    combos = [
        (RoleCode.DISPATCHER, RoleCode.HR_PAYROLL),
        (RoleCode.DISPATCHER, RoleCode.ACCOUNTING),
        (RoleCode.DRIVER, RoleCode.DISPATCHER),
        (RoleCode.HELPER, RoleCode.ACCOUNTING),
        (RoleCode.DRIVER, RoleCode.OWNER),
    ]
    for combo in combos:
        response = client.put(url, headers=headers_for(owner), json=_roles_body(*combo))
        assert response.status_code == 409, combo


def test_owner_may_also_be_dispatcher_without_exception(client, employees, headers_for) -> None:
    owner = employees.create((RoleCode.OWNER,))
    response = client.put(
        f"/api/v1/employees/{owner.employee_id}/roles",
        headers=headers_for(owner),
        json=_roles_body(RoleCode.OWNER, RoleCode.DISPATCHER),
    )
    assert response.status_code == 200
    me = client.get("/api/v1/me", headers=headers_for(owner)).json()
    assert me["capabilities"]["dispatch.assign"] == "FULL"
    assert me["capabilities"]["delivery_order.manage"] == "FULL"


def test_owner_cannot_remove_own_owner_role_or_deactivate_self(client, employees, headers_for) -> None:
    owner = employees.create((RoleCode.OWNER,))
    roles = client.put(
        f"/api/v1/employees/{owner.employee_id}/roles",
        headers=headers_for(owner),
        json=_roles_body(RoleCode.DISPATCHER),
    )
    assert roles.status_code == 409
    deactivate = client.post(f"/api/v1/employees/{owner.employee_id}/deactivate", headers=headers_for(owner))
    assert deactivate.status_code == 409
    assert deactivate.json()["code"] == "CANNOT_DEACTIVATE_SELF"


def test_deactivated_employee_loses_access_but_keeps_history(client, employees, headers_for) -> None:
    owner = employees.create((RoleCode.OWNER,))
    driver = employees.create((RoleCode.DRIVER,))
    assert client.get("/api/v1/me", headers=headers_for(driver)).status_code == 200
    response = client.post(f"/api/v1/employees/{driver.employee_id}/deactivate", headers=headers_for(owner))
    assert response.status_code == 200
    assert client.get("/api/v1/me", headers=headers_for(driver)).status_code == 403
    stored = client.get(f"/api/v1/employees/{driver.employee_id}", headers=headers_for(owner)).json()
    assert stored["is_active"] is False


def test_identity_link_enforces_one_account_per_person(client, employees, headers_for) -> None:
    owner = employees.create((RoleCode.OWNER,))
    first = employees.create((RoleCode.DRIVER,), linked=False)
    second = employees.create((RoleCode.DRIVER,), linked=False)
    first_link = client.put(
        f"/api/v1/employees/{first.employee_id}/identity",
        headers=headers_for(owner),
        json={"clerk_user_id": "user_shared123"},
    )
    second_link = client.put(
        f"/api/v1/employees/{second.employee_id}/identity",
        headers=headers_for(owner),
        json={"clerk_user_id": "user_shared123"},
    )
    assert first_link.status_code == 200 and first_link.json()["has_account"] is True
    assert second_link.status_code == 409


def test_mutations_write_audit_records_with_trace_ids(client, employees, headers_for) -> None:
    owner = employees.create((RoleCode.OWNER,))
    response = client.post(
        "/api/v1/employees",
        headers=headers_for(owner),
        json={"full_name": "Audit Subject", "email": "audit.subject@bm-test.example"},
    )
    audit = client.get("/api/v1/audit-logs", headers=headers_for(owner)).json()["items"]
    created = [row for row in audit if row["action"] == "employee.created"]
    assert created and created[0]["entity_id"] == response.json()["employee_id"]
    assert created[0]["actor_employee_id"] == str(owner.employee_id)
    assert created[0]["trace_id"] == response.headers["x-trace-id"]
    assert "audit.subject@bm-test.example" not in str(created[0]["details"])


def test_missing_employee_returns_problem_json_404(client, employees, headers_for) -> None:
    owner = employees.create((RoleCode.OWNER,))
    response = client.get(f"/api/v1/employees/{uuid4()}", headers=headers_for(owner))
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")


def test_audit_page_size_is_capped(client, employees, headers_for) -> None:
    owner = employees.create((RoleCode.OWNER,))
    response = client.get("/api/v1/audit-logs?limit=1000", headers=headers_for(owner))
    assert response.status_code == 422
