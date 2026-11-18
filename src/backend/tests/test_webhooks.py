# ===== AI GENERATED: test_webhooks =====
# Purpose: Clerk webhook signature and idempotency tests (spec 12 / 13.2)
# Inputs: signed and tampered fake webhook deliveries
# Returns: pass/fail
# Flow:
# 1. Bad signature -> 400, no effect
# 2. Good delivery replayed twice -> exactly one effect
# 3. Unverified email is never linked; user.deleted deactivates

import json
import time

from backend.src.Entity.access import RoleCode
from backend.src.Repository.audit_repository import AuditRepository
from backend.src.Repository.employee_repository import EmployeeRepository
from backend.tests.conftest import sign_webhook

URL = "/api/v1/webhooks/clerk"


def _user_event(event_type: str, clerk_id: str, email: str, verified: bool = True) -> bytes:
    payload = {
        "type": event_type,
        "data": {
            "id": clerk_id,
            "primary_email_address_id": "idn_primary",
            "email_addresses": [
                {
                    "id": "idn_primary",
                    "email_address": email,
                    "verification": {"status": "verified" if verified else "unverified"},
                }
            ],
        },
    }
    return json.dumps(payload).encode()


def _actions(session_factory, name: str) -> int:
    with session_factory() as session:
        return len([row for row in AuditRepository(session).list_page(100, 0) if row.action == name])


def test_bad_signature_is_rejected_with_400_and_no_effect(client, employees, session_factory) -> None:
    target = employees.create((RoleCode.DRIVER,), linked=False, email="link.me@bm-test.example")
    body = _user_event("user.created", "user_attacker1", "link.me@bm-test.example")
    headers = sign_webhook(body, "msg_bad")
    headers["svix-signature"] = "v1,AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    response = client.post(URL, content=body, headers=headers)
    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/problem+json")
    with session_factory() as session:
        stored = EmployeeRepository(session).get_by_id(target.employee_id)
    assert stored is not None and stored.clerk_user_id is None


def test_missing_signature_headers_are_rejected(client) -> None:
    response = client.post(URL, content=b"{}", headers={"content-type": "application/json"})
    assert response.status_code == 400


def test_tampered_body_is_rejected(client, employees) -> None:
    employees.create((RoleCode.DRIVER,), linked=False, email="tamper@bm-test.example")
    original = _user_event("user.created", "user_tamper1", "tamper@bm-test.example")
    headers = sign_webhook(original, "msg_tamper")
    tampered = _user_event("user.created", "user_tamper2", "tamper@bm-test.example")
    assert client.post(URL, content=tampered, headers=headers).status_code == 400


def test_stale_timestamp_is_rejected(client) -> None:
    body = _user_event("user.created", "user_old1", "old@bm-test.example")
    headers = sign_webhook(body, "msg_old", timestamp=int(time.time()) - 3600)
    assert client.post(URL, content=body, headers=headers).status_code == 400


def test_good_delivery_links_by_verified_email_exactly_once(client, employees, session_factory) -> None:
    target = employees.create((RoleCode.DRIVER,), linked=False, email="Driver.One@bm-test.example")
    body = _user_event("user.created", "user_driverone", "driver.one@bm-test.example")
    headers = sign_webhook(body, "msg_good")
    first = client.post(URL, content=body, headers=headers)
    second = client.post(URL, content=body, headers=headers)
    assert first.json() == {"status": "processed"}
    assert second.json() == {"status": "duplicate"}
    with session_factory() as session:
        stored = EmployeeRepository(session).get_by_id(target.employee_id)
    assert stored is not None and stored.clerk_user_id == "user_driverone"
    assert _actions(session_factory, "employee.identity_linked") == 1


def test_unverified_email_is_never_linked(client, employees, session_factory) -> None:
    target = employees.create((RoleCode.DRIVER,), linked=False, email="unverified@bm-test.example")
    body = _user_event("user.created", "user_unverified", "unverified@bm-test.example", verified=False)
    response = client.post(URL, content=body, headers=sign_webhook(body, "msg_unverified"))
    assert response.json() == {"status": "ignored"}
    with session_factory() as session:
        stored = EmployeeRepository(session).get_by_id(target.employee_id)
    assert stored is not None and stored.clerk_user_id is None


def test_existing_link_is_not_overwritten(client, employees, session_factory) -> None:
    target = employees.create((RoleCode.DRIVER,), email="linked@bm-test.example")
    body = _user_event("user.updated", "user_someoneelse", "linked@bm-test.example")
    response = client.post(URL, content=body, headers=sign_webhook(body, "msg_conflict"))
    assert response.json() == {"status": "ignored"}
    with session_factory() as session:
        stored = EmployeeRepository(session).get_by_id(target.employee_id)
    assert stored is not None and stored.clerk_user_id == target.clerk_user_id
    assert _actions(session_factory, "webhook.clerk.link_conflict") == 1


def test_user_deleted_deactivates_the_linked_employee(client, employees, session_factory) -> None:
    target = employees.create((RoleCode.DRIVER,))
    body = json.dumps({"type": "user.deleted", "data": {"id": target.clerk_user_id}}).encode()
    response = client.post(URL, content=body, headers=sign_webhook(body, "msg_deleted"))
    assert response.json() == {"status": "processed"}
    with session_factory() as session:
        stored = EmployeeRepository(session).get_by_id(target.employee_id)
    assert stored is not None and stored.is_active is False


def test_oversized_body_is_rejected(client) -> None:
    response = client.post(URL, content=b"x" * 300000, headers={"content-type": "application/json"})
    assert response.status_code == 413
