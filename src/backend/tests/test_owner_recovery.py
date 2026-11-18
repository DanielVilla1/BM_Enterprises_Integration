import pytest
from sqlalchemy import select

from backend.src.Contract.i_identity_directory import DirectoryUser
from backend.src.Entity.access import RoleCode
from backend.src.Entity.business_rule_error import BusinessRuleError
from backend.src.Repository.audit_repository import AuditRepository
from backend.src.Repository.employee_repository import EmployeeRepository
from backend.src.Repository.orm_models import AuditLogRow
from backend.src.Repository.unit_of_work import SqlAlchemyUnitOfWork
from backend.src.Service.owner_recovery_service import OwnerRecoveryService


def recovery(session):
    return OwnerRecoveryService(
        EmployeeRepository(session), AuditRepository(session), SqlAlchemyUnitOfWork(session)
    )


def test_existing_owner_recovery_repairs_only_the_link_and_is_audited_and_repeatable(
    employees, session_factory, client, headers_for
):
    owner = employees.create((RoleCode.OWNER,), active=False)
    identity = DirectoryUser("user_recovered_owner", owner.email)
    with session_factory() as session:
        first = recovery(session).recover(owner.email, identity)
        second = recovery(session).recover(owner.email, identity)
        assert first.clerk_user_id == identity.user_id
        assert second.is_active and second.role_codes == (RoleCode.OWNER,)
        actions = session.scalars(
            select(AuditLogRow.action).where(AuditLogRow.entity_id == str(owner.employee_id))
        ).all()
        assert actions.count("employee.identity_linked") == 1
        assert actions.count("employee.activated") == 1
    response = client.get("/api/v1/me", headers=headers_for(second))
    assert response.status_code == 200
    assert response.json()["role_codes"] == ["OWNER"]


@pytest.mark.parametrize("role", [role for role in RoleCode if role != RoleCode.OWNER])
def test_recovery_cannot_promote_any_other_role(employees, session_factory, role):
    person = employees.create((role,))
    with session_factory() as session:
        with pytest.raises(BusinessRuleError, match="no existing Owner"):
            recovery(session).recover(person.email, DirectoryUser("user_recovery", person.email))
        unchanged = EmployeeRepository(session).get_by_id(person.employee_id)
        assert unchanged.role_codes == (role,)
        assert unchanged.clerk_user_id == person.clerk_user_id


@pytest.mark.parametrize("verified_email", [None, "different@example.invalid"])
def test_recovery_requires_the_matching_verified_email(employees, session_factory, verified_email):
    owner = employees.create((RoleCode.OWNER,))
    with session_factory() as session:
        with pytest.raises(BusinessRuleError, match="verified Clerk email"):
            recovery(session).recover(owner.email, DirectoryUser("user_recovery", verified_email))
        assert EmployeeRepository(session).get_by_id(owner.employee_id).clerk_user_id == owner.clerk_user_id


def test_recovery_cannot_take_a_sign_in_from_another_employee(employees, session_factory):
    owner = employees.create((RoleCode.OWNER,))
    driver = employees.create((RoleCode.DRIVER,))
    with session_factory() as session:
        with pytest.raises(BusinessRuleError, match="already linked"):
            recovery(session).recover(owner.email, DirectoryUser(driver.clerk_user_id, owner.email))
        assert EmployeeRepository(session).get_by_id(owner.employee_id).clerk_user_id == owner.clerk_user_id
