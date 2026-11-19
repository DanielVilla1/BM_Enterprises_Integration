"""Rolling-window, write-budget and transaction safety checks for the hosted seed."""

import json
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import DateTime, event, func, select
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError

from backend.scripts.seed_recent import validate_target
from backend.src.Entity.clock import MANILA_OFFSET
from backend.src.Repository.finance_models import ExpenseSheetRow, FinanceLockRow
from backend.src.Repository.orm_models import AuditLogRow, ClientRow, EmployeeRow, TripRow
from backend.src.Repository.recent_seed_repository import build_dataset, seed_id, seed_recent


@pytest.mark.parametrize(
    "now",
    [
        datetime(2026, 11, 19, 0, 0, tzinfo=MANILA_OFFSET),
        datetime(2026, 11, 21, 0, 0, 0, 1, tzinfo=MANILA_OFFSET),
        datetime(2026, 11, 22, 23, 59, 59, tzinfo=MANILA_OFFSET),
        datetime(2024, 3, 1, 8, 20, tzinfo=MANILA_OFFSET),
        datetime(2027, 1, 1, 0, 5, tzinfo=UTC),
    ],
)
def test_window_includes_all_dates_and_six_today_without_future_timestamps(now):
    data = build_dataset(now)
    today = now.astimezone(MANILA_OFFSET).date()
    start = today - timedelta(days=29)
    orders = next(rows for table, rows in data.items() if table.name == "delivery_orders")
    assert sum(map(len, data.values())) == 94
    assert len(orders) == 40
    assert {row["scheduled_date"] for row in orders} == {start + timedelta(days=i) for i in range(30)}
    assert len([row for row in orders if row["scheduled_date"] == today]) == 6
    for day in (start + timedelta(days=i) for i in range(29)):
        day_rows = [row for row in orders if row["scheduled_date"] == day]
        assert len(day_rows) == 1 if day.weekday() >= 5 else len(day_rows) in (1, 2)
    for table, rows in data.items():
        for row in rows:
            for key, value in row.items():
                if value is not None and isinstance(table.c[key].type, DateTime):
                    assert start <= value.astimezone(MANILA_OFFSET).date() <= today
                    assert value <= now
    trips = data[TripRow.__table__]
    assert len({row["truck_id"] for row in trips[3:]}) == 3
    for trip in trips:
        stages = [
            trip[key] for key in ("created_at", "accepted_at", "cleared_at", "departed_at", "delivered_at")
        ]
        stages = [value for value in stages if value is not None]
        assert stages == sorted(stages)
    for sheet in data[ExpenseSheetRow.__table__]:
        assert sheet["total"] == sum(Decimal(line["amount"]) for line in sheet["lines"])
        assert sheet["reviewed_by"] != sheet["entered_by"]


def test_naive_clock_is_rejected():
    with pytest.raises(ValueError, match="timezone"):
        build_dataset(datetime(2026, 11, 19))


def test_business_values_use_realistic_names_and_keep_internal_sample_provenance():
    data = build_dataset()
    for table, rows in data.items():
        if table is not AuditLogRow.__table__:
            text = json.dumps(rows, default=str).upper()
            assert "MOCK" not in text and "DEMO" not in text and "FICTIONAL" not in text
    assert data[EmployeeRow.__table__][0]["full_name"] == "Mara Santos"
    assert data[AuditLogRow.__table__][0]["details"]["fictional"] is True


def test_renew_replaces_old_seed_rows_without_growth_or_erasing_audit_history(session_factory):
    engine = session_factory.kw["bind"]
    data = build_dataset()
    old_data = build_dataset()
    old_data[EmployeeRow.__table__][0].update(full_name="MOCK 30D - Mara Santos")
    with engine.begin() as connection:
        seed_recent(connection, old_data)
        connection.execute(
            EmployeeRow.__table__.update()
            .where(EmployeeRow.employee_id == seed_id("dispatch"))
            .values(phone="obsolete sample")
        )
    with engine.begin() as connection:
        counts = seed_recent(connection, data, renew=True)
        assert sum(counts.values()) == 94
        employee = connection.execute(
            select(EmployeeRow.full_name, EmployeeRow.phone).where(
                EmployeeRow.employee_id == seed_id("dispatch")
            )
        ).one()
        assert employee.full_name == "Mara Santos" and employee.phone is None
        for table, rows in data.items():
            assert connection.scalar(select(func.count()).select_from(table)) == len(rows)
        assert connection.scalar(select(func.count()).select_from(AuditLogRow)) == 1


def test_renew_refuses_real_sign_in_links_without_changing_the_data(session_factory):
    engine = session_factory.kw["bind"]
    data = build_dataset()
    with engine.begin() as connection:
        seed_recent(connection, data)
        connection.execute(
            EmployeeRow.__table__.update()
            .where(EmployeeRow.employee_id == seed_id("dispatch"))
            .values(clerk_user_id="user_existing_real_account", full_name="Keep this person")
        )
    with pytest.raises(ValueError, match="real sign-in"), engine.begin() as connection:
        seed_recent(connection, data, renew=True)
    with engine.connect() as connection:
        assert (
            connection.scalar(
                select(EmployeeRow.full_name).where(EmployeeRow.employee_id == seed_id("dispatch"))
            )
            == "Keep this person"
        )


def test_renew_external_references_roll_back_deletes_and_preserve_real_records(session_factory):
    from backend.src.Repository.orm_models import DeliveryOrderRow

    engine = session_factory.kw["bind"]
    data = build_dataset()
    extra_order = {**data[DeliveryOrderRow.__table__][0], "order_id": seed_id("unrelated-real-order")}
    with engine.begin() as connection:
        seed_recent(connection, data)
        connection.execute(DeliveryOrderRow.__table__.insert().values(extra_order))
    with pytest.raises(IntegrityError), engine.begin() as connection:
        seed_recent(connection, data, renew=True)
    with engine.connect() as connection:
        for table, rows in data.items():
            extra = 1 if table is DeliveryOrderRow.__table__ else 0
            assert connection.scalar(select(func.count()).select_from(table)) == len(rows) + extra


def test_bulk_budget_reruns_and_next_day_do_not_grow_or_touch_existing_data(session_factory):
    engine = session_factory.kw["bind"]
    now = datetime(2026, 11, 19, 12, tzinfo=MANILA_OFFSET)
    data = build_dataset(now)
    unrelated_id = seed_id("unrelated-existing-client")
    with engine.begin() as connection:
        connection.execute(
            ClientRow.__table__.insert().values(client_id=unrelated_id, name="Existing client")
        )
    statements = []

    def record(_conn, _cursor, statement, _parameters, _context, _executemany):
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", record)
    try:
        with engine.begin() as connection:
            counts = seed_recent(connection, data)
        assert sum(counts.values()) == 94
        assert len(statements) == 12
        assert sum(statement.lstrip().upper().startswith("INSERT") for statement in statements) == 11
        assert not any(statement.lstrip().upper().startswith("SELECT") for statement in statements)
    finally:
        event.remove(engine, "before_cursor_execute", record)
    for clock in (now, now + timedelta(days=1), now + timedelta(days=45)):
        with engine.begin() as connection:
            seed_recent(connection, build_dataset(clock))
            for table, count in counts.items():
                model_table = next(item for item in data if item.name == table)
                expected = count + (1 if table == "clients" else 0)
                assert connection.scalar(select(func.count()).select_from(model_table)) == expected
            assert (
                connection.scalar(select(ClientRow.name).where(ClientRow.client_id == unrelated_id))
                == "Existing client"
            )
            assert connection.scalar(select(AuditLogRow.audit_id)) == seed_id("audit")
            assert connection.scalar(select(EmployeeRow.clerk_user_id).limit(1)) is None
    with engine.connect() as connection:
        # Existing repository mapping still accepts the rows; all trip crews are complete.
        from backend.src.Repository.trip_repository import TripRepository

        with session_factory(bind=connection) as session:
            trips = TripRepository(session).list_page(100, 0, None, None, None)
            assert len(trips) == 6 and all(len(trip.helper_ids) == 1 for trip in trips)


def test_late_conflict_rolls_back_earlier_batches(session_factory):
    engine = session_factory.kw["bind"]
    data = build_dataset(datetime(2026, 11, 19, 12, tzinfo=MANILA_OFFSET))
    # Fail late, after parents and trips were written; constraints must undo all of it.
    data[ExpenseSheetRow.__table__][-1]["total"] = Decimal("-1")
    with pytest.raises(IntegrityError), engine.begin() as connection:
        seed_recent(connection, data)
    with engine.connect() as connection:
        for table in data:
            assert connection.scalar(select(func.count()).select_from(table)) == 0
        assert connection.scalar(select(FinanceLockRow.version)) == 0


@pytest.mark.parametrize(
    ("url", "host", "valid"),
    [
        ("sqlite:///:memory:", None, True),
        ("postgresql+psycopg2://user:pass@localhost/demo", "localhost", True),
        ("postgresql+psycopg2://user:pass@db.example/demo?sslmode=require", "db.example", True),
        ("postgresql+psycopg2://user:pass@db.example/demo?sslmode=verify-full", "db.example", True),
        ("postgresql+psycopg2://user:pass@db.example/demo", "db.example", False),
        ("postgresql+psycopg2://user:pass@db.example/demo?sslmode=require", "other.example", False),
        ("postgresql+psycopg2://user:pass@db.example/demo?sslmode=require", None, False),
        ("postgresql+asyncpg://user:pass@localhost/demo", "localhost", False),
        ("mysql://user:pass@localhost/demo", "localhost", False),
    ],
)
def test_hosted_target_requires_exact_host_and_tls(url, host, valid):
    if valid:
        validate_target(make_url(url), host)
    else:
        with pytest.raises(ValueError):
            validate_target(make_url(url), host)
