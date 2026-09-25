---
description: "Rules for backend Contract interfaces (ports) used to decouple layers"
applyTo: "backend/**/Contract/**/*.py"
---

# Contract Folder Rules

This folder contains interface definitions (ports) used across backend layers to enable dependency inversion and testable implementations. Contracts declare signatures only — no implementation or persistence logic.

## 1. Architecture Rules

- Purpose: Contracts express behavior and intent between `Service` and `Repository`/`Infrastructure` layers.
- SOC & SRP: Each Contract must have a single responsibility and contain only methods related to that responsibility.
- Explicit naming: Interfaces must use clear, descriptive names (e.g., `IReservationRepository`, `IPaymentGateway`) and follow the naming doctrine in `.github/copilot-instructions.md` (min lengths, no generic names).
- No SDK or DB code: Contracts must never import or reference SDKs, ORMs, or database concerns.
- AI header & docs: When AI generates or modifies a Contract file, include the required AI header and use Python type hints and concise docstrings.

## 2. Modular Interaction Rules

- Location: Place contracts under `backend/src/Contract/<domain>/` or `backend/src/Contract/` for global ports.
- Direction: Services depend on Contracts (interfaces); repositories and infrastructure implement Contracts.
- Testing: Tests should rely on Contract types and provide fakes/mocks implementing the Contract for unit tests.
- No circular dependencies: Contracts must be dependency-light (no imports from `Service` or `Repository` implementations).

## 3. Type Rules

- Use static typing: All functions and methods must have explicit Python type hints; avoid `Any`.
- Prefer `typing.Protocol` or abstract base classes for Contracts to enable structural subtyping and mocks.
- DTOs: Use DTO classes (from `backend/src/DTO/`) in method signatures rather than ORM `Entity` types for layer boundaries.
- Return types: Declare precise return types (e.g., `Optional[ReservationDTO]`, `List[TodoDTO]`).

## 4. Data Fetching Rules

- No fetching implementation: Contracts declare fetch/save signatures only — actual data access belongs in `Repository` or `Infrastructure`.
- Sync vs Async: Choose project-wide sync or async conventions. Contracts must follow the chosen paradigm consistently across all interfaces.
- Pagination & params: Explicitly model pagination, filters, and sorting in Contract method signatures (avoid free-form dicts).

## 5. Implementation Guidance

- Keep Contracts small and focused: Prefer multiple narrow interfaces over one large interface.
- Versioning: If a Contract evolves, create a new interface (`IProductRepositoryV2`) instead of changing the public shape in-place when breaking changes occur.
- Documentation: Add a one-paragraph docstring describing intent and expected invariants for each Contract.

## 6. Consistency Enforcement

- Replicate structure: New domains must add corresponding Contracts following the same folder and naming patterns.
- CI checks: Enforce presence of type hints, AI header, and naming rules via pre-commit hooks or CI linters.
- Violation protocol: If a generated Contract violates these rules, the AI must STOP, report the violated rule, and request clarification before proceeding.

---

Keep Contracts minimal, well-typed, and implementation-agnostic. Follow `.github/copilot-instructions.md` for naming, JSDoc/type conventions, and AI header requirements.
