"""Deployment preparation orders writes and gates automatic mock refresh."""

from types import SimpleNamespace

import pytest
from sqlalchemy import text

from backend.scripts import prepare_deploy


@pytest.fixture
def deployment(monkeypatch):
    calls = []
    monkeypatch.delenv("MOCK_DATA_AUTO_REFRESH", raising=False)
    monkeypatch.delenv("RENDER_GIT_BRANCH", raising=False)
    monkeypatch.setattr(
        prepare_deploy,
        "get_settings",
        lambda: SimpleNamespace(
            database_url="postgresql+psycopg2://demo:fake@db.example/demo?sslmode=require"
        ),
    )
    monkeypatch.setattr(prepare_deploy.command, "upgrade", lambda *_args: calls.append("migrate"))
    monkeypatch.setattr(prepare_deploy.seed_recent, "main", lambda args: calls.append(args))
    return calls


def test_default_only_migrates(deployment):
    prepare_deploy.main()
    assert deployment == ["migrate"]


def test_enabled_main_refresh_follows_migrations(deployment, monkeypatch):
    monkeypatch.setenv("MOCK_DATA_AUTO_REFRESH", "true")
    monkeypatch.setenv("RENDER_GIT_BRANCH", "main")
    prepare_deploy.main()
    assert deployment == ["migrate", ["--mock-data", "--confirm-host", "db.example"]]


@pytest.mark.parametrize("branch", [None, "preview", "feature/demo-seed"])
def test_enabled_refresh_rejects_other_branches_before_writes(deployment, monkeypatch, branch):
    monkeypatch.setenv("MOCK_DATA_AUTO_REFRESH", "true")
    if branch:
        monkeypatch.setenv("RENDER_GIT_BRANCH", branch)
    with pytest.raises(SystemExit, match="restricted"):
        prepare_deploy.main()
    assert deployment == []


@pytest.mark.parametrize(
    "url",
    ["not-a-url", "sqlite:///:memory:", "postgresql+psycopg2://demo:fake@db.example/demo"],
)
def test_enabled_refresh_validates_target_before_writes(deployment, monkeypatch, url):
    monkeypatch.setenv("MOCK_DATA_AUTO_REFRESH", "true")
    monkeypatch.setenv("RENDER_GIT_BRANCH", "main")
    monkeypatch.setattr(prepare_deploy, "get_settings", lambda: SimpleNamespace(database_url=url))
    with pytest.raises(SystemExit, match="valid PostgreSQL"):
        prepare_deploy.main()
    assert deployment == []


def test_migration_failure_stops_refresh_and_redacts_errors(deployment, monkeypatch):
    monkeypatch.setenv("MOCK_DATA_AUTO_REFRESH", "true")
    monkeypatch.setenv("RENDER_GIT_BRANCH", "main")

    def fail(*_args):
        raise RuntimeError("fake credential detail that must not reach build logs")

    monkeypatch.setattr(prepare_deploy.command, "upgrade", fail)
    with pytest.raises(SystemExit, match="migration failed") as error:
        prepare_deploy.main()
    assert "credential" not in str(error.value)
    assert deployment == []


def test_seed_failure_fails_build(deployment, monkeypatch):
    monkeypatch.setenv("MOCK_DATA_AUTO_REFRESH", "true")
    monkeypatch.setenv("RENDER_GIT_BRANCH", "main")

    def fail(_args):
        raise SystemExit("Mock seed failed")

    monkeypatch.setattr(prepare_deploy.seed_recent, "main", fail)
    with pytest.raises(SystemExit, match="Mock seed failed"):
        prepare_deploy.main()
    assert deployment == ["migrate"]


def test_invalid_opt_in_is_rejected_before_writes(deployment, monkeypatch):
    monkeypatch.setenv("MOCK_DATA_AUTO_REFRESH", "yes")
    with pytest.raises(SystemExit, match="true or false"):
        prepare_deploy.main()
    assert deployment == []


def test_real_migrations_are_independent_of_working_directory(tmp_path, monkeypatch):
    database_url = f"sqlite:///{(tmp_path / 'deployment.db').as_posix()}"
    monkeypatch.delenv("MOCK_DATA_AUTO_REFRESH", raising=False)
    monkeypatch.setenv("DATABASE_URL", database_url)
    prepare_deploy.get_settings.cache_clear()
    monkeypatch.chdir(tmp_path)
    try:
        prepare_deploy.main()
        from sqlalchemy import create_engine

        engine = create_engine(database_url)
        try:
            with engine.connect() as connection:
                assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "0006"
                assert connection.scalar(text("SELECT COUNT(*) FROM employees")) == 0
        finally:
            engine.dispose()
    finally:
        prepare_deploy.get_settings.cache_clear()
