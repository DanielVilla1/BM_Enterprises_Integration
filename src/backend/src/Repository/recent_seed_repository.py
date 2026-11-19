"""Bounded, fictional hauling data; no services, storage uploads or identity calls."""

from datetime import UTC, datetime, time, timedelta
from decimal import Decimal
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import Connection, Table, delete, select, tuple_, update
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from ..Entity.clock import MANILA_OFFSET
from .finance_models import ExpenseSheetRow, FinanceLockRow, TripFinancialRow
from .orm_models import (
    AuditLogRow,
    ClientRow,
    DeliveryOrderRow,
    DriverLicenseRow,
    EmployeeRoleRow,
    EmployeeRow,
    TripCrewRow,
    TripRow,
    TruckRow,
)

SEED_NAMESPACE = "bm-enterprises-recent-mock-v1:"
TODAY_COUNT = 6


def seed_id(label: str) -> UUID:
    """Fixed slots, independent of date, prevent growth across successive days."""
    return uuid5(NAMESPACE_URL, SEED_NAMESPACE + label)


def build_dataset(now: datetime | None = None) -> dict[Table, list[dict]]:
    """Capture one clock reading, use Manila calendar days and store UTC timestamps."""
    now = datetime.now(UTC) if now is None else now
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("The seed clock must include a timezone.")
    now = now.astimezone(UTC)
    today = now.astimezone(MANILA_OFFSET).date()
    start = datetime.combine(today - timedelta(days=29), time(), MANILA_OFFSET).astimezone(UTC)
    midnight = datetime.combine(today, time(), MANILA_OFFSET).astimezone(UTC)
    data: dict[Table, list[dict]] = {
        model.__table__: []
        for model in (
            EmployeeRow,
            EmployeeRoleRow,
            ClientRow,
            TruckRow,
            DriverLicenseRow,
            DeliveryOrderRow,
            TripRow,
            TripCrewRow,
            TripFinancialRow,
            ExpenseSheetRow,
            AuditLogRow,
        )
    }
    staff = [
        ("dispatch", "Mara Santos", "DISPATCHER"),
        ("accounting", "Paolo Reyes", "ACCOUNTING"),
        ("driver-0", "Luis Garcia", "DRIVER"),
        ("helper-0", "Nico Cruz", "HELPER"),
        ("driver-1", "Carlo Ramos", "DRIVER"),
        ("helper-1", "Joel Mendoza", "HELPER"),
        ("driver-2", "Ramon Flores", "DRIVER"),
        ("helper-2", "Ben Torres", "HELPER"),
    ]
    for label, name, role in staff:
        data[EmployeeRow.__table__].append(
            dict(
                employee_id=seed_id(label),
                full_name=name,
                email=f"{name.lower().replace(' ', '.')}@sample.invalid",
                is_active=True,
                created_at=start,
            )
        )
        data[EmployeeRoleRow.__table__].append(
            dict(employee_id=seed_id(label), role_code=role, assigned_at=start)
        )
    for index, name in enumerate(("Laguna Steel Supply", "Cavite Fabrication")):
        data[ClientRow.__table__].append(
            dict(
                client_id=seed_id(f"client-{index}"),
                name=name,
                address=("Calamba, Laguna", "Dasmarinas, Cavite")[index],
                contact_person=("Elena Villanueva", "Miguel Navarro")[index],
                is_active=True,
                created_at=start,
            )
        )
    for index, status in enumerate(("ASSIGNED", "IN_TRANSIT", "ASSIGNED", "AVAILABLE")):
        data[TruckRow.__table__].append(
            dict(
                truck_id=seed_id(f"truck-{index}"),
                plate_number=("NCP-4721", "NDR-6835", "NFB-2958", "NGR-8164")[index],
                description="25-ton steel hauling flatbed",
                capacity_tons=Decimal("25"),
                status=status,
                is_active=True,
                created_at=start,
            )
        )
    for index in range(3):
        data[DriverLicenseRow.__table__].append(
            dict(
                employee_id=seed_id(f"driver-{index}"),
                license_number=f"D12-24-1580{index:02d}",
                expiry_date=today,
                updated_at=start,
            )
        )

    # Every historical date is represented. Five busier weekdays get a second order;
    # weekends have one each. Today's six entries are a separate, guaranteed batch.
    days = [today - timedelta(days=29 - index) for index in range(29)]
    busy_days = set(
        sorted((day for day in days if day.weekday() < 5), key=lambda day: day.toordinal() * 17 % 31)[:5]
    )
    order_days = days + sorted(busy_days) + [today] * TODAY_COUNT
    pickups = ("Batangas steel yard", "Calamba loading depot", "Manila port yard")
    destinations = ("Santa Rosa warehouse", "Dasmarinas workshop", "Binan plant")
    orders = data[DeliveryOrderRow.__table__]
    for index, day in enumerate(order_days):
        if day == today:
            slot = index - len(order_days) + TODAY_COUNT
            created_at = midnight + (now - midnight) * ((slot + 1) / (TODAY_COUNT + 1))
        else:
            created_at = datetime.combine(
                day, time(hour=7 + index * 7 % 11, minute=index * 13 % 60), MANILA_OFFSET
            ).astimezone(UTC)
        orders.append(
            dict(
                order_id=seed_id(f"order-{index}"),
                client_id=seed_id(f"client-{index % 2}"),
                client_reference=f"DO-{day:%Y%m%d}-{index + 1:03d}",
                pickup_location=pickups[index % len(pickups)],
                delivery_location=destinations[index % len(destinations)],
                scheduled_date=day,
                total_weight_tons=Decimal(("12.5", "16", "20", "22")[index % 4]),
                status="CANCELLED" if day < today and index % 5 == 0 else "PENDING",
                notes=("Steel sections", "Reinforcing bars", "Fabricated steel frames")[index % 3],
                cancellation_reason="Customer postponed request" if day < today and index % 5 == 0 else None,
                created_by=seed_id("dispatch"),
                created_at=created_at,
            )
        )

    trip_orders = [5, 17, 27, 34, 35, 36]
    states = ["FAILED", "FAILED", "CANCELLED", "SCHEDULED", "IN_TRANSIT", "DELIVERED_OR_PENDING"]
    for index, (order_index, state) in enumerate(zip(trip_orders, states, strict=True)):
        order = orders[order_index]
        created_at = order["created_at"]
        end = now if order["scheduled_date"] == today else created_at + timedelta(hours=3)

        def stage(part: int, created_at: datetime = created_at, end: datetime = end) -> datetime:
            return created_at + (end - created_at) * (part / 6)

        crew = index % 3
        driver = seed_id(f"driver-{crew}")
        trip_id = seed_id(f"trip-{index}")
        departed = state in {"FAILED", "IN_TRANSIT", "DELIVERED_OR_PENDING"}
        order["status"] = "CANCELLED" if index < 3 else "SCHEDULED" if index == 3 else "IN_PROGRESS"
        order["cancellation_reason"] = "Request withdrawn after yard closure" if index < 3 else None
        data[TripRow.__table__].append(
            dict(
                trip_id=trip_id,
                order_id=order["order_id"],
                truck_id=seed_id(f"truck-{crew}"),
                load_tons=order["total_weight_tons"],
                status=state,
                created_by=seed_id("dispatch"),
                created_at=created_at,
                accepted_at=stage(1) if departed else None,
                cleared_at=stage(2) if departed else None,
                departed_at=stage(3) if departed else None,
                delivered_at=stage(4) if state == "DELIVERED_OR_PENDING" else None,
                closed_reason="Receiving yard closed" if index < 3 else None,
                or_uploaded_at=None,
                or_uploaded_by=None,
                receipt_confirmed_at=None,
                receipt_confirmed_by=None,
                receipt_received_at=None,
            )
        )
        for role in ("DRIVER", "HELPER"):
            data[TripCrewRow.__table__].append(
                dict(
                    crew_entry_id=seed_id(f"crew-{index}-{role}"),
                    trip_id=trip_id,
                    employee_id=seed_id(f"{role.lower()}-{crew}"),
                    crew_role=role,
                    assigned_at=created_at,
                    removed_at=None,
                )
            )
        charge = Decimal(16000 + index * 1500) if index >= 3 else None
        data[TripFinancialRow.__table__].append(
            dict(
                record_id=seed_id(f"financial-{index}"),
                created_at=stage(1),
                trip_id=trip_id,
                rate_id=None,
                charge=charge,
                agreed_amount=charge,
                reference=f"HAUL-{order['scheduled_date']:%Y%m%d}-{index + 1:03d}" if charge else "",
                charge_state="FINALIZED" if charge else "MISSING",
                entered_by=seed_id("accounting") if charge else None,
                finalized_by=seed_id("accounting") if charge else None,
                reason="Agreed steel hauling charge",
                held=False,
                hold_reason="",
            )
        )
        if departed:
            amount = Decimal(1500 + index * 325)
            data[ExpenseSheetRow.__table__].append(
                dict(
                    record_id=seed_id(f"expenses-{index}"),
                    created_at=stage(5),
                    trip_id=trip_id,
                    entered_by=driver,
                    state="FINALIZED" if index < 3 else "ENTERING" if index == 4 else "AWAITING_REVIEW",
                    lines=[
                        dict(
                            category="FUEL",
                            amount=str(amount),
                            description="Diesel for steel delivery route",
                            incurred_on=order["scheduled_date"].isoformat(),
                            evidence=f"FUEL-{order['scheduled_date']:%Y%m%d}-{index + 1:03d}",
                        )
                    ],
                    contributors=[str(driver)],
                    declared_zero=False,
                    reason="Route fuel expense",
                    reviewed_by=seed_id("accounting") if index < 3 else None,
                    total=amount,
                )
            )
    data[AuditLogRow.__table__].append(
        dict(
            audit_id=seed_id("audit"),
            occurred_at=now,
            actor_employee_id=None,
            action="mock.recent_seeded",
            entity_type="mock_dataset",
            entity_id=str(seed_id("dataset")),
            details={"fictional": True, "namespace": SEED_NAMESPACE, "orders": len(orders)},
        )
    )
    return data


def seed_recent(
    connection: Connection, data: dict[Table, list[dict]], *, renew: bool = False
) -> dict[str, int]:
    """Twelve statements normally; renewal adds one guard read and ten exact-ID deletes."""
    dialect = connection.dialect.name
    if dialect not in {"postgresql", "sqlite"}:
        raise ValueError("Recent mock seeding supports PostgreSQL and SQLite only.")
    # Match the application's lock order; also serializes concurrent seed runs.
    locked = connection.execute(
        update(FinanceLockRow).where(FinanceLockRow.record_id == 1).values(version=FinanceLockRow.version + 1)
    )
    if locked.rowcount != 1:
        raise ValueError("Finance lock is missing; run Alembic upgrade head first.")
    if renew:
        employee_ids = [row["employee_id"] for row in data[EmployeeRow.__table__]]
        linked_employee = connection.scalar(
            select(EmployeeRow.employee_id)
            .where(EmployeeRow.employee_id.in_(employee_ids), EmployeeRow.clerk_user_id.is_not(None))
            .limit(1)
        )
        if linked_employee is not None:
            raise ValueError("Cannot renew sample employees linked to real sign-in accounts.")
        # Never use names, prefixes or broad table cleanup. Foreign keys reject any
        # external dependants and roll back every delete if the samples are in use.
        for table, rows in reversed(list(data.items())):
            if table is AuditLogRow.__table__:
                continue
            keys = list(table.primary_key.columns)
            identifiers = [tuple(row[column.name] for column in keys) for row in rows]
            connection.execute(delete(table).where(tuple_(*keys).in_(identifiers)))
    insert = postgres_insert if dialect == "postgresql" else sqlite_insert
    for table, rows in data.items():
        statement = insert(table).values(rows)
        keys = list(table.primary_key.columns)
        if table is AuditLogRow.__table__:
            # The real audit log is append-only. Preserve the original seed event.
            statement = statement.on_conflict_do_nothing(index_elements=keys)
        else:
            statement = statement.on_conflict_do_update(
                index_elements=keys,
                set_={key: statement.excluded[key] for key in rows[0] if key not in table.primary_key},
            )
        connection.execute(statement)
    return {table.name: len(rows) for table, rows in data.items()}
