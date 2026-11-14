# ===== AI GENERATED: database_setup =====
# Purpose: Build the SQLAlchemy engine, session factory and declarative base
# Inputs: DATABASE_URL from application settings
# Returns: engine factory, SessionLocal, Base
# Flow:
# 1. Create engine (SQLite gets thread + foreign key settings)
# 2. Expose a sessionmaker with explicit commit control
# 3. Export Base for ORM table declarations

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    """Declarative base shared by every ORM table."""


def build_engine(database_url: str) -> Engine:
    """Create an engine; SQLite enforces foreign keys for parity with PostgreSQL."""
    if database_url.startswith("sqlite"):
        sqlite_engine = create_engine(database_url, connect_args={"check_same_thread": False})

        @event.listens_for(sqlite_engine, "connect")
        def enable_foreign_keys(dbapi_connection: object, _record: object) -> None:
            cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return sqlite_engine
    return create_engine(database_url, pool_pre_ping=True)


engine: Engine = build_engine(get_settings().database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
