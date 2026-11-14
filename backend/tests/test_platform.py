# ===== AI GENERATED: test_platform =====
# Purpose: Migrations, matrix seed, audit immutability, OpenAPI, CORS, role rules
# Inputs: migrated SQLite database
# Returns: pass/fail
# Flow:
# 1. Migration output equals the ORM models and the seed JSON
# 2. audit_log rejects UPDATE and DELETE
# 3. OpenAPI 3.1 is served; CORS is not wildcard; pair rules hold

import json
from pathlib import Path

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from backend.src.database import Base
from backend.src.Entity.access import RoleCode
from backend.src.Entity.role_rules import find_forbidden_pairs, is_forbidden_pair
from backend.src.Repository import orm_models
from backend.src.Repository.audit_repository import AuditRepository

MATRIX_PATH = Path(__file__).resolve().parents[1] / "src" / "Data" / "permission_matrix.json"


def test_migrations_match_the_orm_models(session_factory) -> None:
    with session_factory() as session:
        context = MigrationContext.configure(session.connection())
        assert compare_metadata(context, Base.metadata) == []


def test_seeded_matrix_equals_the_source_json(session_factory) -> None:
    matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    expected = {
        (entry["capability"], role, level, entry.get("conditional", {}).get(role))
        for entry in matrix["capabilities"]
        for role, level in entry["grants"].items()
    }
    with session_factory() as session:
        stored = {
            (row.capability, row.role_code, row.access_level, row.conditional_setting)
            for row in session.scalars(select(orm_models.RolePermissionRow)).all()
        }
        role_codes = {row.code for row in session.scalars(select(orm_models.RoleRow)).all()}
    assert stored == expected
    assert role_codes == {role.value for role in RoleCode}


def test_matrix_matches_the_specification_spot_checks(session_factory) -> None:
    with session_factory() as session:
        grants = {
            (row.capability, row.role_code): row.access_level
            for row in session.scalars(select(orm_models.RolePermissionRow)).all()
        }
    assert grants[("or.confirm_receipt", "DRIVER")] == "OWN"
    assert ("or.confirm_receipt", "HELPER") not in grants
    assert ("payroll.view_others", "DRIVER") not in grants
    assert ("client_rate.view", "DISPATCHER") not in grants
    assert grants[("cash_advance.approve", "OWNER")] == "FULL"
    assert ("cash_advance.approve", "HR_PAYROLL") not in grants
    assert grants[("audit_user.manage", "OWNER")] == "FULL"
    assert [key for key in grants if key[0] == "audit_user.manage"] == [("audit_user.manage", "OWNER")]


def test_audit_log_rejects_update_and_delete(session_factory) -> None:
    with session_factory() as session:
        AuditRepository(session).append(None, "test.event", "thing", None, {}, None)
        session.commit()
    for statement in ("UPDATE audit_log SET action = 'tampered'", "DELETE FROM audit_log"):
        with session_factory() as session, pytest.raises(SQLAlchemyError):
            session.execute(text(statement))
            session.commit()


def test_openapi_31_document_is_served_at_the_versioned_path(client) -> None:
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    assert response.json()["openapi"].startswith("3.1")
    assert all(path.startswith("/api/v1/") for path in response.json()["paths"])


def test_cors_allows_only_configured_origins(client) -> None:
    allowed = client.options(
        "/api/v1/me",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
    )
    denied = client.options(
        "/api/v1/me",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET"},
    )
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert "access-control-allow-origin" not in denied.headers


def test_forbidden_pair_rules_follow_the_specification() -> None:
    assert is_forbidden_pair(RoleCode.HR_PAYROLL, RoleCode.ACCOUNTING)
    assert is_forbidden_pair(RoleCode.DISPATCHER, RoleCode.HR_PAYROLL)
    assert is_forbidden_pair(RoleCode.DISPATCHER, RoleCode.ACCOUNTING)
    assert is_forbidden_pair(RoleCode.DRIVER, RoleCode.FLEET_MANAGER)
    assert is_forbidden_pair(RoleCode.HELPER, RoleCode.OWNER)
    assert not is_forbidden_pair(RoleCode.OWNER, RoleCode.DISPATCHER)
    assert not is_forbidden_pair(RoleCode.DRIVER, RoleCode.HELPER)
    assert find_forbidden_pairs({RoleCode.OWNER, RoleCode.DISPATCHER}) == []
