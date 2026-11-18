# ===== AI GENERATED: test_authentication =====
# Purpose: Interface tests for Clerk token verification (AUTH-01, IT-01, API2)
# Inputs: minted fake tokens
# Returns: pass/fail
# Flow:
# 1. Valid token maps to an active employee
# 2. Expired, wrong issuer, wrong azp, wrong key, wrong alg are rejected
# 3. Unknown / inactive employees get no access

import time

import jwt

from backend.main import app
from backend.src.Contract.i_token_verifier import ProviderUnavailableError
from backend.src.Entity.access import RoleCode
from backend.src.providers import get_token_verifier
from backend.tests.conftest import OTHER_KEY, SIGNING_KEY, TEST_ISSUER, TEST_PARTY, mint_token


def _bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_valid_token_returns_the_matching_active_employee(client, employees, headers_for) -> None:
    driver = employees.create((RoleCode.DRIVER,), name="Driver One")
    response = client.get("/api/v1/me", headers=headers_for(driver))
    assert response.status_code == 200
    body = response.json()
    assert body["employee_id"] == str(driver.employee_id)
    assert body["role_codes"] == ["DRIVER"]
    assert body["capabilities"]["trip.progress"] == "OWN"
    assert "payroll.view_others" not in body["capabilities"]


def test_missing_token_is_401_problem_json(client) -> None:
    response = client.get("/api/v1/me")
    assert response.status_code == 401
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "AUTH_MISSING_TOKEN"
    assert response.headers["www-authenticate"] == "Bearer"


def test_expired_token_is_rejected(client, employees) -> None:
    person = employees.create((RoleCode.DRIVER,))
    token = mint_token(person.clerk_user_id, lifetime_seconds=-120)
    assert client.get("/api/v1/me", headers=_bearer(token)).status_code == 401


def test_wrong_issuer_is_rejected(client, employees) -> None:
    person = employees.create((RoleCode.DRIVER,))
    token = mint_token(person.clerk_user_id, issuer="https://evil.example")
    assert client.get("/api/v1/me", headers=_bearer(token)).status_code == 401


def test_wrong_authorized_party_is_rejected(client, employees) -> None:
    person = employees.create((RoleCode.DRIVER,))
    token = mint_token(person.clerk_user_id, authorized_party="https://evil.example")
    assert client.get("/api/v1/me", headers=_bearer(token)).status_code == 401


def test_token_signed_with_another_key_is_rejected(client, employees) -> None:
    person = employees.create((RoleCode.DRIVER,))
    token = mint_token(person.clerk_user_id, key=OTHER_KEY)
    assert client.get("/api/v1/me", headers=_bearer(token)).status_code == 401


def test_symmetric_algorithm_confusion_is_rejected(client, employees) -> None:
    person = employees.create((RoleCode.DRIVER,))
    now = int(time.time())
    claims = {"sub": person.clerk_user_id, "iss": TEST_ISSUER, "azp": TEST_PARTY, "iat": now, "exp": now + 60}
    forged = jwt.encode(claims, "shared-secret-0123456789-0123456789", algorithm="HS256")
    assert client.get("/api/v1/me", headers=_bearer(forged)).status_code == 401


def test_unsigned_none_algorithm_token_is_rejected(client, employees) -> None:
    person = employees.create((RoleCode.DRIVER,))
    now = int(time.time())
    claims = {"sub": person.clerk_user_id, "iss": TEST_ISSUER, "azp": TEST_PARTY, "iat": now, "exp": now + 60}
    unsigned = jwt.encode(claims, key="", algorithm="none")
    assert client.get("/api/v1/me", headers=_bearer(unsigned)).status_code == 401


def test_token_without_expiry_is_rejected(client, employees) -> None:
    person = employees.create((RoleCode.DRIVER,))
    claims = {"sub": person.clerk_user_id, "iss": TEST_ISSUER, "azp": TEST_PARTY, "iat": int(time.time())}
    token = jwt.encode(claims, SIGNING_KEY, algorithm="RS256")
    assert client.get("/api/v1/me", headers=_bearer(token)).status_code == 401


def test_unknown_clerk_user_has_no_access(client) -> None:
    response = client.get("/api/v1/me", headers=_bearer(mint_token("user_not_in_database")))
    assert response.status_code == 403
    assert response.json()["code"] == "AUTH_NO_ACTIVE_EMPLOYEE"


def test_inactive_employee_has_no_access(client, employees, headers_for) -> None:
    person = employees.create((RoleCode.DRIVER,), active=False)
    response = client.get("/api/v1/me", headers=headers_for(person))
    assert response.status_code == 403
    assert response.json()["code"] == "AUTH_NO_ACTIVE_EMPLOYEE"


def test_identity_provider_outage_without_cached_keys_is_503(client, employees, headers_for) -> None:
    person = employees.create((RoleCode.DRIVER,))

    class UnavailableVerifier:
        def verify(self, raw_token: str):
            raise ProviderUnavailableError("down")

    app.dependency_overrides[get_token_verifier] = lambda: UnavailableVerifier()
    response = client.get("/api/v1/me", headers=headers_for(person))
    assert response.status_code == 503
    assert response.json()["code"] == "AUTH_PROVIDER_UNAVAILABLE"
