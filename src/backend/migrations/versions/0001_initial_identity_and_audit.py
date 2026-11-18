"""Sprint 1: roles, employees, permission matrix, audit log, webhook ledger.

Revision ID: 0001
Revises:
"""

import json
from pathlib import Path

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

_MATRIX_PATH = Path(__file__).resolve().parents[2] / "src" / "Data" / "permission_matrix.json"
_TABLES = (
    "roles",
    "employees",
    "employee_roles",
    "role_permissions",
    "audit_log",
    "processed_webhook_events",
)


def _timestamp_column(name: str) -> sa.Column:
    return sa.Column(name, sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now())


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("code", sa.String(32), primary_key=True),
        sa.Column("name", sa.String(64), nullable=False),
    )
    op.create_table(
        "employees",
        sa.Column("employee_id", sa.Uuid(), primary_key=True),
        sa.Column("full_name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("clerk_user_id", sa.String(64), nullable=True, unique=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        _timestamp_column("created_at"),
    )
    op.create_index("uq_employees_email_lower", "employees", [sa.text("lower(email)")], unique=True)
    op.create_table(
        "employee_roles",
        sa.Column("employee_id", sa.Uuid(), sa.ForeignKey("employees.employee_id"), primary_key=True),
        sa.Column("role_code", sa.String(32), sa.ForeignKey("roles.code"), primary_key=True),
        sa.Column("assigned_by", sa.Uuid(), sa.ForeignKey("employees.employee_id"), nullable=True),
        _timestamp_column("assigned_at"),
        sa.Column("exception_reason", sa.Text(), nullable=True),
    )
    op.create_table(
        "role_permissions",
        sa.Column("capability", sa.String(64), primary_key=True),
        sa.Column("role_code", sa.String(32), sa.ForeignKey("roles.code"), primary_key=True),
        sa.Column("access_level", sa.String(8), nullable=False),
        sa.Column("conditional_setting", sa.String(64), nullable=True),
    )
    op.create_table(
        "audit_log",
        sa.Column("audit_id", sa.Uuid(), primary_key=True),
        _timestamp_column("occurred_at"),
        sa.Column("actor_employee_id", sa.Uuid(), sa.ForeignKey("employees.employee_id"), nullable=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(64), nullable=True),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("trace_id", sa.String(64), nullable=True),
    )
    op.create_table(
        "processed_webhook_events",
        sa.Column("event_id", sa.String(128), primary_key=True),
        sa.Column("event_type", sa.String(64), nullable=False),
        _timestamp_column("processed_at"),
    )

    _seed_permission_matrix()
    _make_audit_log_append_only()
    _lock_down_data_api()


def _seed_permission_matrix() -> None:
    matrix = json.loads(_MATRIX_PATH.read_text(encoding="utf-8"))
    roles_table = sa.table("roles", sa.column("code"), sa.column("name"))
    op.bulk_insert(roles_table, matrix["roles"])
    permissions_table = sa.table(
        "role_permissions",
        sa.column("capability"),
        sa.column("role_code"),
        sa.column("access_level"),
        sa.column("conditional_setting"),
    )
    grant_rows = [
        {
            "capability": entry["capability"],
            "role_code": role_code,
            "access_level": access_level,
            "conditional_setting": entry.get("conditional", {}).get(role_code),
        }
        for entry in matrix["capabilities"]
        for role_code, access_level in entry["grants"].items()
    ]
    op.bulk_insert(permissions_table, grant_rows)


def _make_audit_log_append_only() -> None:
    dialect = op.get_bind().dialect.name
    if dialect == "postgresql":
        op.execute("""
            CREATE FUNCTION audit_log_block_mutation() RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'audit_log is append-only';
            END;
            $$ LANGUAGE plpgsql
            """)
        op.execute(
            "CREATE TRIGGER audit_log_no_update_delete BEFORE UPDATE OR DELETE ON audit_log "
            "FOR EACH ROW EXECUTE FUNCTION audit_log_block_mutation()"
        )
        op.execute(
            "CREATE TRIGGER audit_log_no_truncate BEFORE TRUNCATE ON audit_log "
            "FOR EACH STATEMENT EXECUTE FUNCTION audit_log_block_mutation()"
        )
    elif dialect == "sqlite":
        for event in ("UPDATE", "DELETE"):
            op.execute(
                f"CREATE TRIGGER audit_log_no_{event.lower()} BEFORE {event} ON audit_log "
                "BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END"
            )


_LOCKED_DOWN_TABLES = (*_TABLES, "alembic_version")


def _lock_down_data_api() -> None:
    """Row Level Security on every table; no grants for Supabase anon/authenticated."""
    if op.get_bind().dialect.name != "postgresql":
        return
    for table_name in _LOCKED_DOWN_TABLES:
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
    dialect = op.get_bind().dialect.name
    if dialect == "postgresql":
        op.execute("DROP TRIGGER IF EXISTS audit_log_no_truncate ON audit_log")
        op.execute("DROP TRIGGER IF EXISTS audit_log_no_update_delete ON audit_log")
        op.execute("DROP FUNCTION IF EXISTS audit_log_block_mutation()")
    elif dialect == "sqlite":
        op.execute("DROP TRIGGER IF EXISTS audit_log_no_update")
        op.execute("DROP TRIGGER IF EXISTS audit_log_no_delete")
    for table_name in reversed(_TABLES):
        op.drop_table(table_name)
