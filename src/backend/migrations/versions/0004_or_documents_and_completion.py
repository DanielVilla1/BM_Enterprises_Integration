"""Sprint 4: OR documents, receipt confirmation fields, idempotency keys.

Revision ID: 0004
Revises: 0003
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

_TABLES = ("or_documents", "idempotency_keys")
_TRIP_COLUMNS = (
    "or_uploaded_at",
    "or_uploaded_by",
    "receipt_confirmed_at",
    "receipt_confirmed_by",
    "receipt_received_at",
)


def _timestamp(name: str, nullable: bool = False) -> sa.Column:
    if nullable:
        return sa.Column(name, sa.DateTime(timezone=True), nullable=True)
    return sa.Column(name, sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())


def upgrade() -> None:
    trip_checks = (
        sa.CheckConstraint("load_tons > 0", name="ck_trips_load_positive"),
        sa.CheckConstraint(
            "status IN ('SCHEDULED', 'ACCEPTED', 'CLEARED_FOR_DISPATCH', 'IN_TRANSIT', "
            "'DELIVERED_OR_PENDING', 'OR_UPLOADED', 'COMPLETED', 'FAILED', 'CANCELLED')",
            name="ck_trips_status",
        ),
    )
    with op.batch_alter_table("trips", table_args=trip_checks) as batch:
        batch.add_column(_timestamp("or_uploaded_at", nullable=True))
        batch.add_column(sa.Column("or_uploaded_by", sa.Uuid(), nullable=True))
        batch.add_column(_timestamp("receipt_confirmed_at", nullable=True))
        batch.add_column(sa.Column("receipt_confirmed_by", sa.Uuid(), nullable=True))
        batch.add_column(_timestamp("receipt_received_at", nullable=True))
        batch.create_foreign_key("fk_trips_or_uploaded_by", "employees", ["or_uploaded_by"], ["employee_id"])
        batch.create_foreign_key(
            "fk_trips_receipt_confirmed_by", "employees", ["receipt_confirmed_by"], ["employee_id"]
        )
    op.create_table(
        "or_documents",
        sa.Column("document_id", sa.Uuid(), primary_key=True),
        sa.Column("trip_id", sa.Uuid(), sa.ForeignKey("trips.trip_id"), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("storage_path", sa.String(200), nullable=False, unique=True),
        sa.Column("content_type", sa.String(32), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("uploaded_by", sa.Uuid(), sa.ForeignKey("employees.employee_id"), nullable=True),
        _timestamp("uploaded_at"),
        _timestamp("superseded_at", nullable=True),
        sa.CheckConstraint("kind IN ('SIGNED_OR', 'STAMPED_COPY')", name="ck_or_documents_kind"),
        sa.CheckConstraint("size_bytes > 0", name="ck_or_documents_size_positive"),
    )
    op.create_index("ix_or_documents_trip", "or_documents", ["trip_id"])
    op.create_table(
        "idempotency_keys",
        sa.Column("key", sa.String(128), primary_key=True),
        sa.Column("actor_id", sa.Uuid(), sa.ForeignKey("employees.employee_id"), primary_key=True),
        sa.Column("scope", sa.String(100), nullable=False),
        _timestamp("created_at"),
    )
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
    with op.batch_alter_table("trips") as batch:
        batch.drop_constraint("fk_trips_receipt_confirmed_by", type_="foreignkey")
        batch.drop_constraint("fk_trips_or_uploaded_by", type_="foreignkey")
        for column_name in reversed(_TRIP_COLUMNS):
            batch.drop_column(column_name)
