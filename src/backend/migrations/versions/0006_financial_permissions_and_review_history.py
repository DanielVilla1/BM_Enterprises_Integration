"""Repair existing Sprint 5 databases and retain every expense contributor.

Revision ID: 0006
Revises: 0005
"""

# ===== AI GENERATED: financial_access_upgrade =====
# Purpose: Apply new read grants to databases already at 0005, without widening business writes.
# Inputs: Existing permission matrix and expense records.
# Returns: Forward-compatible financial grants and contributor history.
# Flow: Add read capabilities; insert missing grants; preserve existing approvals and business records.

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None

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
    bind = op.get_bind()
    op.add_column("expense_sheets", sa.Column("contributors", sa.JSON(), nullable=False, server_default="[]"))
    sheets = sa.table(
        "expense_sheets",
        sa.column("record_id", sa.Uuid),
        sa.column("entered_by", sa.Uuid),
        sa.column("contributors", sa.JSON),
    )
    for record_id, entered_by in bind.execute(sa.select(sheets.c.record_id, sheets.c.entered_by)):
        bind.execute(
            sheets.update().where(sheets.c.record_id == record_id).values(contributors=[str(entered_by)])
        )
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


def downgrade() -> None:
    permissions = sa.table("role_permissions", sa.column("capability", sa.String))
    op.get_bind().execute(permissions.delete().where(permissions.c.capability.in_(list(_GRANTS))))
    op.drop_column("expense_sheets", "contributors")
