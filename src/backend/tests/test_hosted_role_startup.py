"""Exercise real authenticated account loading for every stored business role."""

import json
from pathlib import Path

import pytest

from backend.src.config import get_settings
from backend.src.Entity.access import RoleCode
from backend.tests.conftest import mint_token

MATRIX = json.loads(
    (Path(__file__).resolve().parents[1] / "src" / "Data" / "permission_matrix.json").read_text(
        encoding="utf-8"
    )
)


@pytest.mark.parametrize("role", list(RoleCode), ids=lambda role: role.value)
@pytest.mark.parametrize("helper_uploads", [False, True], ids=["helper-upload-off", "helper-upload-on"])
def test_every_role_loads_its_own_account_and_exact_seed_grants(
    client, employees, headers_for, monkeypatch, role, helper_uploads
) -> None:
    monkeypatch.setattr(get_settings(), "helper_or_upload_enabled", helper_uploads)
    person = employees.create((role,))
    expected = {
        entry["capability"]: entry["grants"][role.value]
        for entry in MATRIX["capabilities"]
        if role.value in entry["grants"]
        and (role.value not in entry.get("conditional", {}) or helper_uploads)
    }

    health = client.get("/api/v1/health")
    assert health.status_code == 200 and health.json() == {"status": "ok"}
    response = client.get("/api/v1/me", headers=headers_for(person))
    assert response.status_code == 200, response.text
    account = response.json()
    assert account["employee_id"] == str(person.employee_id)
    assert account["role_codes"] == [role.value]
    assert account["capabilities"] == expected


@pytest.mark.parametrize("role", list(RoleCode), ids=lambda role: role.value)
def test_inactive_employees_cannot_enter_for_any_role(client, employees, headers_for, role) -> None:
    person = employees.create((role,), active=False)
    response = client.get("/api/v1/me", headers=headers_for(person))
    assert response.status_code == 403
    assert response.json()["code"] == "AUTH_NO_ACTIVE_EMPLOYEE"
    assert response.json()["account_setup"] == {
        "reason": "employee_inactive",
        "clerk_user_id": person.clerk_user_id,
    }


@pytest.mark.parametrize("role", list(RoleCode), ids=lambda role: role.value)
def test_expired_tokens_are_rejected_for_every_role(client, employees, role) -> None:
    person = employees.create((role,))
    token = mint_token(person.clerk_user_id, lifetime_seconds=-120)
    response = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["code"] == "AUTH_INVALID_TOKEN"
    assert "account_setup" not in response.json()


def test_unlinked_identity_gets_only_its_own_setup_information(client, employees) -> None:
    owner = employees.create((RoleCode.OWNER,))
    token = mint_token("user_not_linked")
    response = client.get("/api/v1/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    body = response.json()
    assert body["code"] == "AUTH_NO_ACTIVE_EMPLOYEE"
    assert body["account_setup"] == {"reason": "identity_not_linked", "clerk_user_id": "user_not_linked"}
    assert str(owner.employee_id) not in response.text
    assert owner.clerk_user_id not in response.text
    assert "capabilities" not in body
