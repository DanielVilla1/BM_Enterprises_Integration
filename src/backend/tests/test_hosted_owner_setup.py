"""The hosted operator helper must reject unintended destinations before connecting."""

import runpy
from pathlib import Path

import pytest
from sqlalchemy.engine import make_url

HELPER = Path(__file__).resolve().parents[3] / "tools" / "scripts" / "bootstrap_hosted_owner.py"
normalize_database_url = runpy.run_path(str(HELPER))["normalize_database_url"]


def test_hosted_owner_url_keeps_encoded_password_and_requires_tls() -> None:
    normalized = normalize_database_url(
        "postgresql://postgres.demo:example%40value@aws-1-region.pooler.supabase.com:5432/postgres"
    )
    address = make_url(normalized)
    assert address.password == "example@value"
    assert address.host == "aws-1-region.pooler.supabase.com"
    assert address.drivername == "postgresql+psycopg2"
    assert address.query["sslmode"] == "require"
    assert address.query["connect_timeout"] == "15"


@pytest.mark.parametrize(
    "raw_value",
    [
        "sqlite:///local.db",
        "postgresql://postgres:example@localhost:5432/postgres",
        "postgresql://postgres:example@external.invalid/postgres",
        "postgresql://postgres:example@value@aws-1-region.pooler.supabase.com:5432/postgres",
        "postgresql://postgres:example@value%40aws-1-region.pooler.supabase.com:5432/postgres",
        "postgresql://postgres:example@aws-1-region.pooler.supabase.com:invalid/postgres",
        "postgresql://postgres@aws-1-region.pooler.supabase.com:5432/postgres",
        "postgresql://postgres:example@aws-1-region.pooler.supabase.com:5432/other",
        "postgresql://postgres:example@aws-1-region.pooler.supabase.com/postgres?sslmode=disable",
    ],
)
def test_hosted_owner_url_rejects_unsafe_or_malformed_destinations_without_echoing_input(
    raw_value: str,
) -> None:
    with pytest.raises(ValueError) as failure:
        normalize_database_url(raw_value)
    assert "example" not in str(failure.value)
    assert raw_value not in str(failure.value)
