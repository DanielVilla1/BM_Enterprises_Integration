# ===== AI GENERATED: presentation_and_finance_regressions =====
# Purpose: Prove the Owner regression fix, safe demo seed and financial race controls.
# Inputs: Isolated migrated databases and fictional records only.
# Returns: API, schema, concurrency and demonstration-data acceptance checks.
# Flow: Test the existing-0005 upgrade path as well as clean installations.

from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from pathlib import Path

from alembic import command as alembic_command
from alembic.config import Config
from sqlalchemy import create_engine, func, select, text

from backend.src.Entity.clock import manila_today
from backend.src.Entity.finance import money, payroll_period
from backend.src.Repository.orm_models import EmployeeRow
from backend.src.Repository.presentation_seed_repository import PresentationSeedRepository, demo_id
from backend.tests.test_finance_workflows import (
    command,
    completed,
    finalize_sources,
    invoice,
    workspace,
)
from backend.tests.test_finance_workflows import finance_world as finance_world


def test_revision_0006_repairs_missing_owner_read_grants(tmp_path: Path):
    configuration = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    address = f"sqlite:///{(tmp_path / 'upgrade-existing.db').as_posix()}"
    configuration.set_main_option("sqlalchemy.url", address)
    engine = create_engine(address)
    try:
        alembic_command.upgrade(configuration, "0005")
        with engine.begin() as connection:
            connection.execute(text("DELETE FROM role_permissions WHERE capability = 'expense.view'"))
        alembic_command.upgrade(configuration, "head")
        with engine.connect() as connection:
            assert (
                connection.execute(
                    text(
                        "SELECT access_level FROM role_permissions "
                        "WHERE capability = 'expense.view' AND role_code = 'OWNER'"
                    )
                ).scalar()
                == "FULL"
            )
            assert "contributors" in [
                row[1] for row in connection.execute(text("PRAGMA table_info(expense_sheets)"))
            ]
    finally:
        engine.dispose()


def test_presentation_seed_is_repeatable_and_preserves_existing_identity(finance_world):
    world = finance_world
    with world.session_factory() as session:
        existing = session.get(EmployeeRow, world.owner.employee_id)
        original_link = existing.clerk_user_id
        counts = PresentationSeedRepository(session).seed()
        first_count = session.scalar(select(func.count()).select_from(EmployeeRow))
        assert counts["trips"] == 8 and counts["invoices"] == 3
        assert PresentationSeedRepository(session).seed()["already_loaded"] == 1
        assert session.scalar(select(func.count()).select_from(EmployeeRow)) == first_count
        assert session.get(EmployeeRow, world.owner.employee_id).clerk_user_id == original_link
    expenses = workspace(world, "expenses", world.owner)
    assert expenses["presentation_data"] and len(expenses["trips"]) == 8
    assert len(expenses["expenses"]) == 7
    payroll = workspace(world, "payroll", world.owner)
    assert len(payroll["payrolls"]) == 2 and len(payroll["statements"]) >= 5
    assert workspace(world, "billing", world.owner)["invoices"]
    assert len(workspace(world, "advances", world.owner)["advances"]) == 4


def test_presentation_documents_remain_authorized_and_are_conspicuously_fake(finance_world):
    world = finance_world
    with world.session_factory() as session:
        PresentationSeedRepository(session).seed()
    identifier = demo_id("document-0-SIGNED_OR")
    response = world.get(f"/api/v1/finance/presentation-documents/{identifier}", world.owner)
    assert response.status_code == 200 and response.content.startswith(b"\x89PNG\r\n\x1a\n")
    outsider = world.make_driver()
    assert world.get(f"/api/v1/finance/presentation-documents/{identifier}", outsider).status_code == 404
    assert response.headers["cache-control"] == "no-store"


def test_prior_contributor_cannot_approve_after_a_different_editor(finance_world):
    world = finance_world
    delivered = completed(world)
    payload = {"declared_zero": True, "reason": "Confirmed no purchases"}
    assert command(world, f"/expenses/{delivered.trip_id}", world.owner, payload).status_code == 200
    assert command(world, f"/expenses/{delivered.trip_id}", world.dispatcher, payload).status_code == 200
    assert command(world, f"/expenses/{delivered.trip_id}/submit", world.dispatcher).status_code == 200
    response = command(
        world,
        f"/expenses/{delivered.trip_id}/review",
        world.owner,
        {"approved": True, "reason": "Cannot approve own contribution"},
    )
    assert response.status_code == 409 and response.json()["code"] == "SELF_APPROVAL_FORBIDDEN"


def test_zero_expenses_and_rounding_variance_are_explicit(finance_world):
    world = finance_world
    delivered = completed(world)
    finalize_sources(world, delivered, expense="0.00", charge="0.05")
    assert workspace(world, "expenses", world.accounting)["expenses"][0]["state"] == "CONFIRMED_ZERO"
    assert command(world, f"/earnings/{delivered.trip_id}/calculate", world.owner).status_code == 200
    earnings = workspace(world, "payroll", world.hr)["earnings"]
    assert sum((Decimal(entry["amount"]) for entry in earnings), Decimal(0)) == 0
    assert sum((Decimal(entry["rounding_variance"]) for entry in earnings), Decimal(0)) == Decimal("-0.01")
    assert money(Decimal("1.005")) == Decimal("1.01")


def test_operating_shortage_does_not_create_personal_debt(finance_world):
    world = finance_world
    delivered = completed(world)
    finalize_sources(world, delivered)
    response = command(
        world,
        "/advances",
        world.hr,
        {
            "employee_id": str(delivered.driver.employee_id),
            "amount": "5000.00",
            "kind": "OPERATING",
            "trip_id": delivered.trip_id,
            "reason": "Trip fuel float",
        },
    )
    identifier = response.json()["record_id"]
    approval = {
        "amount": "5000.00",
        "installment": "1.00",
        "start_on": payroll_period(manila_today())[0].isoformat(),
        "acknowledgment": "DEMO custodian acknowledgment",
        "reason": "Operating float approved",
    }
    assert command(world, f"/advances/{identifier}/approve", world.owner, approval).status_code == 200
    assert (
        command(
            world,
            f"/advances/{identifier}/release",
            world.hr,
            {
                "amount": "5000.00",
                "occurred_on": manila_today().isoformat(),
                "reference": "Actual float release",
            },
        ).status_code
        == 200
    )
    response = command(world, f"/advances/{identifier}/reconcile", world.owner, {"reason": "Review variance"})
    assert response.status_code == 200 and response.json()["state"] == "REVIEW_REQUIRED"
    assert (
        Decimal(
            world.get("/api/v1/finance/reports", world.owner).json()["financial_totals"][
                "personal_advance_balance"
            ]
        )
        == 0
    )


def test_concurrent_bill_creation_allocates_once(finance_world):
    world = finance_world
    delivered = completed(world)
    finalize_sources(world, delivered)
    payload = {
        "client_id": str(world.client_id),
        "cutoff": manila_today().isoformat(),
        "trip_ids": [delivered.trip_id],
    }
    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(
            executor.map(lambda _attempt: command(world, "/invoices", world.accounting, payload), range(2))
        )
    assert sorted(response.status_code for response in responses) == [200, 409]
    assert len(workspace(world, "billing", world.accounting)["invoices"]) == 1


def test_concurrent_collection_retries_post_once(finance_world):
    world = finance_world
    delivered = completed(world)
    finalize_sources(world, delivered)
    identifier = invoice(world, delivered)
    assert command(world, f"/invoices/{identifier}/issue", world.accounting).status_code == 200
    payload = {
        "amount": "5.00",
        "paid_on": manila_today().isoformat(),
        "method": "Cash",
        "reference": "Actual receipt TEST-2",
    }
    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(
            executor.map(
                lambda _attempt: command(
                    world,
                    f"/invoices/{identifier}/payments",
                    world.accounting,
                    payload,
                    key="concurrent-payment",
                ),
                range(2),
            )
        )
    assert all(response.status_code == 200 for response in responses)
    assert responses[0].json()["record_id"] == responses[1].json()["record_id"]
    assert len(workspace(world, "billing", world.accounting)["payments"]) == 1
