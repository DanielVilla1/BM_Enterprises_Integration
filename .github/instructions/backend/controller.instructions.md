---
description: "Rules for backend Controllers (FastAPI routers) defining HTTP entry points"
applyTo: "backend/**/Controller/**/*.py"
---

# Controller Folder Rules

Controllers (FastAPI routers) are the HTTP orchestration layer. They accept requests, validate and transform inputs into DTOs, delegate to `Service` layer, and return response DTOs or appropriate HTTP errors. Controllers must never contain business logic or direct persistence/SDK calls.

## 1. Architecture Rules

- Purpose: Controllers map transport (HTTP) to application use-cases implemented in `Service`.
- SOC & SRP: Each controller file (or router) should represent a cohesive set of endpoints for a single domain or resource.
- Explicit naming: Controllers should be named to reflect resource intent (e.g., `reservation_controller.py`, `user_controller.py`). Follow naming doctrine from `.github/copilot-instructions.md` (min lengths, avoid generic names).
- Thin controllers: Keep controllers minimal — input validation, DTO conversion, calling service methods, and mapping service results to response DTOs.
- No DB/SDK: Do not import ORMs, database sessions, or external SDKs in controllers. Use `Repository`/`Infrastructure` through `Service`.
- AI header & docstrings: Files generated or modified by AI must include the AI header comment. Use concise module and function docstrings and Python type hints.

## 2. Modular Interaction Rules

- Location: Place controllers under `backend/src/<domain>/Controller/` or `backend/src/Controller/` following repository conventions.
- Dependency injection: Use FastAPI `Depends` to inject `Service` instances or DB sessions via well-defined providers (factories in `Controller` or top-level providers module).
- DTO boundaries: Convert incoming requests to `DTO` shapes (Pydantic models) before passing to services; services should expect DTOs or domain `Entity` objects as defined by Contracts.
- Error handling: Controllers should translate service exceptions to appropriate HTTP responses (status codes and structured error DTOs). Business exceptions should originate from Services.
- No circular imports: Controllers must import Contracts and DTOs, not Service implementations directly (use factories/providers when necessary).

## 3. Type Rules

- Python typing: All controller functions and handlers must include explicit type hints for parameters and return types.
- Pydantic models: Use Pydantic `BaseModel` DTOs for request bodies and response models. Always declare `response_model` on FastAPI route decorators when possible.
- Avoid `Any`: Do not use `Any` in public handler signatures; prefer explicit DTOs or `Dict[str, Any]` only where unavoidable and documented.

## 4. Data Fetching Rules

- No fetching in controllers: Controllers must not perform database queries or external API calls directly. Delegate to Services which in turn use Repositories/Infrastructure.
- Async vs sync: Follow the project-wide convention (async FastAPI handlers recommended). Controllers must consistently adhere to the chosen model.
- Pagination and filtering: Accept pagination/filter parameters as typed query parameters and pass structured DTOs to Services — do not assemble SQL or query objects inside controllers.

## 5. Response & Validation

- Response models: Use `response_model` in route decorators and return DTOs or Pydantic models (with `orm_mode` when mapping from ORM models inside Repositories).
- Validation errors: Let Pydantic and FastAPI handle schema validation; map domain/service validation errors to `HTTPException` with proper status codes.
- Status codes: Ensure endpoints return correct HTTP status codes (201 for create, 204 for delete where no body is returned, etc.).

## 6. Consistency Enforcement

- Folder and file naming: Follow the canonical structure and naming rules from `.github/copilot-instructions.md`.
- AI generation checks: CI/pre-commit should validate AI header presence, type hints, and `response_model` usage for controllers.
- Tests: Add controller-level tests (FastAPI TestClient) to verify request/response contracts and error mapping.
- Violation protocol: If a controller violates these rules (business logic, DB calls, missing DTOs), the AI must STOP, report the violation, and request clarification before proceeding.

---

Controllers are orchestration-only: validate, convert to DTO, call Service, and return DTO-based responses. Keep them small, typed, and testable.
