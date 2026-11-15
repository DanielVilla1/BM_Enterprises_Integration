# ===== AI GENERATED: test_problem_details =====
# Purpose: Every error path returns RFC 9457 problem+json without internals
# Inputs: a scratch app with failing routes, plus the real app
# Returns: pass/fail
# Flow:
# 1. Validation, HTTP, business, DB and unhandled errors share one format
# 2. Bodies carry a trace id and no stack trace, SQL or file path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy.exc import OperationalError

from backend.src.Entity.business_rule_error import BusinessRuleError
from backend.src.problem_details import install_problem_details

FORBIDDEN_FRAGMENTS = ("Traceback", 'File "', "SELECT ", ".py", "/etc/passwd", "sqlite")


class SampleBody(BaseModel):
    quantity: int


def _scratch_client() -> TestClient:
    scratch = FastAPI()
    install_problem_details(scratch)

    @scratch.post("/validate")
    def validate(body: SampleBody) -> dict[str, int]:
        return {"quantity": body.quantity}

    @scratch.get("/rule")
    def rule() -> None:
        raise BusinessRuleError(409, "CAPACITY_EXCEEDED", "Conflict", "Load exceeds truck capacity.")

    @scratch.get("/database")
    def database() -> None:
        raise OperationalError("SELECT secret FROM /etc/passwd", {}, Exception("sqlite broke"))

    @scratch.get("/crash")
    def crash() -> None:
        raise RuntimeError("secret /etc/passwd SELECT * FROM salaries")

    return TestClient(scratch, raise_server_exceptions=False)


def _assert_problem(response, status: int, code: str) -> dict[str, object]:
    assert response.status_code == status
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert body["code"] == code and body["status"] == status
    assert body["trace_id"] == response.headers["x-trace-id"]
    for fragment in FORBIDDEN_FRAGMENTS:
        assert fragment not in response.text
    return body


def test_validation_error_is_problem_json_without_echoing_input() -> None:
    response = _scratch_client().post("/validate", json={"quantity": "secret-value"})
    body = _assert_problem(response, 422, "VALIDATION_ERROR")
    assert body["errors"][0]["field"] == "body.quantity"
    assert "secret-value" not in response.text


def test_unknown_route_is_problem_json() -> None:
    _assert_problem(_scratch_client().get("/missing"), 404, "HTTP_404")


def test_wrong_method_is_problem_json() -> None:
    _assert_problem(_scratch_client().get("/validate"), 405, "HTTP_405")


def test_business_rule_error_uses_its_stable_code() -> None:
    _assert_problem(_scratch_client().get("/rule"), 409, "CAPACITY_EXCEEDED")


def test_database_outage_is_503_without_sql() -> None:
    _assert_problem(_scratch_client().get("/database"), 503, "DATABASE_UNAVAILABLE")


def test_unhandled_exception_is_500_without_internals() -> None:
    _assert_problem(_scratch_client().get("/crash"), 500, "INTERNAL_ERROR")


def test_real_app_validation_error_is_problem_json(client, employees, headers_for) -> None:
    from backend.src.Entity.access import RoleCode

    owner = employees.create((RoleCode.OWNER,))
    response = client.get("/api/v1/employees/not-a-uuid", headers=headers_for(owner))
    _assert_problem(response, 422, "VALIDATION_ERROR")


def test_client_supplied_trace_header_is_ignored(client) -> None:
    response = client.get("/api/v1/me", headers={"x-trace-id": "attacker-chosen"})
    assert response.headers["x-trace-id"] != "attacker-chosen"
