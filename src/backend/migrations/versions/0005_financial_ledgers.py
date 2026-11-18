"""Sprint 5: exact financial ledgers, private tables and historical rate seed.

Revision ID: 0005
Revises: 0004
"""

# ===== AI GENERATED: financial_migration =====
# Purpose: Create finance tables, seed the original rate and secure the Data API.
# Inputs: Alembic bind at revision 0004.
# Returns: Reversible schema migration; no operational data is rewritten.
# Flow: Define a migration-owned schema snapshot; create and lock down each table.

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

# Frozen additions apply to databases already migrated through Sprint 4 too.
_GRANTS = {
    "expense.view": {"OWNER": "FULL", "DISPATCHER": "FULL", "DRIVER": "OWN", "ACCOUNTING": "FULL"},
    "payroll.view": {"OWNER": "FULL", "HR_PAYROLL": "FULL", "DRIVER": "OWN", "HELPER": "OWN"},
    "payroll.prepare": {"HR_PAYROLL": "FULL"},
    "payroll.reverse": {"OWNER": "FULL"},
    "earnings.calculate": {"OWNER": "FULL", "HR_PAYROLL": "FULL"},
    "cash_advance.view": {"OWNER": "FULL", "HR_PAYROLL": "FULL", "DRIVER": "OWN", "HELPER": "OWN"},
    "cash_advance.approval_action": {"OWNER": "FULL", "HR_PAYROLL": "FULL"},
    "cash_advance.delegated_approve": {"HR_PAYROLL": "FULL"},
}


def upgrade() -> None:
    # AI GENERATED: The migrations package owns this immutable schema snapshot.
    from backend.migrations.financial_schema_0005 import finance_metadata

    bind = op.get_bind()
    permissions = sa.table(
        "role_permissions",
        sa.column("capability", sa.String),
        sa.column("role_code", sa.String),
        sa.column("access_level", sa.String),
    )
    for capability, grants in _GRANTS.items():
        for role_code, access_level in grants.items():
            existing = bind.execute(
                sa.select(permissions.c.capability).where(
                    permissions.c.capability == capability, permissions.c.role_code == role_code
                )
            ).first()
            if existing is None:
                bind.execute(
                    permissions.insert().values(
                        capability=capability, role_code=role_code, access_level=access_level
                    )
                )
    metadata = finance_metadata()
    for table in metadata.sorted_tables:
        if table.info.get("financial"):
            table.create(bind)
    bind.execute(metadata.tables["finance_lock"].insert().values(record_id=1, version=0))
    bind.execute(
        metadata.tables["earning_rates"]
        .insert()
        .values(
            record_id=UUID("00000000-0000-0000-0000-000000000005"),
            created_at=datetime.now(UTC),
            effective_on=date(1970, 1, 1),
            driver_one=Decimal("8"),
            helper_one=Decimal("4"),
            driver_two=Decimal("6"),
            helper_two=Decimal("3"),
            reference="Initial D6 policy",
            entered_by=None,
        )
    )
    if bind.dialect.name == "postgresql":
        for table in metadata.sorted_tables:
            if not table.info.get("financial"):
                continue
            table_name = table.name
            op.execute(sa.text(f'ALTER TABLE "{table_name}" ENABLE ROW LEVEL SECURITY'))
            op.execute(sa.text(f"""DO $$ BEGIN
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    REVOKE ALL ON TABLE "{table_name}" FROM anon;
                END IF;
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    REVOKE ALL ON TABLE "{table_name}" FROM authenticated;
                END IF;
            END $$"""))


def downgrade() -> None:
    from backend.migrations.financial_schema_0005 import finance_metadata

    permissions = sa.table("role_permissions", sa.column("capability", sa.String))
    op.get_bind().execute(permissions.delete().where(permissions.c.capability.in_(list(_GRANTS))))

    for table in reversed(finance_metadata().sorted_tables):
        if table.info.get("financial"):
            table.drop(op.get_bind())
