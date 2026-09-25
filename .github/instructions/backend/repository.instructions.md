---
description: "Rules for backend Repository implementations (data access layer)"
applyTo: "backend/**/Repository/**/*.py"
---

# Repository Folder Rules

Repositories encapsulate persistence concerns: queries, mapping, and transaction management. They must not contain business rules.

## 1. Architecture Rules

- Purpose: Provide a thin abstraction over ORM/SQL for CRUD and query operations; return domain `Entity` objects or DTOs for consumption by Services.
- No business logic: Repositories must not implement business rules or orchestration.
- Naming: Use descriptive names (e.g., `ReservationRepository`) following naming doctrine.
- AI header & docs: AI-generated/modified repository files require AI header and clear docstrings.

## 2. Modular Interaction Rules

- Location: Place repositories under `backend/src/Repository/<domain>/` or `backend/src/Repository/`.
- Contracts: Repositories should implement `Contract` interfaces where applicable to enable swapping in tests.
- Session management: Keep session/connection handling explicit and minimal; prefer session injection rather than global sessions.
- Return types: Repositories should return Entities or DTOs (avoid returning raw ORM internals like session-bound objects unless converted).

## 3. Type & Safety Rules

- Explicit typing: Annotate method parameters and return types precisely (`Optional[Entity]`, `List[Entity]`).
- Transactions: Explicitly document transactional boundaries; services may orchestrate transactions, repositories can provide helper transactional methods.

## 4. Query & Performance Rules

- Avoid N+1: Repositories must use appropriate eager-loading / joins to avoid N+1 query patterns.
- Pagination & filters: Provide explicit parameters for pagination and filtering; return paged DTOs when appropriate.
- No raw SQL unless necessary: Prefer ORM querying patterns; raw SQL allowed only in specialized repository methods with justification and tests.

## 5. Testing & Mocks

- Implement fakes: Provide in-memory or lightweight fakes for repositories to use in unit tests of Services.
- Integration tests: Repository integration tests should run against a test DB and clean up state.

## 6. Consistency Enforcement

- Implement Contracts: Repositories implementing Contracts must follow the contract signatures exactly.
- CI checks: Lint for AI header, typing, and forbidden business-rule patterns.
- Violation protocol: If a repository contains business logic, the AI must STOP and request clarification.

---

Repositories must be focused, well-typed, and responsible only for persistence and mapping.
