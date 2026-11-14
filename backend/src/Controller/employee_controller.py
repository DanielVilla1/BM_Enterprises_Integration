# ===== AI GENERATED: employee_controller =====
# Purpose: Employee, account-link and role endpoints
# Inputs: validated DTOs, AccessContext from the permission matrix
# Returns: employee DTOs (limited projection for the Ltd level)
# Flow:
# 1. require_capability gates each route
# 2. Delegate to EmployeeService with the caller's access level
# 3. Map entities to explicit response DTOs

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from ..DTO.account_dto import ProblemDetailsResponse
from ..DTO.employee_dto import (
    EmployeeCreateRequest,
    EmployeeDetailResponse,
    EmployeeLimitedResponse,
    EmployeePageResponse,
    EmployeeUpdateRequest,
    IdentityLinkRequest,
    RoleAssignmentRequest,
)
from ..Entity.access import AccessLevel
from ..Entity.employee import Employee
from ..providers import AccessContext, get_employee_service, get_trace_id, require_capability
from ..Service.employee_service import EmployeeService

router = APIRouter(
    prefix="/api/v1/employees",
    tags=["employees"],
    responses={
        401: {"model": ProblemDetailsResponse},
        403: {"model": ProblemDetailsResponse},
    },
)


def _project(employee: Employee, level: AccessLevel) -> EmployeeDetailResponse | EmployeeLimitedResponse:
    if level is AccessLevel.LTD:
        return EmployeeLimitedResponse.from_entity(employee)
    return EmployeeDetailResponse.from_entity(employee)


@router.get("", response_model=EmployeePageResponse)
def list_employees(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0, le=100000),
    active: bool | None = None,
    access: AccessContext = Depends(require_capability("employee.manage")),
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeePageResponse:
    employees = service.list_employees(access.principal, access.level, limit, offset, active)
    return EmployeePageResponse(
        items=[_project(employee, access.level) for employee in employees],
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=EmployeeDetailResponse, status_code=201)
def create_employee(
    payload: EmployeeCreateRequest,
    access: AccessContext = Depends(require_capability("employee.manage", AccessLevel.FULL)),
    service: EmployeeService = Depends(get_employee_service),
    trace_id: str = Depends(get_trace_id),
) -> EmployeeDetailResponse:
    employee = service.create_employee(
        access.principal, access.level, payload.full_name, payload.email, payload.phone, trace_id
    )
    return EmployeeDetailResponse.from_entity(employee)


@router.get("/{employee_id}", response_model=EmployeeDetailResponse | EmployeeLimitedResponse)
def read_employee(
    employee_id: UUID,
    access: AccessContext = Depends(require_capability("employee.manage")),
    service: EmployeeService = Depends(get_employee_service),
) -> EmployeeDetailResponse | EmployeeLimitedResponse:
    employee = service.get_employee(access.principal, access.level, employee_id)
    return _project(employee, access.level)


@router.patch("/{employee_id}", response_model=EmployeeDetailResponse)
def update_employee(
    employee_id: UUID,
    payload: EmployeeUpdateRequest,
    access: AccessContext = Depends(require_capability("employee.manage", AccessLevel.FULL)),
    service: EmployeeService = Depends(get_employee_service),
    trace_id: str = Depends(get_trace_id),
) -> EmployeeDetailResponse:
    employee = service.update_employee(
        access.principal,
        access.level,
        employee_id,
        payload.full_name,
        payload.email,
        payload.phone,
        trace_id,
    )
    return EmployeeDetailResponse.from_entity(employee)


@router.post("/{employee_id}/activate", response_model=EmployeeDetailResponse)
def activate_employee(
    employee_id: UUID,
    access: AccessContext = Depends(require_capability("employee.activate")),
    service: EmployeeService = Depends(get_employee_service),
    trace_id: str = Depends(get_trace_id),
) -> EmployeeDetailResponse:
    return EmployeeDetailResponse.from_entity(
        service.activate_employee(access.principal, employee_id, trace_id)
    )


@router.post("/{employee_id}/deactivate", response_model=EmployeeDetailResponse)
def deactivate_employee(
    employee_id: UUID,
    access: AccessContext = Depends(require_capability("audit_user.manage")),
    service: EmployeeService = Depends(get_employee_service),
    trace_id: str = Depends(get_trace_id),
) -> EmployeeDetailResponse:
    return EmployeeDetailResponse.from_entity(
        service.deactivate_employee(access.principal, employee_id, trace_id)
    )


@router.put("/{employee_id}/identity", response_model=EmployeeDetailResponse)
def link_employee_identity(
    employee_id: UUID,
    payload: IdentityLinkRequest,
    access: AccessContext = Depends(require_capability("audit_user.manage")),
    service: EmployeeService = Depends(get_employee_service),
    trace_id: str = Depends(get_trace_id),
) -> EmployeeDetailResponse:
    return EmployeeDetailResponse.from_entity(
        service.link_identity(access.principal, employee_id, payload.clerk_user_id, trace_id)
    )


@router.put("/{employee_id}/roles", response_model=EmployeeDetailResponse)
def assign_employee_roles(
    employee_id: UUID,
    payload: RoleAssignmentRequest,
    access: AccessContext = Depends(require_capability("audit_user.manage")),
    service: EmployeeService = Depends(get_employee_service),
    trace_id: str = Depends(get_trace_id),
) -> EmployeeDetailResponse:
    return EmployeeDetailResponse.from_entity(
        service.assign_roles(
            access.principal,
            employee_id,
            set(payload.role_codes),
            payload.exception_reason,
            trace_id,
        )
    )
