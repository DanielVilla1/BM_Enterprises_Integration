# ===== AI GENERATED: test_reconciliation =====
# Purpose: Clerk <-> employee reconciliation rules and the Clerk directory client
# Inputs: fake directory, httpx mock transport, fake employees
# Returns: pass/fail
# Flow:
# 1. Missing Clerk users are deactivated; unlinked employees link by verified email
# 2. Unsafe input (empty list, mass deactivation, outage) changes nothing
# 3. Directory client paginates, retries 5xx, never returns partial data

import httpx
import pytest

from backend.src.Contract.i_identity_directory import DirectoryUser, IdentityDirectoryError
from backend.src.Entity.access import RoleCode
from backend.src.Entity.business_rule_error import BusinessRuleError
from backend.src.Infrastructure.Clerk.clerk_identity_directory import ClerkIdentityDirectory
from backend.src.Repository.audit_repository import AuditRepository
from backend.src.Repository.employee_repository import EmployeeRepository
from backend.src.Repository.unit_of_work import SqlAlchemyUnitOfWork
from backend.src.Service.reconciliation_service import ReconciliationService


class FakeDirectory:
    def __init__(self, users: list[DirectoryUser] | None = None, failure: bool = False) -> None:
        self._users = users or []
        self._failure = failure

    def list_users(self) -> list[DirectoryUser]:
        if self._failure:
            raise IdentityDirectoryError("down")
        return self._users


def _run(session_factory, directory):
    with session_factory() as session:
        service = ReconciliationService(
            directory,
            EmployeeRepository(session),
            AuditRepository(session),
            SqlAlchemyUnitOfWork(session),
        )
        return service.run()


def _employee(session_factory, employee_id):
    with session_factory() as session:
        return EmployeeRepository(session).get_by_id(employee_id)


def _audit_actions(session_factory) -> list[str]:
    with session_factory() as session:
        return [row.action for row in AuditRepository(session).list_page(100, 0)]


def test_employee_whose_clerk_user_vanished_is_deactivated(session_factory, employees) -> None:
    present = employees.create((RoleCode.DRIVER,))
    gone = employees.create((RoleCode.DRIVER,))
    directory = FakeDirectory([DirectoryUser(present.clerk_user_id, None)])
    report = _run(session_factory, directory)
    assert report.deactivated_count == 1
    assert _employee(session_factory, gone.employee_id).is_active is False
    assert _employee(session_factory, present.employee_id).is_active is True
    assert "employee.deactivated" in _audit_actions(session_factory)


def test_unlinked_employee_is_linked_by_verified_email_only(session_factory, employees) -> None:
    keeper = employees.create((RoleCode.OWNER,))
    waiting = employees.create((RoleCode.DRIVER,), linked=False, email="Waiting@bm-test.example")
    stranger = employees.create((RoleCode.DRIVER,), linked=False, email="stranger@bm-test.example")
    directory = FakeDirectory(
        [
            DirectoryUser(keeper.clerk_user_id, None),
            DirectoryUser("user_waiting1", "waiting@bm-test.example"),
            DirectoryUser("user_stranger", None),
        ]
    )
    report = _run(session_factory, directory)
    assert report.linked_count == 1
    assert _employee(session_factory, waiting.employee_id).clerk_user_id == "user_waiting1"
    assert _employee(session_factory, stranger.employee_id).clerk_user_id is None
    assert report.clerk_users_without_employee == 1


def test_second_run_changes_nothing(session_factory, employees) -> None:
    present = employees.create((RoleCode.DRIVER,))
    employees.create((RoleCode.DRIVER,))
    directory = FakeDirectory([DirectoryUser(present.clerk_user_id, None)])
    _run(session_factory, directory)
    again = _run(session_factory, directory)
    assert (again.deactivated_count, again.linked_count) == (0, 0)


def test_empty_directory_aborts_without_changes(session_factory, employees) -> None:
    person = employees.create((RoleCode.DRIVER,))
    with pytest.raises(BusinessRuleError) as raised:
        _run(session_factory, FakeDirectory([]))
    assert raised.value.error_code == "RECONCILIATION_ABORTED"
    assert _employee(session_factory, person.employee_id).is_active is True


def test_mass_deactivation_is_refused(session_factory, employees) -> None:
    people = [employees.create((RoleCode.DRIVER,)) for _ in range(4)]
    directory = FakeDirectory([DirectoryUser(people[0].clerk_user_id, None)])
    with pytest.raises(BusinessRuleError) as raised:
        _run(session_factory, directory)
    assert raised.value.error_code == "RECONCILIATION_ABORTED"
    assert all(_employee(session_factory, one.employee_id).is_active for one in people)


def test_directory_outage_changes_nothing(session_factory, employees) -> None:
    person = employees.create((RoleCode.DRIVER,))
    with pytest.raises(BusinessRuleError) as raised:
        _run(session_factory, FakeDirectory(failure=True))
    assert raised.value.status_code == 503
    assert _employee(session_factory, person.employee_id).is_active is True


def _user_json(index: int) -> dict[str, object]:
    return {
        "id": f"user_{index}",
        "primary_email_address_id": "idn_1",
        "email_addresses": [
            {"id": "idn_1", "email_address": f"u{index}@x.example", "verification": {"status": "verified"}}
        ],
    }


def _directory(handler, sleeps: list[float] | None = None) -> ClerkIdentityDirectory:
    return ClerkIdentityDirectory(
        "sk_test_fake",
        "https://api.clerk.test",
        transport=httpx.MockTransport(handler),
        sleeper=(sleeps.append if sleeps is not None else (lambda _seconds: None)),
    )


def test_directory_pages_through_all_users_with_the_secret_key() -> None:
    seen_offsets: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer sk_test_fake"
        offset = int(request.url.params["offset"])
        seen_offsets.append(str(offset))
        count = 100 if offset == 0 else 1
        return httpx.Response(200, json=[_user_json(offset + i) for i in range(count)])

    users = _directory(handler).list_users()
    assert len(users) == 101 and seen_offsets == ["0", "100"]
    assert users[0].verified_email == "u0@x.example"


def test_directory_retries_server_errors_then_succeeds() -> None:
    attempts = {"count": 0}
    sleeps: list[float] = []

    def handler(_request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        if attempts["count"] < 3:
            return httpx.Response(503)
        return httpx.Response(200, json=[_user_json(1)])

    assert len(_directory(handler, sleeps).list_users()) == 1
    assert attempts["count"] == 3 and sleeps == [0.5, 1.0]


def test_directory_gives_up_after_bounded_retries() -> None:
    attempts = {"count": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        return httpx.Response(500)

    with pytest.raises(IdentityDirectoryError):
        _directory(handler).list_users()
    assert attempts["count"] == 3


def test_directory_does_not_retry_authorization_failures() -> None:
    attempts = {"count": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        return httpx.Response(401)

    with pytest.raises(IdentityDirectoryError):
        _directory(handler).list_users()
    assert attempts["count"] == 1


def test_directory_failure_on_a_later_page_never_returns_partial_data() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if int(request.url.params["offset"]) == 0:
            return httpx.Response(200, json=[_user_json(i) for i in range(100)])
        return httpx.Response(500)

    with pytest.raises(IdentityDirectoryError):
        _directory(handler).list_users()


@pytest.mark.parametrize("body", ["not json", {"unexpected": "shape"}, [{"no_id": True}], ["string"]])
def test_directory_rejects_malformed_responses(body) -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        if isinstance(body, str):
            return httpx.Response(200, content=body)
        return httpx.Response(200, json=body)

    with pytest.raises(IdentityDirectoryError):
        _directory(handler).list_users()


def test_directory_requires_a_secret_key() -> None:
    with pytest.raises(IdentityDirectoryError):
        ClerkIdentityDirectory("", "https://api.clerk.test").list_users()
