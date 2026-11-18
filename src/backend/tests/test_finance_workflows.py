# ===== AI GENERATED: financial_acceptance_tests =====
# Purpose: Exercise financial invariants through authenticated APIs and migrated SQL.
# Inputs: Fictional completed deliveries and independently authorized staff.
# Returns: Regression proof for money, ownership, retries, holds and transactions.
# Flow: Drive real workflows; inspect independent ledgers rather than implementation details.

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from backend.src.Entity.access import RoleCode
from backend.src.Entity.clock import manila_today
from backend.src.Entity.finance import AdvanceMovement, payroll_period
from backend.src.Repository.financial_repository import FinancialRepository
from backend.src.Repository.orm_models import TripRow
from backend.tests.conftest import auth_headers
from backend.tests.dispatch_support import World
from backend.tests.image_support import make_jpeg


@pytest.fixture
def finance_world(client, session_factory, employees):
    world = World(client, session_factory, employees)
    world.accounting = employees.create((RoleCode.ACCOUNTING,))
    world.hr = employees.create((RoleCode.HR_PAYROLL,))
    return world


def command(world, path, actor, payload=None, key=None):
    return world.client.post(
        f"/api/v1/finance{path}",
        headers={**auth_headers(actor), "Idempotency-Key": key or str(uuid4())},
        json=payload or {},
    )


def completed(world, two_helpers=False):
    delivered = world.delivered_trip()
    if two_helpers:
        # Retain the completed API journey while adding the second crew member for this financial fixture.
        from backend.src.Repository.orm_models import TripCrewRow

        helper = world.make_helper()
        with world.session_factory() as session:
            session.add(
                TripCrewRow(
                    trip_id=UUID(delivered.trip_id), employee_id=helper.employee_id, crew_role="HELPER"
                )
            )
            session.commit()
        delivered.helpers.append(helper)
    uploaded = world.client.post(
        f"/api/v1/trips/{delivered.trip_id}/or-documents",
        headers=auth_headers(delivered.driver),
        files={"file": ("signed.jpg", make_jpeg(), "image/jpeg")},
        data={"kind": "SIGNED_OR"},
    )
    assert uploaded.status_code == 201, uploaded.text
    confirmed = world.client.post(
        f"/api/v1/trips/{delivered.trip_id}/confirm-receipt",
        headers={**auth_headers(delivered.driver), "Idempotency-Key": str(uuid4())},
        json={"received_at": datetime.now(UTC).isoformat()},
    )
    assert confirmed.status_code == 200, confirmed.text
    return delivered


def finalize_sources(world, delivered, expense="5500.00", charge="20000.00"):
    trip_id = delivered.trip_id
    payload = {"lines": [], "declared_zero": expense == "0.00", "reason": "Actual trip expenses"}
    if expense != "0.00":
        payload["lines"] = [
            {
                "category": "FUEL",
                "amount": expense,
                "description": "Diesel at station",
                "incurred_on": manila_today().isoformat(),
                "evidence": "Receipt TEST-123",
            }
        ]
    response = command(world, f"/expenses/{trip_id}", delivered.driver, payload)
    assert response.status_code == 200, response.text
    assert command(world, f"/expenses/{trip_id}/submit", delivered.driver).status_code == 200
    assert (
        command(
            world,
            f"/expenses/{trip_id}/review",
            world.accounting,
            {"approved": True, "reason": "Verified source receipt"},
        ).status_code
        == 200
    )
    response = command(
        world,
        f"/charges/{trip_id}",
        world.accounting,
        {
            "amount": charge,
            "agreed_amount": charge,
            "reference": "Agreement TEST-1",
            "reason": "Agreed trip fee",
        },
    )
    assert response.status_code == 200, response.text


def workspace(world, section, actor):
    response = world.get(f"/api/v1/finance/{section}", actor)
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.parametrize(
    "two_helpers,expected",
    [(False, [Decimal("580"), Decimal("1160")]), (True, [Decimal("435"), Decimal("435"), Decimal("870")])],
)
def test_individual_percentages_are_of_base_and_generated_once(finance_world, two_helpers, expected):
    world = finance_world
    delivered = completed(world, two_helpers)
    finalize_sources(world, delivered)
    for _attempt in range(2):
        result = command(world, f"/earnings/{delivered.trip_id}/calculate", world.owner)
        assert result.status_code == 200, result.text
    earnings = workspace(world, "payroll", world.hr)["earnings"]
    assert sorted(Decimal(entry["amount"]) for entry in earnings) == expected
    assert all(Decimal(entry["base"]) == Decimal("14500") for entry in earnings)


def test_missing_expenses_are_not_implicitly_zero_and_completion_is_independent(finance_world):
    world = finance_world
    delivered = completed(world)
    response = command(world, f"/earnings/{delivered.trip_id}/calculate", world.owner)
    assert response.status_code == 409 and response.json()["code"] == "PENDING_CALCULATION"
    response = command(
        world,
        f"/expenses/{delivered.trip_id}",
        delivered.driver,
        {"reason": "No lines supplied", "declared_zero": False},
    )
    assert response.status_code == 409
    assert world.get(f"/api/v1/trips/{delivered.trip_id}", world.dispatcher).json()["status"] == "COMPLETED"


def test_expense_review_forbids_combined_role_self_approval_and_resets_rejected_submission(finance_world):
    world = finance_world
    combined = world.employees.create((RoleCode.OWNER, RoleCode.DISPATCHER))
    delivered = completed(world)
    assert (
        command(
            world,
            f"/expenses/{delivered.trip_id}",
            combined,
            {"declared_zero": True, "reason": "No trip purchases"},
        ).status_code
        == 200
    )
    assert command(world, f"/expenses/{delivered.trip_id}/submit", combined).status_code == 200
    review = {"approved": True, "reason": "Independent review needed"}
    rejected = command(world, f"/expenses/{delivered.trip_id}/review", combined, review)
    assert rejected.status_code == 409 and rejected.json()["code"] == "SELF_APPROVAL_FORBIDDEN"
    assert (
        command(
            world,
            f"/expenses/{delivered.trip_id}/review",
            world.accounting,
            {"approved": False, "reason": "Confirm expense evidence"},
        ).status_code
        == 200
    )
    assert workspace(world, "expenses", combined)["expenses"][0]["state"] == "ENTERING"


def test_money_requires_decimal_strings_and_fuel_receipt_reference(finance_world):
    world = finance_world
    delivered = completed(world)
    response = command(
        world,
        f"/charges/{delivered.trip_id}",
        world.accounting,
        {"amount": 100.1, "agreed_amount": "100.10", "reference": "TEST-1", "reason": "Agreed charge"},
    )
    assert response.status_code == 422
    response = command(
        world,
        f"/expenses/{delivered.trip_id}",
        delivered.driver,
        {
            "reason": "Actual expenses",
            "lines": [
                {
                    "category": "FUEL",
                    "amount": "1.00",
                    "description": "Diesel purchase",
                    "incurred_on": manila_today().isoformat(),
                }
            ],
        },
    )
    assert response.status_code == 422


def test_zero_requires_independent_review_and_negative_base_creates_hold(finance_world):
    world = finance_world
    delivered = completed(world)
    finalize_sources(world, delivered, expense="21000.00")
    response = command(world, f"/earnings/{delivered.trip_id}/calculate", world.owner)
    assert response.status_code == 200 and response.json()["state"] == "HELD"
    assert workspace(world, "payroll", world.hr)["earnings"] == []
    assert workspace(world, "expenses", world.owner)["charges"][0]["held"] is True


def test_charge_variance_needs_different_owner_and_historical_rate_is_immutable(finance_world):
    world = finance_world
    delivered = completed(world)
    response = command(
        world,
        f"/charges/{delivered.trip_id}",
        world.owner,
        {
            "amount": "19999.00",
            "agreed_amount": "20000.00",
            "reference": "TEST-variance",
            "reason": "Rate variance",
        },
    )
    assert response.status_code == 200
    assert command(world, f"/charges/{delivered.trip_id}/approve-variance", world.owner).status_code == 409
    second_owner = world.employees.create((RoleCode.OWNER,))
    assert command(world, f"/charges/{delivered.trip_id}/approve-variance", second_owner).status_code == 200
    response = command(
        world,
        "/rates",
        world.owner,
        {
            "effective_on": (manila_today() + timedelta(days=1)).isoformat(),
            "driver_one": "9",
            "helper_one": "5",
            "driver_two": "7",
            "helper_two": "4",
            "reference": "Future rate agreement",
        },
    )
    assert response.status_code == 200
    with world.session_factory() as session:
        financial = FinancialRepository(session).find(
            __import__("backend.src.Entity.finance", fromlist=["TripFinancial"]).TripFinancial,
            trip_id=UUID(delivered.trip_id),
        )[0]
    assert str(financial.rate_id) == "00000000-0000-0000-0000-000000000005"


def invoice(world, delivered):
    response = command(
        world,
        "/invoices",
        world.accounting,
        {
            "client_id": str(world.client_id),
            "cutoff": manila_today().isoformat(),
            "trip_ids": [delivered.trip_id],
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["record_id"]


def test_billing_does_not_wait_for_expenses_payroll_or_payment(finance_world):
    world = finance_world
    delivered = completed(world)
    assert (
        command(
            world,
            f"/charges/{delivered.trip_id}",
            world.accounting,
            {
                "amount": "20000.00",
                "agreed_amount": "20000.00",
                "reference": "Agreement",
                "reason": "Trip charge",
            },
        ).status_code
        == 200
    )
    identifier = invoice(world, delivered)
    assert command(world, f"/invoices/{identifier}/issue", world.accounting).status_code == 200
    assert workspace(world, "billing", world.accounting)["invoices"][0]["state"] == "ISSUED"
    assert workspace(world, "expenses", world.accounting)["expenses"] == []


def test_active_bill_is_unique_void_is_independent_and_collections_preserve_credit(finance_world):
    world = finance_world
    delivered = completed(world)
    finalize_sources(world, delivered)
    identifier = invoice(world, delivered)
    duplicate = command(
        world,
        "/invoices",
        world.accounting,
        {
            "client_id": str(world.client_id),
            "cutoff": manila_today().isoformat(),
            "trip_ids": [delivered.trip_id],
        },
    )
    assert duplicate.status_code == 409
    assert command(world, f"/invoices/{identifier}/issue", world.accounting).status_code == 200
    payment = {
        "amount": "20500.00",
        "paid_on": manila_today().isoformat(),
        "method": "Bank reference",
        "reference": "TEST-collection",
    }
    assert (
        command(
            world, f"/invoices/{identifier}/payments", world.accounting, payment, key="collection-once"
        ).status_code
        == 200
    )
    assert (
        command(
            world, f"/invoices/{identifier}/payments", world.accounting, payment, key="collection-once"
        ).status_code
        == 200
    )
    body = workspace(world, "billing", world.accounting)
    assert Decimal(body["invoices"][0]["paid"]) == Decimal("20000")
    assert Decimal(body["invoices"][0]["unallocated_credit"]) == Decimal("500")
    assert len(body["payments"]) == 1
    assert (
        command(
            world,
            f"/invoices/{identifier}/request-void",
            world.accounting,
            {"reason": "Review duplicate invoice"},
        ).status_code
        == 200
    )
    assert (
        command(world, f"/invoices/{identifier}/approve-void", world.owner).json()["code"]
        == "INVOICE_HAS_COLLECTIONS"
    )


def test_receipt_correction_holds_earnings_and_invoice_in_one_transaction(finance_world):
    world = finance_world
    delivered = completed(world)
    finalize_sources(world, delivered)
    assert command(world, f"/earnings/{delivered.trip_id}/calculate", world.owner).status_code == 200
    identifier = invoice(world, delivered)
    assert command(world, f"/invoices/{identifier}/issue", world.accounting).status_code == 200
    corrected = world.post(
        f"/api/v1/trips/{delivered.trip_id}/receipt-correction",
        world.owner,
        {"reason": "Company has not received it"},
    )
    assert corrected.status_code == 200, corrected.text
    assert all(entry["state"] == "HELD" for entry in workspace(world, "payroll", world.hr)["earnings"])
    assert workspace(world, "billing", world.accounting)["invoices"][0]["held"]
    response = command(
        world,
        f"/invoices/{identifier}/payments",
        world.accounting,
        {"amount": "1.00", "paid_on": manila_today().isoformat(), "method": "Cash", "reference": "TEST-held"},
    )
    assert response.status_code == 409


def test_crew_cannot_read_other_pay_or_commercial_rates(finance_world):
    world = finance_world
    delivered = completed(world)
    finalize_sources(world, delivered)
    assert command(world, f"/earnings/{delivered.trip_id}/calculate", world.owner).status_code == 200
    payroll = workspace(world, "payroll", delivered.driver)
    assert {entry["employee_id"] for entry in payroll["earnings"]} == {str(delivered.driver.employee_id)}
    expense_view = workspace(world, "expenses", delivered.driver)
    assert expense_view["charges"] == [] and expense_view["rates"] == []
    assert all(entry["charge"] is None for entry in expense_view["trips"])
    outsider = world.make_driver()
    assert workspace(world, "expenses", outsider)["trips"] == []
    assert workspace(world, "payroll", outsider)["earnings"] == []
    assert world.get("/api/v1/finance/billing", outsider).status_code == 403


def test_report_flags_and_financial_field_permissions(finance_world):
    world = finance_world
    delivered = completed(world)
    owner = world.get("/api/v1/finance/reports", world.owner).json()
    assert "COMPLETED_WITHOUT_STAMPED_COPY" in owner["trips"][0]["flags"]
    dispatcher = world.get("/api/v1/finance/reports", world.dispatcher).json()
    assert dispatcher["financial_totals"] == {}
    stranger = world.make_driver()
    assert world.get("/api/v1/finance/reports", stranger).json()["trips"] == []
    assert (
        world.get("/api/v1/finance/reports", delivered.driver).json()["trips"][0]["trip_id"]
        == delivered.trip_id
    )


def test_idempotency_conflict_rejects_changed_payload_and_missing_key(finance_world):
    world = finance_world
    delivered = completed(world)
    payload = {"amount": "10.00", "agreed_amount": "10.00", "reference": "TEST", "reason": "Agreed charge"}
    assert (
        command(
            world, f"/charges/{delivered.trip_id}", world.accounting, payload, key="retry-charge"
        ).status_code
        == 200
    )
    payload["amount"] = "11.00"
    assert (
        command(world, f"/charges/{delivered.trip_id}", world.accounting, payload, key="retry-charge").json()[
            "code"
        ]
        == "IDEMPOTENCY_CONFLICT"
    )
    response = world.client.post(
        f"/api/v1/finance/charges/{delivered.trip_id}", headers=auth_headers(world.accounting), json=payload
    )
    assert response.status_code == 422


def ready_previous_payroll(world, delivered):
    previous_day = payroll_period(manila_today())[0] - timedelta(days=1)
    with world.session_factory() as session:
        row = session.get(TripRow, UUID(delivered.trip_id))
        row.receipt_confirmed_at = datetime.combine(previous_day, datetime.min.time(), UTC)
        session.commit()
    finalize_sources(world, delivered)
    assert command(world, f"/earnings/{delivered.trip_id}/calculate", world.owner).status_code == 200
    start_on, _end_on = payroll_period(previous_day)
    response = command(world, "/payrolls", world.hr, {"start_on": start_on.isoformat()})
    assert response.status_code == 200, response.text
    return response.json()["record_id"], start_on


def approved_advance(world, driver, start_on):
    response = command(
        world,
        "/advances",
        driver,
        {"employee_id": str(driver.employee_id), "amount": "1000.00", "reason": "Personal advance request"},
    )
    assert response.status_code == 200
    identifier = response.json()["record_id"]
    response = command(
        world,
        f"/advances/{identifier}/approve",
        world.owner,
        {
            "amount": "1000.00",
            "installment": "200.00",
            "start_on": start_on.isoformat(),
            "acknowledgment": "Employee written agreement TEST-1",
            "reason": "Reviewed request",
        },
    )
    assert response.status_code == 200, response.text
    return identifier


def test_advance_debt_starts_on_release_draft_does_not_repay_and_finalization_retries_once(finance_world):
    world = finance_world
    delivered = completed(world)
    payroll_id, start_on = ready_previous_payroll(world, delivered)
    advance_id = approved_advance(world, delivered.driver, start_on)
    assert Decimal(workspace(world, "advances", world.hr)["advances"][0]["balance"]) == 0
    response = command(
        world,
        f"/advances/{advance_id}/release",
        world.hr,
        {"amount": "500.00", "occurred_on": manila_today().isoformat(), "reference": "Release TEST-1"},
    )
    assert response.status_code == 200, response.text
    preview = workspace(world, "payroll", world.hr)
    assert sum(Decimal(entry["repayments"]) for entry in preview["statements"]) == Decimal("200")
    assert Decimal(workspace(world, "advances", world.hr)["advances"][0]["balance"]) == Decimal("500")
    for _attempt in range(2):
        response = command(world, f"/payrolls/{payroll_id}/finalize", world.hr, key="finalize-payroll-once")
        assert response.status_code == 200, response.text
    assert Decimal(workspace(world, "advances", world.hr)["advances"][0]["balance"]) == Decimal("300")
    with world.session_factory() as session:
        assert len(FinancialRepository(session).find(AdvanceMovement, kind="REPAYMENT")) == 1
    response = command(
        world, f"/payrolls/{payroll_id}/reverse", world.owner, {"reason": "Correct unpaid payroll"}
    )
    assert response.status_code == 200, response.text
    assert Decimal(workspace(world, "advances", world.hr)["advances"][0]["balance"]) == Decimal("500")


def test_hr_records_payment_owner_cannot_and_paid_payroll_cannot_be_reversed(finance_world):
    world = finance_world
    delivered = completed(world)
    payroll_id, _start_on = ready_previous_payroll(world, delivered)
    assert command(world, f"/payrolls/{payroll_id}/finalize", world.hr).status_code == 200
    statement = workspace(world, "payroll", world.hr)["statements"][0]
    payment = {
        "amount": "1.00",
        "paid_on": manila_today().isoformat(),
        "method": "Cash",
        "reference": "TEST-payroll",
    }
    assert (
        command(world, f"/statements/{statement['record_id']}/payments", world.owner, payment).status_code
        == 403
    )
    assert (
        command(world, f"/statements/{statement['record_id']}/payments", world.hr, payment).status_code == 200
    )
    assert (
        command(
            world, f"/payrolls/{payroll_id}/reverse", world.owner, {"reason": "Review payment first"}
        ).json()["code"]
        == "PAYROLL_HAS_PAYMENTS"
    )


def test_deductions_closed_by_default_and_advance_approval_needs_owner_delegation(finance_world):
    world = finance_world
    driver = world.make_driver()
    response = command(
        world,
        "/adjustments",
        world.hr,
        {
            "employee_id": str(driver.employee_id),
            "amount": "1.00",
            "kind": "VOLUNTARY",
            "period_start": payroll_period(manila_today())[0].isoformat(),
            "reason": "Requested deduction",
            "authorization": "Consent TEST-1",
        },
    )
    assert response.status_code == 409 and response.json()["code"] == "DEDUCTIONS_DISABLED"
    response = command(
        world,
        "/advances",
        driver,
        {"employee_id": str(driver.employee_id), "amount": "100.00", "reason": "Personal request"},
    )
    identifier = response.json()["record_id"]
    approval = {
        "amount": "100.00",
        "installment": "20.00",
        "start_on": payroll_period(manila_today())[0].isoformat(),
        "acknowledgment": "Agreement TEST-2",
        "reason": "Reviewed request",
    }
    assert command(world, f"/advances/{identifier}/approve", world.hr, approval).status_code == 403
    response = command(
        world,
        "/advance-delegations",
        world.owner,
        {
            "employee_id": str(world.hr.employee_id),
            "expires_on": manila_today().isoformat(),
            "reason": "Owner absent today",
        },
    )
    assert response.status_code == 200
    assert command(world, f"/advances/{identifier}/approve", world.hr, approval).status_code == 200
    assert (
        command(
            world,
            f"/advances/{identifier}/release",
            world.hr,
            {"amount": "100.00", "occurred_on": manila_today().isoformat(), "reference": "TEST-release"},
        ).json()["code"]
        == "SELF_APPROVAL_FORBIDDEN"
    )


def test_commit_failure_rolls_back_charge_and_retry_record_together(finance_world, monkeypatch):
    from backend.src.Repository.unit_of_work import SqlAlchemyUnitOfWork

    world = finance_world
    delivered = completed(world)
    original = SqlAlchemyUnitOfWork.commit

    def fail_commit(_self):
        raise RuntimeError("Injected transaction failure")

    monkeypatch.setattr(SqlAlchemyUnitOfWork, "commit", fail_commit)
    payload = {
        "amount": "10.00",
        "agreed_amount": "10.00",
        "reference": "TEST-rollback",
        "reason": "Agreed charge",
    }
    response = command(
        world, f"/charges/{delivered.trip_id}", world.accounting, payload, key="rollback-retry"
    )
    assert response.status_code == 500
    monkeypatch.setattr(SqlAlchemyUnitOfWork, "commit", original)
    assert workspace(world, "expenses", world.owner)["charges"][0]["charge"] is None
    assert (
        command(
            world, f"/charges/{delivered.trip_id}", world.accounting, payload, key="rollback-retry"
        ).status_code
        == 200
    )
