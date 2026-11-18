"""Sprint 2: clients, trucks, maintenance, driver licenses, delivery orders.

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

_TABLES = (
    "clients",
    "trucks",
    "truck_maintenance_records",
    "driver_licenses",
    "delivery_orders",
)


def _timestamp(name: str, nullable: bool = False) -> sa.Column:
    if nullable:
        return sa.Column(name, sa.DateTime(timezone=True), nullable=True)
    return sa.Column(name, sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("client_id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("address", sa.String(300), nullable=True),
        sa.Column("contact_person", sa.String(120), nullable=True),
        sa.Column("contact_phone", sa.String(32), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        _timestamp("created_at"),
    )
    op.create_index("uq_clients_name_lower", "clients", [sa.text("lower(name)")], unique=True)
    op.create_table(
        "trucks",
        sa.Column("truck_id", sa.Uuid(), primary_key=True),
        sa.Column("plate_number", sa.String(16), nullable=False, unique=True),
        sa.Column("description", sa.String(120), nullable=True),
        sa.Column("capacity_tons", sa.Numeric(10, 3), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        _timestamp("created_at"),
        sa.CheckConstraint("capacity_tons > 0", name="ck_trucks_capacity_positive"),
        sa.CheckConstraint(
            "status IN ('AVAILABLE', 'ASSIGNED', 'IN_TRANSIT', 'MAINTENANCE')", name="ck_trucks_status"
        ),
    )
    op.create_table(
        "truck_maintenance_records",
        sa.Column("record_id", sa.Uuid(), primary_key=True),
        sa.Column("truck_id", sa.Uuid(), sa.ForeignKey("trucks.truck_id"), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        _timestamp("started_at"),
        _timestamp("ended_at", nullable=True),
        sa.Column("started_by", sa.Uuid(), sa.ForeignKey("employees.employee_id"), nullable=True),
    )
    op.create_table(
        "driver_licenses",
        sa.Column("employee_id", sa.Uuid(), sa.ForeignKey("employees.employee_id"), primary_key=True),
        sa.Column("license_number", sa.String(32), nullable=False, unique=True),
        sa.Column("expiry_date", sa.Date(), nullable=False),
        _timestamp("updated_at"),
    )
    op.create_table(
        "delivery_orders",
        sa.Column("order_id", sa.Uuid(), primary_key=True),
        sa.Column("client_id", sa.Uuid(), sa.ForeignKey("clients.client_id"), nullable=False),
        sa.Column("client_reference", sa.String(64), nullable=True),
        sa.Column("pickup_location", sa.String(300), nullable=False),
        sa.Column("delivery_location", sa.String(300), nullable=False),
        sa.Column("scheduled_date", sa.Date(), nullable=False),
        sa.Column("total_weight_tons", sa.Numeric(12, 3), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("employees.employee_id"), nullable=True),
        _timestamp("created_at"),
        sa.CheckConstraint("total_weight_tons > 0", name="ck_delivery_orders_weight_positive"),
        sa.CheckConstraint(
            "status IN ('PENDING', 'PARTIALLY_ASSIGNED', 'SCHEDULED', 'IN_PROGRESS', "
            "'COMPLETED', 'CANCELLED')",
            name="ck_delivery_orders_status",
        ),
    )
    op.create_index("ix_delivery_orders_status_date", "delivery_orders", ["status", "scheduled_date"])
    _lock_down_data_api()


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
    for table_name in reversed(_TABLES):
        op.drop_table(table_name)
