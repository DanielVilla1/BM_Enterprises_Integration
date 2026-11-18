"""Sprint 3: trips, crew history, truck replacements, assignment-view capability.

Revision ID: 0003
Revises: 0002

Matrix additions ship as an idempotent migration: databases created before this
revision get the new rows here; fresh databases already received them from the
seed JSON in revision 0001, so existing rows are skipped.
"""

import json
from pathlib import Path

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

_MATRIX_PATH = Path(__file__).resolve().parents[2] / "src" / "Data" / "permission_matrix.json"
_NEW_CAPABILITIES = ("trip.assignment_view",)
_TABLES = ("trips", "trip_crew", "truck_replacements")


def _timestamp(name: str, nullable: bool = False) -> sa.Column:
    if nullable:
        return sa.Column(name, sa.DateTime(timezone=True), nullable=True)
    return sa.Column(name, sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())


def upgrade() -> None:
    op.create_table(
        "trips",
        sa.Column("trip_id", sa.Uuid(), primary_key=True),
        sa.Column("order_id", sa.Uuid(), sa.ForeignKey("delivery_orders.order_id"), nullable=False),
        sa.Column("truck_id", sa.Uuid(), sa.ForeignKey("trucks.truck_id"), nullable=False),
        sa.Column("load_tons", sa.Numeric(12, 3), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        _timestamp("accepted_at", nullable=True),
        _timestamp("cleared_at", nullable=True),
        _timestamp("departed_at", nullable=True),
        _timestamp("delivered_at", nullable=True),
        sa.Column("closed_reason", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("employees.employee_id"), nullable=True),
        _timestamp("created_at"),
        sa.CheckConstraint("load_tons > 0", name="ck_trips_load_positive"),
        sa.CheckConstraint(
            "status IN ('SCHEDULED', 'ACCEPTED', 'CLEARED_FOR_DISPATCH', 'IN_TRANSIT', "
            "'DELIVERED_OR_PENDING', 'OR_UPLOADED', 'COMPLETED', 'FAILED', 'CANCELLED')",
            name="ck_trips_status",
        ),
    )
    op.create_index("ix_trips_order", "trips", ["order_id"])
    op.create_index("ix_trips_truck_status", "trips", ["truck_id", "status"])
    op.create_index("ix_trips_status", "trips", ["status"])
    op.create_table(
        "trip_crew",
        sa.Column("crew_entry_id", sa.Uuid(), primary_key=True),
        sa.Column("trip_id", sa.Uuid(), sa.ForeignKey("trips.trip_id"), nullable=False),
        sa.Column("employee_id", sa.Uuid(), sa.ForeignKey("employees.employee_id"), nullable=False),
        sa.Column("crew_role", sa.String(8), nullable=False),
        _timestamp("assigned_at"),
        _timestamp("removed_at", nullable=True),
        sa.CheckConstraint("crew_role IN ('DRIVER', 'HELPER')", name="ck_trip_crew_role"),
    )
    op.create_index("ix_trip_crew_employee", "trip_crew", ["employee_id"])
    op.create_index("ix_trip_crew_trip", "trip_crew", ["trip_id"])
    active_driver = sa.text("crew_role = 'DRIVER' AND removed_at IS NULL")
    op.create_index(
        "uq_trip_crew_one_active_driver",
        "trip_crew",
        ["trip_id"],
        unique=True,
        postgresql_where=active_driver,
        sqlite_where=active_driver,
    )
    active_member = sa.text("removed_at IS NULL")
    op.create_index(
        "uq_trip_crew_active_member",
        "trip_crew",
        ["trip_id", "employee_id"],
        unique=True,
        postgresql_where=active_member,
        sqlite_where=active_member,
    )
    op.create_table(
        "truck_replacements",
        sa.Column("replacement_id", sa.Uuid(), primary_key=True),
        sa.Column("trip_id", sa.Uuid(), sa.ForeignKey("trips.trip_id"), nullable=False),
        sa.Column("original_truck_id", sa.Uuid(), sa.ForeignKey("trucks.truck_id"), nullable=False),
        sa.Column("replacement_truck_id", sa.Uuid(), sa.ForeignKey("trucks.truck_id"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        _timestamp("effective_at"),
        sa.Column("replaced_by", sa.Uuid(), sa.ForeignKey("employees.employee_id"), nullable=True),
    )
    _add_missing_capabilities()
    _lock_down_data_api()


def _add_missing_capabilities() -> None:
    matrix = json.loads(_MATRIX_PATH.read_text(encoding="utf-8"))
    permissions_table = sa.table(
        "role_permissions",
        sa.column("capability"),
        sa.column("role_code"),
        sa.column("access_level"),
        sa.column("conditional_setting"),
    )
    connection = op.get_bind()
    existing = {
        (row.capability, row.role_code)
        for row in connection.execute(
            sa.select(permissions_table.c.capability, permissions_table.c.role_code)
        )
    }
    missing_rows = [
        {
            "capability": entry["capability"],
            "role_code": role_code,
            "access_level": access_level,
            "conditional_setting": entry.get("conditional", {}).get(role_code),
        }
        for entry in matrix["capabilities"]
        if entry["capability"] in _NEW_CAPABILITIES
        for role_code, access_level in entry["grants"].items()
        if (entry["capability"], role_code) not in existing
    ]
    if missing_rows:
        op.bulk_insert(permissions_table, missing_rows)


def _lock_down_data_api() -> None:
    """Row Level Security on every new table; no grants for Supabase anon/authenticated."""
    if op.get_bind().dialect.name != "postgresql":
        return
    for table_name in _TABLES:
        op.execute(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY")
        op.execute(f"""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    EXECUTE 'REVOKE ALL ON TABLE {table_name} FROM anon';
                END IF;
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    EXECUTE 'REVOKE ALL ON TABLE {table_name} FROM authenticated';
                END IF;
            END
            $$
            """)


def downgrade() -> None:
    op.execute("DELETE FROM role_permissions WHERE capability = 'trip.assignment_view'")
    for table_name in reversed(_TABLES):
        op.drop_table(table_name)
