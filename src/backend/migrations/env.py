# ===== AI GENERATED: alembic_env =====
# Purpose: Alembic runtime configuration
# Inputs: DATABASE_URL (settings) or an injected sqlalchemy.url
# Returns: online / offline migration runner
# Flow:
# 1. Resolve the URL (injected value wins, e.g. in tests)
# 2. Load ORM metadata for autogenerate comparison
# 3. Run migrations inside one transaction

from logging.config import fileConfig

from alembic import context
from backend.src.config import get_settings
from backend.src.database import Base
from backend.src.Repository import finance_models, orm_models  # noqa: F401  (register tables)
from sqlalchemy import create_engine

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def resolve_database_url() -> str:
    """Prefer an explicitly injected URL, otherwise the application settings."""
    return config.get_main_option("sqlalchemy.url") or get_settings().database_url


def run_migrations_offline() -> None:
    context.configure(
        url=resolve_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(resolve_database_url())
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
