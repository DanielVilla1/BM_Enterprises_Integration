# ===== AI GENERATED: PresentationSeedRepository =====
# Purpose: Add a repeatable, entirely fictional presentation dataset without rewriting existing records.
# Inputs: A development database session; all identifiers live in a fixed demo namespace.
# Returns: Counts of inserted presentation records and a persistent seed marker.
# Flow: Create unlinked demo employees and operating records; add financial snapshots; audit once.

from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy.orm import Session

from ..Entity.clock import manila_today
from ..Entity.finance import (
    ZERO,
    Advance,
    AdvanceMovement,
    Earning,
    ExpenseSheet,
    FinancialOperation,
    FinancialPayment,
    Invoice,
    InvoiceLine,
    Payroll,
    PayStatement,
    TripFinancial,
    money,
    payroll_period,
)
from .audit_repository import AuditRepository
from .financial_repository import FinancialRepository
from .orm_models import (
    ClientRow,
    DeliveryOrderRow,
    DriverLicenseRow,
    EmployeeRoleRow,
    EmployeeRow,
    OrDocumentRow,
    TripCrewRow,
    TripRow,
    TruckRow,
)


def demo_id(label: str) -> UUID:
    """Stable IDs isolate the demo set and make accidental repeated inserts fail safely."""
    return uuid5(NAMESPACE_URL, "bm-enterprises-presentation-v1:" + label)


def demo_time(day: date, hour: int = 1) -> datetime:
    return datetime.combine(day, time(hour=hour), UTC)


class PresentationSeedRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.finances = FinancialRepository(session)

    def _employee(self, label: str, role: str) -> UUID:
        identifier = demo_id(label)
        self.session.add(
            EmployeeRow(
                employee_id=identifier,
                full_name=f"DEMO {label}",
                email=f"{identifier.hex}@presentation.invalid",
                is_active=True,
                clerk_user_id=None,
                created_at=demo_time(manila_today() - timedelta(days=60)),
            )
        )
        self.session.flush()
        self.session.add(EmployeeRoleRow(employee_id=identifier, role_code=role))
        self.session.flush()
        return identifier

    def seed(self) -> dict[str, int]:
        self.finances.lock()
        previous = self.finances.find(FinancialOperation, key="presentation-seed-v1")
        if previous:
            return {"already_loaded": 1, **previous[0].response}
        today = manila_today()
        period_start, period_end = payroll_period(today - timedelta(days=35))
        owner = self._employee("Olivia Owner", "OWNER")
        dispatcher = self._employee("Drew Dispatcher", "DISPATCHER")
        accounting = self._employee("Avery Accounting", "ACCOUNTING")
        payroll_staff = self._employee("Harper Payroll", "HR_PAYROLL")
        self._employee("Frankie Fleet", "FLEET_MANAGER")
        client_ids = [demo_id(f"client-{index}") for index in range(2)]
        for client_id, name in zip(client_ids, ("North Steel", "Harbor Fabrication"), strict=True):
            self.session.add(
                ClientRow(
                    client_id=client_id,
                    name=f"DEMO PRESENTATION - {name}",
                    address="Fictional presentation address",
                    contact_person="DEMO contact",
                    is_active=True,
                )
            )
        self.session.flush()
        payroll = self.finances.save(
            Payroll(
                record_id=demo_id("payroll-final"),
                start_on=period_start,
                end_on=period_end,
                prepared_by=payroll_staff,
                finalized_by=payroll_staff,
                state="FINALIZED",
            )
        )
        current_start, current_end = payroll_period(today)
        self.finances.save(
            Payroll(
                record_id=demo_id("payroll-draft"),
                start_on=current_start,
                end_on=current_end,
                prepared_by=payroll_staff,
            )
        )
        charge_amounts = ["20000", "0", "18000", "0", "2000", "24000", "26000", "0"]
        expense_amounts = ["5500", "3200", "0", "1500", "2500", "4200", "6200", "0"]
        rate_id = UUID("00000000-0000-0000-0000-000000000005")
        earning_count = 0
        for index in range(8):
            driver = self._employee(f"Driver {index + 1:02d}", "DRIVER")
            helpers = [self._employee(f"Helper {index + 1:02d}A", "HELPER")]
            if index == 2:
                helpers.append(self._employee("Helper 03B", "HELPER"))
            self.session.add(
                DriverLicenseRow(
                    employee_id=driver,
                    license_number=f"DEMO-{index + 1:05d}",
                    expiry_date=today + timedelta(days=365),
                )
            )
            truck_id, order_id, trip_id = (demo_id(f"{kind}-{index}") for kind in ("truck", "order", "trip"))
            state = "OR_UPLOADED" if index == 3 else "SCHEDULED" if index == 7 else "COMPLETED"
            day = today if index in (3, 7) else period_start + timedelta(days=2 + index)
            self.session.add(
                TruckRow(
                    truck_id=truck_id,
                    plate_number=f"DEMO-{index + 1:03d}",
                    description="Fictional presentation truck",
                    capacity_tons=Decimal("25"),
                    status="ASSIGNED" if index in (3, 7) else "AVAILABLE",
                    is_active=True,
                )
            )
            self.session.add(
                DeliveryOrderRow(
                    order_id=order_id,
                    client_id=client_ids[index % 2],
                    client_reference=f"DEMO-PRESENTATION-{index + 1:03d}",
                    pickup_location="DEMO North loading yard",
                    delivery_location="DEMO receiving warehouse",
                    scheduled_date=day,
                    total_weight_tons=Decimal("20"),
                    status="SCHEDULED" if index == 7 else "IN_PROGRESS" if index == 3 else "COMPLETED",
                    notes="PRESENTATION ONLY - fictional order",
                    created_by=dispatcher,
                    created_at=demo_time(day - timedelta(days=1)),
                )
            )
            self.session.flush()
            self.session.add(
                TripRow(
                    trip_id=trip_id,
                    order_id=order_id,
                    truck_id=truck_id,
                    load_tons=Decimal("20"),
                    status=state,
                    created_by=dispatcher,
                    created_at=demo_time(day - timedelta(days=1)),
                    accepted_at=None if index == 7 else demo_time(day),
                    cleared_at=None if index == 7 else demo_time(day),
                    departed_at=None if index == 7 else demo_time(day, 1),
                    delivered_at=None if index == 7 else demo_time(day, 2),
                    or_uploaded_at=None if index == 7 else demo_time(day, 3),
                    or_uploaded_by=None if index == 7 else driver,
                    receipt_confirmed_at=demo_time(day, 4) if state == "COMPLETED" else None,
                    receipt_confirmed_by=driver if state == "COMPLETED" else None,
                    receipt_received_at=demo_time(day, 4) if state == "COMPLETED" else None,
                )
            )
            self.session.flush()
            for employee_id, role in [(driver, "DRIVER"), *((helper, "HELPER") for helper in helpers)]:
                self.session.add(TripCrewRow(trip_id=trip_id, employee_id=employee_id, crew_role=role))
            if index != 7:
                kinds = ["SIGNED_OR", "STAMPED_COPY"] if index in (0, 2, 6) else ["SIGNED_OR"]
                for kind in kinds:
                    self.session.add(
                        OrDocumentRow(
                            document_id=demo_id(f"document-{index}-{kind}"),
                            trip_id=trip_id,
                            kind=kind,
                            storage_path=f"presentation/{trip_id}/{kind}.png",
                            content_type="image/png",
                            size_bytes=1024,
                            uploaded_by=driver,
                            uploaded_at=demo_time(day, 3),
                        )
                    )
            self.session.flush()
            amount = Decimal(expense_amounts[index])
            expense_state = (
                "AWAITING_REVIEW" if index in (1, 3) else "CONFIRMED_ZERO" if index == 2 else "FINALIZED"
            )
            if index != 7:
                lines = (
                    []
                    if index == 2
                    else [
                        {
                            "category": "FUEL",
                            "amount": str(amount),
                            "description": "DEMO diesel purchase",
                            "incurred_on": day.isoformat(),
                            "evidence": f"DEMO-RECEIPT-{index + 1:03d}",
                        }
                    ]
                )
                self.finances.save(
                    ExpenseSheet(
                        record_id=demo_id(f"expenses-{index}"),
                        trip_id=trip_id,
                        entered_by=driver,
                        contributors=[str(driver)],
                        state=expense_state,
                        lines=lines,
                        declared_zero=index == 2,
                        total=amount,
                        reviewed_by=None if index in (1, 3) else accounting,
                        reason="PRESENTATION ONLY - fictional expenses",
                    )
                )
            charge = Decimal(charge_amounts[index])
            self.finances.save(
                TripFinancial(
                    record_id=demo_id(f"financial-{index}"),
                    trip_id=trip_id,
                    rate_id=None if index == 7 else rate_id,
                    charge=charge if charge else None,
                    agreed_amount=charge if charge else None,
                    charge_state="FINALIZED" if charge else "MISSING",
                    entered_by=accounting if charge else None,
                    finalized_by=accounting if charge else None,
                    reference=f"DEMO-AGREEMENT-{index + 1:03d}" if charge else "",
                    reason="PRESENTATION ONLY",
                    held=index == 4,
                    hold_reason="NEGATIVE_EARNINGS_BASE" if index == 4 else "",
                )
            )
            if index in (0, 2, 5, 6):
                base = charge - amount
                percentages = (
                    [Decimal("6"), Decimal("3"), Decimal("3")] if index == 2 else [Decimal("8"), Decimal("4")]
                )
                for position, (employee_id, percentage) in enumerate(
                    zip([driver, *helpers], percentages, strict=True)
                ):
                    gross = money(base * percentage / Decimal("100"))
                    earning = self.finances.save(
                        Earning(
                            record_id=demo_id(f"earning-{index}-{position}"),
                            trip_id=trip_id,
                            employee_id=employee_id,
                            rate_id=rate_id,
                            percentage=percentage,
                            base=base,
                            amount=gross,
                            original_date=day,
                            payroll_id=payroll.record_id if index in (0, 2) else None,
                        )
                    )
                    earning_count += 1
                    if index in (0, 2):
                        repayment = Decimal("200") if index == 0 and position == 0 else ZERO
                        statement = self.finances.save(
                            PayStatement(
                                record_id=demo_id(f"statement-{index}-{position}"),
                                payroll_id=payroll.record_id,
                                employee_id=employee_id,
                                gross=gross,
                                deductions=ZERO,
                                repayments=repayment,
                                net=gross - repayment,
                                lines=[
                                    {
                                        "kind": "EARNING",
                                        "record_id": str(earning.record_id),
                                        "trip_id": str(trip_id),
                                        "original_date": day.isoformat(),
                                        "percentage": str(percentage),
                                        "amount": str(gross),
                                    }
                                ]
                                + (
                                    [
                                        {
                                            "kind": "REPAYMENT",
                                            "advance_id": str(demo_id("personal-released")),
                                            "amount": "200.00",
                                        }
                                    ]
                                    if repayment
                                    else []
                                ),
                            )
                        )
                        if index == 0 and position == 0:
                            self.finances.save(
                                FinancialPayment(
                                    record_id=demo_id("payroll-payment"),
                                    statement_id=statement.record_id,
                                    amount=Decimal("500"),
                                    allocated=Decimal("500"),
                                    paid_on=period_end + timedelta(days=1),
                                    method="DEMO cash record",
                                    reference="PRESENTATION ONLY - no money transferred",
                                    actor_id=payroll_staff,
                                )
                            )
            if index in (0, 2, 6):
                invoice = self.finances.save(
                    Invoice(
                        record_id=demo_id(f"invoice-{index}"),
                        client_id=client_ids[index % 2],
                        cutoff=period_end,
                        entered_by=accounting,
                        total=charge,
                        state="DRAFT" if index == 2 else "ISSUED",
                        issued_on=None if index == 2 else period_end + timedelta(days=1),
                        due_on=None if index == 2 else period_end + timedelta(days=31),
                        reason="PRESENTATION ONLY",
                    )
                )
                self.finances.save(
                    InvoiceLine(
                        record_id=demo_id(f"invoice-line-{index}"),
                        invoice_id=invoice.record_id,
                        trip_id=trip_id,
                        amount=charge,
                        delivered_on=day,
                    )
                )
                if index in (0, 6):
                    collected = Decimal("8000") if index == 0 else charge
                    self.finances.save(
                        FinancialPayment(
                            record_id=demo_id(f"collection-{index}"),
                            invoice_id=invoice.record_id,
                            amount=collected,
                            allocated=collected,
                            paid_on=period_end + timedelta(days=2),
                            method="DEMO bank record",
                            reference="PRESENTATION ONLY - no collection occurred",
                            actor_id=accounting,
                        )
                    )
            if index in (0, 1, 2, 3):
                advance_id = demo_id("personal-released" if index == 0 else f"advance-{index}")
                advance_state = "REQUESTED" if index == 1 else "APPROVED" if index == 2 else "RELEASED"
                self.finances.save(
                    Advance(
                        record_id=advance_id,
                        employee_id=driver,
                        requested_by=driver if index != 3 else payroll_staff,
                        amount=Decimal("1000"),
                        reason="PRESENTATION ONLY - fictional advance",
                        kind="OPERATING" if index == 3 else "PERSONAL",
                        trip_id=trip_id if index == 3 else None,
                        state="RELEASED" if index == 0 else advance_state,
                        approved_by=None if index == 1 else owner,
                        installment=ZERO if index in (1, 3) else Decimal("200"),
                        start_on=None if index == 1 else period_start,
                        acknowledgment="DEMO written acknowledgment" if index != 1 else "",
                    )
                )
                if index in (0, 3):
                    self.finances.save(
                        AdvanceMovement(
                            record_id=demo_id(f"release-{index}"),
                            advance_id=advance_id,
                            kind="RELEASE",
                            amount=Decimal("1000"),
                            actor_id=payroll_staff,
                            reference="DEMO release, no real transfer",
                            occurred_on=day,
                        )
                    )
                if index == 0:
                    self.finances.save(
                        AdvanceMovement(
                            record_id=demo_id("repayment"),
                            advance_id=advance_id,
                            kind="REPAYMENT",
                            amount=Decimal("200"),
                            actor_id=payroll_staff,
                            reference="DEMO finalized payroll",
                            occurred_on=period_end + timedelta(days=1),
                            payroll_id=payroll.record_id,
                        )
                    )
        counts = {"trips": 8, "earnings": earning_count, "invoices": 3, "advances": 4, "payrolls": 2}
        self.finances.save(
            FinancialOperation(
                record_id=demo_id("seed-marker"),
                actor_id=owner,
                key="presentation-seed-v1",
                fingerprint="presentation-seed-v1",
                response=counts,
            )
        )
        AuditRepository(self.session).append(
            None,
            "presentation.seeded",
            "presentation_dataset",
            str(demo_id("seed-marker")),
            {"fictional": True, **counts},
            None,
        )
        self.session.commit()
        return counts
