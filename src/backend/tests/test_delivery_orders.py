# ===== AI GENERATED: test_delivery_orders =====
# Purpose: Clients and delivery orders (DO-01, CT-01) with role rules
# Inputs: fake clients, orders and employees
# Returns: pass/fail
# Flow:
# 1. Valid order -> 201 PENDING; invalid weight, date, client rejected
# 2. Only Dispatcher writes; Owner and Accounting read
# 3. Edit/cancel only while PENDING; every change is audited

from datetime import timedelta

import pytest

from backend.src.Entity.access import RoleCode
from backend.src.Entity.clock import manila_today

ORDERS = "/api/v1/delivery-orders"
CLIENTS = "/api/v1/clients"


@pytest.fixture
def dispatcher(employees):
    return employees.create((RoleCode.DISPATCHER,))


def _make_client(client, headers, name: str = "Fake Steel Corp") -> str:
    response = client.post(CLIENTS, headers=headers, json={"name": name, "address": "Plant Road 1"})
    assert response.status_code == 201, response.text
    return response.json()["client_id"]


def _order_body(client_id: str, **overrides) -> dict[str, object]:
    body: dict[str, object] = {
        "client_id": client_id,
        "client_reference": "PO-1001",
        "pickup_location": "Plant gate 4, Steel City",
        "delivery_location": "Warehouse 7, Harbour Zone",
        "scheduled_date": manila_today().isoformat(),
        "total_weight_tons": 48.5,
    }
    body.update(overrides)
    return body


def test_valid_order_is_created_as_pending_with_a_schema_valid_body(client, dispatcher, headers_for) -> None:
    headers = headers_for(dispatcher)
    client_id = _make_client(client, headers)
    response = client.post(ORDERS, headers=headers, json=_order_body(client_id))
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "PENDING"
    assert body["total_weight_tons"] == 48.5
    assert set(body) == {
        "order_id",
        "client_id",
        "client_reference",
        "pickup_location",
        "delivery_location",
        "scheduled_date",
        "total_weight_tons",
        "status",
        "notes",
        "cancellation_reason",
        "created_at",
    }
    fetched = client.get(f"{ORDERS}/{body['order_id']}", headers=headers)
    assert fetched.status_code == 200 and fetched.json() == body


@pytest.mark.parametrize("weight", [0, -5, 100000.001, 12.3456])
def test_invalid_weights_are_rejected(client, dispatcher, headers_for, weight) -> None:
    headers = headers_for(dispatcher)
    client_id = _make_client(client, headers)
    response = client.post(ORDERS, headers=headers, json=_order_body(client_id, total_weight_tons=weight))
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")


def test_past_dates_are_rejected_but_today_is_allowed(client, dispatcher, headers_for) -> None:
    headers = headers_for(dispatcher)
    client_id = _make_client(client, headers)
    yesterday = (manila_today() - timedelta(days=1)).isoformat()
    rejected = client.post(ORDERS, headers=headers, json=_order_body(client_id, scheduled_date=yesterday))
    assert rejected.status_code == 422
    assert rejected.json()["code"] == "SCHEDULED_DATE_IN_PAST"
    accepted = client.post(ORDERS, headers=headers, json=_order_body(client_id))
    assert accepted.status_code == 201


def test_unknown_and_inactive_clients_are_rejected(client, dispatcher, headers_for) -> None:
    headers = headers_for(dispatcher)
    unknown = client.post(ORDERS, headers=headers, json=_order_body("00000000-0000-4000-8000-000000000001"))
    assert unknown.status_code == 404 and unknown.json()["code"] == "CLIENT_NOT_FOUND"
    client_id = _make_client(client, headers)
    client.patch(f"{CLIENTS}/{client_id}", headers=headers, json={"is_active": False})
    inactive = client.post(ORDERS, headers=headers, json=_order_body(client_id))
    assert inactive.status_code == 409 and inactive.json()["code"] == "CLIENT_INACTIVE"


def test_mass_assignment_of_status_is_rejected(client, dispatcher, headers_for) -> None:
    headers = headers_for(dispatcher)
    client_id = _make_client(client, headers)
    response = client.post(ORDERS, headers=headers, json=_order_body(client_id, status="COMPLETED"))
    assert response.status_code == 422


def test_only_dispatcher_writes_while_owner_and_accounting_read(client, employees, headers_for) -> None:
    dispatcher = employees.create((RoleCode.DISPATCHER,))
    client_id = _make_client(client, headers_for(dispatcher))
    order = client.post(ORDERS, headers=headers_for(dispatcher), json=_order_body(client_id)).json()
    for role in (RoleCode.OWNER, RoleCode.ACCOUNTING):
        person = employees.create((role,))
        assert client.get(ORDERS, headers=headers_for(person)).status_code == 200
        assert client.get(f"{ORDERS}/{order['order_id']}", headers=headers_for(person)).status_code == 200
        create = client.post(ORDERS, headers=headers_for(person), json=_order_body(client_id))
        assert create.status_code == 403
        cancel = client.post(
            f"{ORDERS}/{order['order_id']}/cancel", headers=headers_for(person), json={"reason": "nope"}
        )
        assert cancel.status_code == 403
    for role in (RoleCode.DRIVER, RoleCode.HELPER, RoleCode.FLEET_MANAGER, RoleCode.HR_PAYROLL):
        person = employees.create((role,))
        assert client.get(ORDERS, headers=headers_for(person)).status_code == 403


def test_pending_orders_can_be_edited_then_cancelled_but_not_after(client, dispatcher, headers_for) -> None:
    headers = headers_for(dispatcher)
    client_id = _make_client(client, headers)
    order_id = client.post(ORDERS, headers=headers, json=_order_body(client_id)).json()["order_id"]
    edited = client.patch(
        f"{ORDERS}/{order_id}", headers=headers, json={"total_weight_tons": 60, "notes": "Rush"}
    )
    assert edited.status_code == 200 and edited.json()["total_weight_tons"] == 60
    assert client.patch(f"{ORDERS}/{order_id}", headers=headers, json={}).status_code == 422
    assert (
        client.patch(f"{ORDERS}/{order_id}", headers=headers, json={"total_weight_tons": None}).status_code
        == 422
    )
    cancelled = client.post(
        f"{ORDERS}/{order_id}/cancel", headers=headers, json={"reason": "Client withdrew"}
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "CANCELLED"
    assert cancelled.json()["cancellation_reason"] == "Client withdrew"
    again = client.post(f"{ORDERS}/{order_id}/cancel", headers=headers, json={"reason": "Twice"})
    assert again.status_code == 409 and again.json()["code"] == "ORDER_NOT_CANCELLABLE"
    late_edit = client.patch(f"{ORDERS}/{order_id}", headers=headers, json={"notes": "Too late"})
    assert late_edit.status_code == 409 and late_edit.json()["code"] == "ORDER_NOT_EDITABLE"


def test_list_filters_and_page_cap(client, dispatcher, headers_for) -> None:
    headers = headers_for(dispatcher)
    first = _make_client(client, headers, "Alpha Steel")
    second = _make_client(client, headers, "Beta Steel")
    tomorrow = (manila_today() + timedelta(days=1)).isoformat()
    client.post(ORDERS, headers=headers, json=_order_body(first))
    keep = client.post(ORDERS, headers=headers, json=_order_body(second, scheduled_date=tomorrow)).json()
    cancelled = client.post(ORDERS, headers=headers, json=_order_body(first)).json()
    client.post(f"{ORDERS}/{cancelled['order_id']}/cancel", headers=headers, json={"reason": "Dup entry"})
    by_client = client.get(ORDERS, headers=headers, params={"client_id": second}).json()["items"]
    assert [row["order_id"] for row in by_client] == [keep["order_id"]]
    pending = client.get(ORDERS, headers=headers, params={"status": "PENDING"}).json()["items"]
    assert len(pending) == 2
    dated = client.get(ORDERS, headers=headers, params={"date_from": tomorrow}).json()["items"]
    assert [row["order_id"] for row in dated] == [keep["order_id"]]
    assert client.get(ORDERS, headers=headers, params={"limit": 101}).status_code == 422
    assert client.get(ORDERS, headers=headers, params={"status": "BOGUS"}).status_code == 422


def test_order_changes_are_audited_without_personal_data(client, employees, dispatcher, headers_for) -> None:
    headers = headers_for(dispatcher)
    client_id = _make_client(client, headers)
    order_id = client.post(ORDERS, headers=headers, json=_order_body(client_id)).json()["order_id"]
    client.patch(f"{ORDERS}/{order_id}", headers=headers, json={"notes": "Call before arrival"})
    owner = employees.create((RoleCode.OWNER,))
    audit = client.get("/api/v1/audit-logs", headers=headers_for(owner)).json()["items"]
    actions = {row["action"] for row in audit}
    assert {"client.created", "delivery_order.created", "delivery_order.updated"} <= actions
    updated = next(row for row in audit if row["action"] == "delivery_order.updated")
    assert updated["details"] == {"fields": ["notes"]}
    assert updated["actor_employee_id"] == str(dispatcher.employee_id)


def test_client_names_are_unique_ignoring_case_and_updates_are_partial(
    client, dispatcher, headers_for
) -> None:
    headers = headers_for(dispatcher)
    client_id = _make_client(client, headers, "Unique Steel")
    duplicate = client.post(CLIENTS, headers=headers, json={"name": "UNIQUE STEEL"})
    assert duplicate.status_code == 409 and duplicate.json()["code"] == "CLIENT_NAME_EXISTS"
    renamed = client.patch(f"{CLIENTS}/{client_id}", headers=headers, json={"contact_person": "Ana Reyes"})
    assert renamed.status_code == 200
    assert renamed.json()["name"] == "Unique Steel" and renamed.json()["contact_person"] == "Ana Reyes"
    assert client.patch(f"{CLIENTS}/{client_id}", headers=headers, json={"name": None}).status_code == 422
    same_name = client.patch(f"{CLIENTS}/{client_id}", headers=headers, json={"name": "Unique Steel"})
    assert same_name.status_code == 200


def test_clients_cannot_be_written_by_view_only_roles(client, employees, headers_for) -> None:
    dispatcher = employees.create((RoleCode.DISPATCHER,))
    client_id = _make_client(client, headers_for(dispatcher))
    owner = employees.create((RoleCode.OWNER,))
    assert client.get(f"{CLIENTS}/{client_id}", headers=headers_for(owner)).status_code == 200
    assert client.post(CLIENTS, headers=headers_for(owner), json={"name": "Nope"}).status_code == 403
    patch = client.patch(f"{CLIENTS}/{client_id}", headers=headers_for(owner), json={"is_active": False})
    assert patch.status_code == 403
