---
description: "Rules for backend Services (business orchestration)"
applyTo: "backend/**/Service/**/*.py"
---

# Service Folder Rules

Services implement application use-cases and business rules. They orchestrate Repositories, Infrastructure adapters, and enforce invariants.

## 1. Architecture Rules

- Purpose: Coordinate repositories and infrastructure to implement application logic and transactions.
- SRP: Each service should represent a coherent application capability (e.g., `ReservationService`).
- Naming: Use descriptive service names per naming doctrine.
- AI header & docs: AI-generated/modified service files must include the AI header and concise docstrings; use explicit Python type hints.

## 2. Modular Interaction Rules

- Location: Place services under `backend/src/Service/<domain>/` or `backend/src/Service/`.
- Dependencies: Services depend on Contracts (interfaces) or repository implementations injected via factories/providers.
- No HTTP concerns: Services should not import FastAPI or handle HTTP specifics; that's a controller responsibility.
- Transaction boundaries: Services should manage transactions and rollback semantics where appropriate.

## 3. Type Rules

- Explicit typing: Use full Python type hints for method signatures and return types.
- Domain types: Prefer Entities and DTOs for inputs/outputs; avoid returning raw ORM query objects.

## 4. Business Rules & Validation

- Centralize rules: Implement business validations and invariants in Services; keep them unit-testable.
- Exceptions: Raise domain-specific exceptions; controllers map these to HTTP responses.

## 5. Testing & Observability

- Unit tests: Mock repositories via Contracts to test service logic in isolation.
- Logging: Services should log important state transitions and errors, avoiding sensitive data.

## 6. Consistency Enforcement

- Replicate structure: New services must follow folder and naming patterns.
- CI checks: Enforce presence of type hints, AI header, and unit tests for core behaviors.
- Violation protocol: If service contains direct DB or SDK calls, the AI must STOP and request clarification.

---

Services are the heart of the application — keep them focused, typed, and orchestrating only.
