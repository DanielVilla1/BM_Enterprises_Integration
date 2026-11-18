# ===== AI GENERATED: test_permission_matrix =====
# Purpose: Generate permission tests from the stored matrix (spec 3.4 / 13.2)
# Inputs: role_permissions table + the live FastAPI route table
# Returns: pass/fail per route x role cell
# Flow:
# 1. Fail if any route lacks a capability (deny by default)
# 2. Call every capability route as every role, compare with the table
# 3. Unauthenticated calls to non-public routes must return 401

import uuid
from collections.abc import Iterator

from fastapi.routing import APIRoute
from sqlalchemy import select

from backend.main import app
from backend.src.Entity.access import AccessLevel, RoleCode
from backend.src.providers import get_principal
from backend.src.Repository.orm_models import RolePermissionRow

PUBLIC_ROUTES = {("GET", "/api/v1/health"), ("POST", "/api/v1/webhooks/clerk")}
AUTHENTICATED_ONLY_ROUTES = {("GET", "/api/v1/me")}
BODY_METHODS = {"POST", "PUT", "PATCH"}


def _dependency_calls(dependant) -> Iterator[object]:
    for sub_dependant in dependant.dependencies:
        yield sub_dependant.call
        yield from _dependency_calls(sub_dependant)


def _all_routes() -> list[tuple[str, str, APIRoute]]:
    return [
        (method, route.path, route)
        for route in app.routes
        if isinstance(route, APIRoute)
        for method in sorted(route.methods - {"HEAD", "OPTIONS"})
    ]


def _capability_rule(route: APIRoute):
    for call in _dependency_calls(route.dependant):
        capability = getattr(call, "capability", None)
        if capability is not None:
            return (
                capability,
                getattr(call, "minimum_level", None),
                getattr(call, "only_levels", None),
            )
    return None


def _concrete_path(path: str) -> str:
    segments = [str(uuid.uuid4()) if part.startswith("{") else part for part in path.split("/")]
    return "/".join(segments)


def test_every_route_declares_a_capability_or_is_explicitly_allowlisted() -> None:
    undeclared = []
    for method, path, route in _all_routes():
        if (method, path) in PUBLIC_ROUTES:
            continue
        if _capability_rule(route) is not None:
            continue
        uses_authentication = any(
            getattr(call, "requires_authentication", False) for call in _dependency_calls(route.dependant)
        )
        if (method, path) in AUTHENTICATED_ONLY_ROUTES and uses_authentication:
            continue
        undeclared.append(f"{method} {path}")
    assert not undeclared, f"routes without a permission entry: {undeclared}"


def test_every_referenced_capability_exists_in_the_stored_matrix(session_factory) -> None:
    with session_factory() as session:
        stored = set(session.scalars(select(RolePermissionRow.capability)).all())
    referenced = {rule[0] for _, _, route in _all_routes() if (rule := _capability_rule(route))}
    assert referenced <= stored, f"capabilities missing from role_permissions: {referenced - stored}"


def test_every_role_gets_exactly_what_the_matrix_grants(client, session_factory, employees) -> None:
    with session_factory() as session:
        grants = {
            (row.capability, row.role_code): AccessLevel(row.access_level)
            for row in session.scalars(select(RolePermissionRow)).all()
        }
    people = {role: employees.create((role,)) for role in RoleCode}
    from backend.tests.conftest import auth_headers

    failures = []
    for method, path, route in _all_routes():
        rule = _capability_rule(route)
        if rule is None:
            continue
        capability, minimum, only_levels = rule
        for role, person in people.items():
            level = grants.get((capability, role.value))
            allowed = (
                level is not None
                and (minimum is None or level.rank >= minimum.rank)
                and (only_levels is None or level in only_levels)
            )
            response = client.request(
                method,
                _concrete_path(path),
                headers=auth_headers(person),
                json={} if method in BODY_METHODS else None,
            )
            if allowed and response.status_code in (401, 403):
                failures.append(f"{role} should reach {method} {path}, got {response.status_code}")
            if not allowed and not (
                response.status_code == 403 and response.json()["code"] == "PERMISSION_DENIED"
            ):
                failures.append(f"{role} must be denied {method} {path}, got {response.status_code}")
    assert not failures, "\n".join(failures)


def test_unauthenticated_calls_to_protected_routes_return_401_problem_json(client) -> None:
    failures = []
    for method, path, _route in _all_routes():
        if (method, path) in PUBLIC_ROUTES:
            continue
        response = client.request(method, _concrete_path(path), json={} if method in BODY_METHODS else None)
        content_type = response.headers.get("content-type", "")
        if response.status_code != 401 or "application/problem+json" not in content_type:
            failures.append(f"{method} {path} -> {response.status_code} {content_type}")
    assert not failures, "\n".join(failures)


def test_get_principal_is_the_marked_authentication_dependency() -> None:
    assert getattr(get_principal, "requires_authentication", False) is True
