# ===== AI GENERATED: finance_controller =====
# Purpose: Financial HTTP boundary with explicit capability checks and typed commands.
# Inputs: Validated DTOs, authenticated access, and a required retry key.
# Returns: Public command/workspace DTOs.
# Flow: Authorize before invoking services; keep calculations and persistence out of controllers.

from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Response

from ..DTO.account_dto import ProblemDetailsResponse
from ..DTO.finance_dto import (
    AdjustmentRequest,
    AdvanceApprovalRequest,
    AdvanceRequest,
    ChargeRequest,
    CommandRequest,
    CommandResponse,
    DelegationRequest,
    ExpenseRequest,
    FinanceWorkspaceResponse,
    InvoiceRequest,
    MovementRequest,
    PaymentRequest,
    PayrollRequest,
    RateRequest,
    ReasonRequest,
    ReportsResponse,
    ReviewRequest,
)
from ..Entity.access import AccessLevel
from ..Infrastructure.Imaging.presentation_document import render_presentation_document
from ..providers import (
    AccessContext,
    get_advance_service,
    get_billing_service,
    get_finance_query_service,
    get_payroll_service,
    get_trace_id,
    get_trip_finance_service,
    require_capability,
)
from ..Service.advance_service import AdvanceService
from ..Service.billing_service import BillingService
from ..Service.finance_query_service import FinanceQueryService
from ..Service.payroll_service import PayrollService
from ..Service.trip_finance_service import TripFinanceService

router = APIRouter(
    prefix="/api/v1/finance",
    tags=["finance"],
    responses={
        401: {"model": ProblemDetailsResponse},
        403: {"model": ProblemDetailsResponse},
        409: {"model": ProblemDetailsResponse},
    },
)


def command_key(
    key: str = Header(
        ..., alias="Idempotency-Key", min_length=8, max_length=128, pattern=r"^[A-Za-z0-9][A-Za-z0-9._:-]+$"
    )
) -> str:
    """Validate retry identity on the header itself (FastAPI header constraints)."""
    return key


@router.get(
    "/presentation-documents/{document_id}",
    response_class=Response,
    responses={200: {"content": {"image/png": {}}}},
)
def read_presentation_document(
    document_id: UUID,
    access: AccessContext = Depends(require_capability("or.view_files")),
    service: FinanceQueryService = Depends(get_finance_query_service),
) -> Response:
    document = service.presentation_document(access.principal, access.level, document_id)
    return Response(
        render_presentation_document(str(document.trip_id)[:8], document.kind.value), media_type="image/png"
    )


@router.get("/expenses", response_model=FinanceWorkspaceResponse)
def read_expenses(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0, le=100000),
    access: AccessContext = Depends(require_capability("expense.view")),
    service: FinanceQueryService = Depends(get_finance_query_service),
    payroll: PayrollService = Depends(get_payroll_service),
) -> FinanceWorkspaceResponse:
    return service.workspace(access.principal, "expenses", limit, offset, payroll)


@router.get("/payroll", response_model=FinanceWorkspaceResponse)
def read_payroll(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0, le=100000),
    access: AccessContext = Depends(require_capability("payroll.view")),
    service: FinanceQueryService = Depends(get_finance_query_service),
    payroll: PayrollService = Depends(get_payroll_service),
) -> FinanceWorkspaceResponse:
    return service.workspace(access.principal, "payroll", limit, offset, payroll)


@router.get("/advances", response_model=FinanceWorkspaceResponse)
def read_advances(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0, le=100000),
    access: AccessContext = Depends(require_capability("cash_advance.view")),
    service: FinanceQueryService = Depends(get_finance_query_service),
    payroll: PayrollService = Depends(get_payroll_service),
) -> FinanceWorkspaceResponse:
    return service.workspace(access.principal, "advances", limit, offset, payroll)


@router.get("/billing", response_model=FinanceWorkspaceResponse)
def read_billing(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0, le=100000),
    access: AccessContext = Depends(require_capability("billing.manage")),
    service: FinanceQueryService = Depends(get_finance_query_service),
    payroll: PayrollService = Depends(get_payroll_service),
) -> FinanceWorkspaceResponse:
    return service.workspace(access.principal, "billing", limit, offset, payroll)


@router.get("/reports", response_model=ReportsResponse)
def read_reports(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0, le=100000),
    access: AccessContext = Depends(require_capability("report.view")),
    service: FinanceQueryService = Depends(get_finance_query_service),
) -> ReportsResponse:
    return service.reports(access.principal, access.level, limit, offset)


@router.post("/expenses/{trip_id}", response_model=CommandResponse)
def save_expenses(
    trip_id: UUID,
    payload: ExpenseRequest,
    access: AccessContext = Depends(require_capability("expense.enter")),
    service: TripFinanceService = Depends(get_trip_finance_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"save_expenses:{trip_id}",
        payload,
        trace_id,
        lambda: service.save_expenses(access.principal, trip_id, payload),
    )


@router.post("/expenses/{trip_id}/submit", response_model=CommandResponse)
def submit_expenses(
    trip_id: UUID,
    payload: CommandRequest,
    access: AccessContext = Depends(require_capability("expense.enter")),
    service: TripFinanceService = Depends(get_trip_finance_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"submit_expenses:{trip_id}",
        payload,
        trace_id,
        lambda: service.submit_expenses(access.principal, trip_id),
    )


@router.post("/expenses/{trip_id}/review", response_model=CommandResponse)
def review_expenses(
    trip_id: UUID,
    payload: ReviewRequest,
    access: AccessContext = Depends(require_capability("expense.approve", AccessLevel.FULL)),
    service: TripFinanceService = Depends(get_trip_finance_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"review_expenses:{trip_id}",
        payload,
        trace_id,
        lambda: service.review_expenses(access.principal, trip_id, payload),
    )


@router.post("/charges/{trip_id}", response_model=CommandResponse)
def finalize_charge(
    trip_id: UUID,
    payload: ChargeRequest,
    access: AccessContext = Depends(require_capability("charge.finalize", AccessLevel.FULL)),
    service: TripFinanceService = Depends(get_trip_finance_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"finalize_charge:{trip_id}",
        payload,
        trace_id,
        lambda: service.finalize_charge(access.principal, trip_id, payload),
    )


@router.post("/charges/{trip_id}/approve-variance", response_model=CommandResponse)
def approve_charge(
    trip_id: UUID,
    payload: CommandRequest,
    access: AccessContext = Depends(require_capability("earning_percentage.set", AccessLevel.FULL)),
    service: TripFinanceService = Depends(get_trip_finance_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"approve_charge:{trip_id}",
        payload,
        trace_id,
        lambda: service.approve_charge_variance(access.principal, trip_id),
    )


@router.post("/earnings/{trip_id}/calculate", response_model=CommandResponse)
def calculate_earnings(
    trip_id: UUID,
    payload: CommandRequest,
    access: AccessContext = Depends(require_capability("earnings.calculate", AccessLevel.FULL)),
    service: TripFinanceService = Depends(get_trip_finance_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"calculate_earnings:{trip_id}",
        payload,
        trace_id,
        lambda: service.generate_earnings(access.principal, trip_id),
    )


@router.post("/holds/{trip_id}/release", response_model=CommandResponse)
def release_hold(
    trip_id: UUID,
    payload: ReasonRequest,
    access: AccessContext = Depends(require_capability("earning_percentage.set", AccessLevel.FULL)),
    service: TripFinanceService = Depends(get_trip_finance_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"release_hold:{trip_id}",
        payload,
        trace_id,
        lambda: service.release_hold(access.principal, trip_id),
    )


@router.post("/rates", response_model=CommandResponse)
def create_rates(
    payload: RateRequest,
    access: AccessContext = Depends(require_capability("earning_percentage.set", AccessLevel.FULL)),
    service: TripFinanceService = Depends(get_trip_finance_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        "create_rates",
        payload,
        trace_id,
        lambda: service.create_rate(access.principal, payload),
    )


@router.post("/advances", response_model=CommandResponse)
def request_advance(
    payload: AdvanceRequest,
    access: AccessContext = Depends(require_capability("cash_advance.request")),
    service: AdvanceService = Depends(get_advance_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        "request_advance",
        payload,
        trace_id,
        lambda: service.request_advance(access.principal, payload),
    )


@router.post("/advances/{identifier}/approve", response_model=CommandResponse)
def approve_advance(
    identifier: UUID,
    payload: AdvanceApprovalRequest,
    access: AccessContext = Depends(require_capability("cash_advance.approval_action", AccessLevel.FULL)),
    service: AdvanceService = Depends(get_advance_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"approve_advance:{identifier}",
        payload,
        trace_id,
        lambda: service.approve_advance(access.principal, identifier, payload),
    )


@router.post("/advances/{identifier}/release", response_model=CommandResponse)
def release_advance(
    identifier: UUID,
    payload: MovementRequest,
    access: AccessContext = Depends(require_capability("cash_advance.release_repay", AccessLevel.FULL)),
    service: AdvanceService = Depends(get_advance_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"release_advance:{identifier}",
        payload,
        trace_id,
        lambda: service.release_advance(access.principal, identifier, payload),
    )


@router.post("/advances/{identifier}/return", response_model=CommandResponse)
def return_operating(
    identifier: UUID,
    payload: MovementRequest,
    access: AccessContext = Depends(require_capability("cash_advance.release_repay", AccessLevel.FULL)),
    service: AdvanceService = Depends(get_advance_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"return_operating:{identifier}",
        payload,
        trace_id,
        lambda: service.return_operating_funds(access.principal, identifier, payload),
    )


@router.post("/advances/{identifier}/reconcile", response_model=CommandResponse)
def reconcile_operating(
    identifier: UUID,
    payload: ReasonRequest,
    access: AccessContext = Depends(require_capability("cash_advance.approve", AccessLevel.FULL)),
    service: AdvanceService = Depends(get_advance_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"reconcile_operating:{identifier}",
        payload,
        trace_id,
        lambda: service.reconcile_operating(access.principal, identifier),
    )


@router.post("/advance-delegations", response_model=CommandResponse)
def delegate_approver(
    payload: DelegationRequest,
    access: AccessContext = Depends(require_capability("cash_advance.approve", AccessLevel.FULL)),
    service: AdvanceService = Depends(get_advance_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        "delegate_approver",
        payload,
        trace_id,
        lambda: service.delegate_approver(access.principal, payload),
    )


@router.post("/advance-delegations/{identifier}/revoke", response_model=CommandResponse)
def revoke_delegation(
    identifier: UUID,
    payload: ReasonRequest,
    access: AccessContext = Depends(require_capability("cash_advance.approve", AccessLevel.FULL)),
    service: AdvanceService = Depends(get_advance_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"revoke_delegation:{identifier}",
        payload,
        trace_id,
        lambda: service.revoke_delegation(access.principal, identifier),
    )


@router.post("/adjustments", response_model=CommandResponse)
def propose_adjustment(
    payload: AdjustmentRequest,
    access: AccessContext = Depends(require_capability("deduction.record", AccessLevel.FULL)),
    service: PayrollService = Depends(get_payroll_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        "propose_adjustment",
        payload,
        trace_id,
        lambda: service.propose_adjustment(access.principal, payload),
    )


@router.post("/adjustments/{identifier}/approve", response_model=CommandResponse)
def approve_adjustment(
    identifier: UUID,
    payload: CommandRequest,
    access: AccessContext = Depends(require_capability("deduction.approve", AccessLevel.FULL)),
    service: PayrollService = Depends(get_payroll_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"approve_adjustment:{identifier}",
        payload,
        trace_id,
        lambda: service.approve_adjustment(access.principal, identifier),
    )


@router.post("/payrolls", response_model=CommandResponse)
def prepare_payroll(
    payload: PayrollRequest,
    access: AccessContext = Depends(require_capability("payroll.prepare", AccessLevel.FULL)),
    service: PayrollService = Depends(get_payroll_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        "prepare_payroll",
        payload,
        trace_id,
        lambda: service.prepare_payroll(access.principal, payload),
    )


@router.post("/payrolls/{identifier}/finalize", response_model=CommandResponse)
def finalize_payroll(
    identifier: UUID,
    payload: CommandRequest,
    access: AccessContext = Depends(require_capability("payroll.prepare", AccessLevel.FULL)),
    service: PayrollService = Depends(get_payroll_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"finalize_payroll:{identifier}",
        payload,
        trace_id,
        lambda: service.finalize_payroll(access.principal, identifier),
    )


@router.post("/payrolls/{identifier}/reverse", response_model=CommandResponse)
def reverse_payroll(
    identifier: UUID,
    payload: ReasonRequest,
    access: AccessContext = Depends(require_capability("payroll.reverse", AccessLevel.FULL)),
    service: PayrollService = Depends(get_payroll_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"reverse_payroll:{identifier}",
        payload,
        trace_id,
        lambda: service.reverse_payroll(access.principal, identifier, payload.reason),
    )


@router.post("/statements/{identifier}/payments", response_model=CommandResponse)
def record_payroll_payment(
    identifier: UUID,
    payload: PaymentRequest,
    access: AccessContext = Depends(require_capability("payroll_payment.record", AccessLevel.FULL)),
    service: PayrollService = Depends(get_payroll_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"record_payroll_payment:{identifier}",
        payload,
        trace_id,
        lambda: service.record_payment(access.principal, identifier, payload),
    )


@router.post("/invoices", response_model=CommandResponse)
def create_invoice(
    payload: InvoiceRequest,
    access: AccessContext = Depends(require_capability("billing.manage", AccessLevel.FULL)),
    service: BillingService = Depends(get_billing_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        "create_invoice",
        payload,
        trace_id,
        lambda: service.create_invoice(access.principal, payload),
    )


@router.post("/invoices/{identifier}/issue", response_model=CommandResponse)
def issue_invoice(
    identifier: UUID,
    payload: CommandRequest,
    access: AccessContext = Depends(require_capability("billing.manage", AccessLevel.FULL)),
    service: BillingService = Depends(get_billing_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"issue_invoice:{identifier}",
        payload,
        trace_id,
        lambda: service.issue_invoice(access.principal, identifier),
    )


@router.post("/invoices/{identifier}/request-void", response_model=CommandResponse)
def request_invoice_void(
    identifier: UUID,
    payload: ReasonRequest,
    access: AccessContext = Depends(require_capability("billing.manage", AccessLevel.FULL)),
    service: BillingService = Depends(get_billing_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"request_invoice_void:{identifier}",
        payload,
        trace_id,
        lambda: service.request_void(access.principal, identifier, payload.reason),
    )


@router.post("/invoices/{identifier}/approve-void", response_model=CommandResponse)
def approve_invoice_void(
    identifier: UUID,
    payload: CommandRequest,
    access: AccessContext = Depends(require_capability("invoice.void_approve", AccessLevel.FULL)),
    service: BillingService = Depends(get_billing_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"approve_invoice_void:{identifier}",
        payload,
        trace_id,
        lambda: service.approve_void(access.principal, identifier),
    )


@router.post("/invoices/{identifier}/payments", response_model=CommandResponse)
def record_collection(
    identifier: UUID,
    payload: PaymentRequest,
    access: AccessContext = Depends(require_capability("billing.manage", AccessLevel.FULL)),
    service: BillingService = Depends(get_billing_service),
    key: str = Depends(command_key),
    trace_id: str = Depends(get_trace_id),
) -> CommandResponse:
    return service.execute(
        access.principal,
        key,
        f"record_collection:{identifier}",
        payload,
        trace_id,
        lambda: service.record_collection(access.principal, identifier, payload),
    )
