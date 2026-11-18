# ===== AI GENERATED: test_postgres_hardening =====
# Purpose: Prove the Data API lockdown and audit protection on real PostgreSQL
# Inputs: TEST_DATABASE_URL (skipped when unset)
# Returns: pass/fail
# Flow:
# 1. RLS is enabled on every table in the public schema
# 2. anon / authenticated hold no privileges (Supabase public key reach)
# 3. audit_log rejects UPDATE, DELETE and TRUNCATE

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.src.Repository.audit_repository import AuditRepository
from backend.tests.conftest import USING_POSTGRES

pytestmark = pytest.mark.skipif(not USING_POSTGRES, reason="needs TEST_DATABASE_URL (PostgreSQL)")

PUBLIC_TABLES_SQL = text(
    "SELECT c.relname, c.relrowsecurity FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
    "WHERE n.nspname = 'public' AND c.relkind = 'r' ORDER BY c.relname"
)


def test_row_level_security_is_enabled_on_every_public_table(session_factory) -> None:
    with session_factory() as session:
        rows = session.execute(PUBLIC_TABLES_SQL).all()
    assert rows, "no tables found"
    unprotected = [name for name, secured in rows if not secured]
    assert not unprotected, f"tables without RLS: {unprotected}"


@pytest.mark.parametrize("role_name", ["anon", "authenticated"])
def test_public_api_roles_have_no_table_privileges(session_factory, role_name: str) -> None:
    with session_factory() as session:
        table_names = [name for name, _ in session.execute(PUBLIC_TABLES_SQL).all()]
        leaks = [
            name
            for name in table_names
            if session.execute(
                text("SELECT has_table_privilege(:role, :table, 'SELECT,INSERT,UPDATE,DELETE')"),
                {"role": role_name, "table": f"public.{name}"},
            ).scalar()
        ]
    assert not leaks, f"{role_name} can still reach: {leaks}"


@pytest.mark.parametrize(
    "statement",
    ["UPDATE audit_log SET action = 'tampered'", "DELETE FROM audit_log", "TRUNCATE audit_log"],
)
def test_audit_log_is_append_only_on_postgres(session_factory, statement: str) -> None:
    with session_factory() as session:
        AuditRepository(session).append(None, "test.event", "thing", None, {}, None)
        session.commit()
    with session_factory() as session, pytest.raises(SQLAlchemyError):
        session.execute(text(statement))
        session.commit()
