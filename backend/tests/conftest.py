# ===== AI GENERATED: test_fixtures =====
# Purpose: Shared pytest fixtures (migrated DB, signed tokens, signed webhooks)
# Inputs: none (fake keys and fake data only)
# Returns: client, session factory, token and webhook helpers
# Flow:
# 1. Migrate a template SQLite DB once via Alembic, copy it per test
# 2. Override DB session and verifiers with test-key versions
# 3. Provide helpers to create employees and mint tokens

import base64
import os
import shutil
import time
import uuid
from collections.abc import Callable, Iterator
from pathlib import Path

import jwt
import pytest
from alembic import command
from alembic.config import Config
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker
from svix.webhooks import Webhook

TEST_ISSUER = "https://clerk.test.example"
TEST_PARTY = "http://localhost:5173"
TEST_WEBHOOK_SECRET = "whsec_" + base64.b64encode(b"unit-test-signing-secret-0123456").decode()

os.environ.update(
    {
        "DATABASE_URL": "sqlite:///./unused-import-time.db",
        "CLERK_ISSUER": TEST_ISSUER,
        "CLERK_AUTHORIZED_PARTIES": TEST_PARTY,
        "CLERK_WEBHOOK_SECRET": TEST_WEBHOOK_SECRET,
        "ENABLE_API_DOCS": "true",
    }
)

from backend.main import app  # noqa: E402
from backend.src.database import build_engine  # noqa: E402
from backend.src.Entity.access import RoleCode  # noqa: E402
from backend.src.Entity.employee import Employee  # noqa: E402
from backend.src.Infrastructure.Clerk.clerk_token_verifier import ClerkTokenVerifier  # noqa: E402
from backend.src.Infrastructure.Clerk.clerk_webhook_verifier import ClerkWebhookVerifier  # noqa: E402
from backend.src.providers import get_session, get_token_verifier, get_webhook_verifier  # noqa: E402
from backend.src.Repository.employee_repository import EmployeeRepository  # noqa: E402

BACKEND_DIRECTORY = Path(__file__).resolve().parents[1]


def _generate_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


SIGNING_KEY = _generate_key()
OTHER_KEY = _generate_key()


def build_test_verifier() -> ClerkTokenVerifier:
    return ClerkTokenVerifier(
        issuer=TEST_ISSUER,
        jwks_url="",
        audience="",
        authorized_parties=(TEST_PARTY,),
        clock_skew_seconds=5,
        key_resolver=lambda _token: SIGNING_KEY.public_key(),
    )


def mint_token(
    subject: str,
    issuer: str = TEST_ISSUER,
    authorized_party: str = TEST_PARTY,
    lifetime_seconds: int = 60,
    key: rsa.RSAPrivateKey | None = None,
) -> str:
    now = int(time.time())
    claims = {
        "sub": subject,
        "iss": issuer,
        "azp": authorized_party,
        "iat": now,
        "exp": now + lifetime_seconds,
    }
    return jwt.encode(claims, key or SIGNING_KEY, algorithm="RS256")


@pytest.fixture(scope="session")
def template_database(tmp_path_factory: pytest.TempPathFactory) -> Path:
    database_path = tmp_path_factory.mktemp("template") / "template.db"
    configuration = Config(str(BACKEND_DIRECTORY / "alembic.ini"))
    configuration.set_main_option("sqlalchemy.url", f"sqlite:///{database_path.as_posix()}")
    command.upgrade(configuration, "head")
    return database_path


@pytest.fixture
def session_factory(template_database: Path, tmp_path: Path) -> Iterator[sessionmaker[Session]]:
    database_path = tmp_path / "test.db"
    shutil.copy(template_database, database_path)
    engine = build_engine(f"sqlite:///{database_path.as_posix()}")
    yield sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    engine.dispose()


@pytest.fixture
def client(session_factory: sessionmaker[Session]) -> Iterator[TestClient]:
    def override_session() -> Iterator[Session]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_token_verifier] = build_test_verifier
    app.dependency_overrides[get_webhook_verifier] = lambda: ClerkWebhookVerifier(TEST_WEBHOOK_SECRET)
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class EmployeeFactory:
    """Creates fake employees directly through the repository."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create(
        self,
        roles: tuple[RoleCode, ...],
        active: bool = True,
        email: str | None = None,
        linked: bool = True,
        name: str = "Fake Person",
    ) -> Employee:
        with self._session_factory() as session:
            repository = EmployeeRepository(session)
            unique = uuid.uuid4().hex[:10]
            employee = repository.create(name, email or f"{unique}@bm-test.example", None)
            if linked:
                repository.set_clerk_user_id(employee.employee_id, f"user_{unique}")
            repository.replace_roles(employee.employee_id, set(roles), None, None)
            repository.set_active(employee.employee_id, active)
            session.commit()
            stored = repository.get_by_id(employee.employee_id)
        assert stored is not None
        return stored


@pytest.fixture
def employees(session_factory: sessionmaker[Session]) -> EmployeeFactory:
    return EmployeeFactory(session_factory)


def auth_headers(employee: Employee) -> dict[str, str]:
    assert employee.clerk_user_id is not None
    return {"Authorization": f"Bearer {mint_token(employee.clerk_user_id)}"}


@pytest.fixture
def headers_for() -> Callable[[Employee], dict[str, str]]:
    return auth_headers


def sign_webhook(payload: bytes, message_id: str, timestamp: int | None = None) -> dict[str, str]:
    issued_at = timestamp if timestamp is not None else int(time.time())
    from datetime import UTC, datetime

    signature = Webhook(TEST_WEBHOOK_SECRET).sign(
        message_id, datetime.fromtimestamp(issued_at, tz=UTC), payload.decode()
    )
    return {
        "svix-id": message_id,
        "svix-timestamp": str(issued_at),
        "svix-signature": signature,
        "content-type": "application/json",
    }
