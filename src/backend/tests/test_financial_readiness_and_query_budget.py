# ===== AI GENERATED: financial_readiness_regressions =====
# Purpose: Verify automatic earnings and bounded report queries after the load-test finding.
# Inputs: Authenticated journeys on isolated databases.
# Returns: Behavioral and query-growth regression evidence.
# Flow: Finalize sources, confirm receipt, and compare report work at different trip counts.

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import event

from backend.tests.conftest import auth_headers
from backend.tests.image_support import make_jpeg
from backend.tests.test_finance_workflows import command, completed, finalize_sources, workspace
from backend.tests.test_finance_workflows import finance_world as finance_world


def test_report_queries_do_not_grow_per_trip(finance_world):
    world = finance_world
    completed(world)
    engine = world.session_factory.kw["bind"]

    def measure_report():
        statements = []

        def count_query(_connection, _cursor, statement, _parameters, _context, _many):
            statements.append(statement)

        event.listen(engine, "before_cursor_execute", count_query)
        try:
            response = world.get("/api/v1/finance/reports", world.owner)
            assert response.status_code == 200, response.text
            return len(statements)
        finally:
            event.remove(engine, "before_cursor_execute", count_query)

    one_trip_queries = measure_report()
    for _trip_index in range(4):
        completed(world)
    assert measure_report() <= one_trip_queries + 2


def test_financial_finalization_generates_without_manual_calculate(finance_world):
    world = finance_world
    delivered = completed(world)
    finalize_sources(world, delivered)
    assert len(workspace(world, "payroll", world.hr)["earnings"]) == 2


def test_receipt_generates_ready_finance_after_operational_commit(finance_world):
    world = finance_world
    delivered = world.delivered_trip()
    finalize_sources(world, delivered)
    assert workspace(world, "payroll", world.hr)["earnings"] == []
    response = world.client.post(
        f"/api/v1/trips/{delivered.trip_id}/or-documents",
        headers=auth_headers(delivered.driver),
        files={"file": ("signed.jpg", make_jpeg(), "image/jpeg")},
        data={"kind": "SIGNED_OR"},
    )
    assert response.status_code == 201
    response = world.client.post(
        f"/api/v1/trips/{delivered.trip_id}/confirm-receipt",
        headers={**auth_headers(delivered.driver), "Idempotency-Key": str(uuid4())},
        json={"received_at": datetime.now(UTC).isoformat()},
    )
    assert response.status_code == 200 and response.json()["status"] == "COMPLETED"
    assert len(workspace(world, "payroll", world.hr)["earnings"]) == 2


def test_combined_owner_driver_cannot_release_own_financial_hold(finance_world):
    from backend.src.Entity.access import RoleCode
    from backend.src.Repository.employee_repository import EmployeeRepository

    world = finance_world
    delivered = completed(world)
    finalize_sources(world, delivered)
    with world.session_factory() as session:
        EmployeeRepository(session).replace_roles(
            delivered.driver.employee_id,
            {RoleCode.DRIVER, RoleCode.OWNER},
            world.owner.employee_id,
            "Fictional combined-role regression",
        )
        session.commit()
    response = world.post(
        f"/api/v1/trips/{delivered.trip_id}/receipt-correction",
        world.owner,
        {"reason": "Company receipt needs correction"},
    )
    assert response.status_code == 200
    response = command(
        world,
        f"/holds/{delivered.trip_id}/release",
        delivered.driver,
        {"reason": "Beneficiary cannot authorize own pay"},
    )
    assert response.status_code == 409 and response.json()["code"] == "SELF_APPROVAL_FORBIDDEN"
