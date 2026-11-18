"""Exercise the real Alembic loader so missing migration dependencies fail in tests."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text


def test_financial_migration_upgrade_downgrade_and_upgrade(tmp_path: Path) -> None:
    """Finance DDL and historical seed survive a reversible migration cycle."""
    backend_root = Path(__file__).resolve().parents[1]
    database_url = f"sqlite:///{(tmp_path / 'financial-migration.db').as_posix()}"
    configuration = Config(str(backend_root / "alembic.ini"))
    configuration.set_main_option("sqlalchemy.url", database_url)
    engine = create_engine(database_url)
    try:
        command.upgrade(configuration, "0005")
        with engine.connect() as connection:
            assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar() == "0005"
            assert (
                connection.execute(text("SELECT version FROM finance_lock WHERE record_id=1")).scalar() == 0
            )
            assert connection.execute(
                text("SELECT driver_one,helper_one,driver_two,helper_two FROM earning_rates")
            ).one() == (8, 4, 6, 3)

        command.downgrade(configuration, "0004")
        remaining_tables = inspect(engine).get_table_names()
        assert "employees" in remaining_tables
        assert "trips" in remaining_tables
        assert "finance_lock" not in remaining_tables
        assert "earning_rates" not in remaining_tables

        command.upgrade(configuration, "0005")
        with engine.connect() as connection:
            assert connection.execute(text("SELECT count(*) FROM earning_rates")).scalar() == 1
    finally:
        engine.dispose()
