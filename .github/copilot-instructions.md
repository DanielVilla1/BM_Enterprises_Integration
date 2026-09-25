# Copilot Development Governance (React + FastAPI Strict Mode)

Last Update: 2026-03-03  
Authority: AI + Human  
Language: JavaScript (JSDoc for frontend) + Python (Strict Type Hints for backend)

This document defines non-negotiable architectural, structural, and naming rules for a React frontend and FastAPI backend stack.

AI must enforce these rules before generating code for their respective languages.

No structural drift.
No undocumented patterns.
No creative deviations.

---

# 1. Authority Model

- Folder-specific rules override global rules.
- Global rules are non-negotiable.
- AI must reject rule violations before generation.
- If conflict occurs → STOP and request clarification.
- Modular boundaries are enforced before implementation.

Hard stop is default behavior.

---

# 2. Modular Doctrine (MANDATORY)

The system must follow Modular Architecture.

Each domain must be isolated.

### Backend Structure

backend/

- Controller/
- Service/
- Repository/
- DTO/
- Entity/
- Contract/

Descriptions:

- `Controller/` : HTTP entry points and request/response mapping. Controllers validate incoming requests, transform to DTOs, call Services, and produce HTTP responses (no DB queries or business rules here).
- `Service/` : Application/use-case orchestration and business rules. Services coordinate repositories, infrastructure adapters, and transactions; they contain the core application logic.
- `Repository/` : Data-access layer. Repositories encapsulate all persistence concerns (ORM/SQL) and map between storage models and domain `Entity` objects.
- `DTO/` : Data Transfer Objects used at layer boundaries. DTOs define request and response shapes and decouple API contracts from persistence models.
- `Entity/` : Domain model objects representing core business concepts and invariants. Entities are persistence-agnostic and used inside Services and Repositories.
- `Contract/` : Interface definitions (ports) for repositories, services, and adapters. Use Contracts for dependency inversion and to make implementations swappable in tests.

backend/endpoint/

- Account/
- Booking/
- inspection/
- Analytics/
- Payment/ (Paymongo)
- Dashboard/

Descriptions:

- `Account/` : Endpoints and controllers dealing with user accounts, authentication, profile management, and account settings.
- `Booking/` : Reservation and booking-related endpoints, scheduling logic orchestration, and booking lifecycle handlers.
- `inspection/` : Inspection workflows, checklists, and related domain orchestration for audit/inspection features.
- `Analytics/` : Lightweight aggregation endpoints and read-only reporting APIs (no heavy ETL inside controllers).
- `Payment/` : Payment endpoints and gateway adapters; wrap Paymongo SDK in the Infrastructure layer and call from services.
- `Payment/` : Payment endpoints and gateway adapters; wrap Paymongo SDK in the Infrastructure layer and call from services.
- `Dashboard/` : Composite endpoints used by dashboard UIs, coordinating multiple services and read-model queries.

Rules:

- No external SDK inside Domain layer.
- No database logic inside Controller.
- No business logic inside Repository.
- No entity exposure in API response.
- All responses must use DTO or Contract.

---

### Frontend Structure

frontend/src/

- components/
- hooks/
- store/ (React Context / Redux / Zustand — project choice)
- services/
- utils/

Descriptions:

- `components/` : Presentational React components. Components must remain pure UI; they should receive props and emit events (callbacks).
- `hooks/` : Reusable React hooks for local logic, data fetching orchestration, and encapsulated behaviours.
- `store/` : Global state management (React Context, Redux, or Zustand). One store per domain; prefer explicit state shape and avoid business-rule branching here.
- `services/` : API clients and adapters for network calls and external integrations. All HTTP and SDK usage must be wrapped here and exposed via small functions.
- `utils/` : Pure, side-effect-free helper functions, formatters, and validators. Keep them small, well-documented, and platform-agnostic.

Rules:

- No API call inside `components/`.
- No business rule inside `components/`.
- API calls must go through `services/`.
- State must go through `store/` (choose a library explicitly per project).
- No cross-domain service chaining.
- Shared logic must go under `shared/`.

Modular implementation is mandatory.
Flat architecture is forbidden.

---

# 3. Language Rules (JavaScript Strict Mode)

TypeScript is NOT used.

Instead:

- JSDoc typing is mandatory.
- All exported functions must have JSDoc.
- All parameters must have JSDoc type.
- All return types must be declared.
- No implicit return types.
- No dynamic untyped objects longer than 2 properties.
- No `any`-like ambiguity.
- No silent undefined returns.

Example:

```js
/**
 * @function createReservationService
 * @description Creates a reservation record.
 * @param {Object} inputPayload
 * @param {string} inputPayload.userIdentifier
 * @param {string} inputPayload.itemIdentifier
 * @returns {Promise<Object>}
 */
async function createReservationService(inputPayload) {
```

No function without documentation allowed.

---

# 4. Naming Doctrine (STRICT)

Predictability > brevity.

Minimum Length Rules:

- Variables → minimum 4 characters
- Functions → minimum 6 characters
- Classes → minimum 6 characters
- Stores → minimum 6 characters
- Services → minimum 6 characters

Forbidden names:

- data
- item
- obj
- val
- thing
- temp
- test
- misc

Loop index short names allowed only with inline comment.

Names must reflect domain intent.

Examples:

Allowed:

- reservationRecord
- paymentProcessorService
- authenticationVerifier

Not Allowed:

- data
- service
- manager
- handler (unless domain-qualified)

---

# 5. AI Comment Requirement (MANDATORY)

When AI generates or modifies code, a comment header must exist:

```js
// ===== AI GENERATED: <FunctionName> =====
// Purpose:
// Inputs:
// Returns:
// Flow:
// 1.
// 2.
// 3.
```

Rules:

- Must not exceed 8 lines.
- Must describe logic tree.
- Must appear before implementation.
- Missing header = invalid output.

If AI edits existing code:

- Must add `// AI MODIFIED:` comment.

No silent AI generation allowed.

---

# 6. Separation of Concerns Enforcement

Backend:

Controller → Request handling only
Service → Business orchestration only
Repository → Database only
Infrastructure → External systems only

Frontend:

Component → Presentation only
Store → Cross-component state
Service → API calls and business logic only
Utils → Pure functions only

No layer mixing allowed.

---

# 7. Security Enforcement

- Frontend must never trust role from UI.
- Payment (Paymongo) only callable from backend.
- PDF official generation must be backend.
- No secret keys inside frontend.

All sensitive logic server-side only.

---

# 8. Dependency Wrapping Rule

External libraries must be wrapped.

Examples:

backend/src/Infrastructure/Payment/XenditClient.php
frontend/src/shared/services/barcodeScannerService.js

No direct SDK usage inside domain modules.

Infrastructure adapters only.

---

# 9. Consistency Enforcement

When creating new module:

1. Search existing module pattern.
2. Identify structure.
3. Replicate structure exactly.
4. Replicate naming pattern.
5. Replicate documentation pattern.
6. Do not improvise.

No creative variations allowed.

---

# 10. Store Rules

- One store per domain.
- No mega-store.
- Explicit state structure required.
- No direct state mutation outside store.
- No API calls inside store unless domain-global.

Store must not contain business rule branching.

---

# 11. Routing & RBAC

Frontend:

- Route guards centralized in router/middleware.
- No inline role checks in components.
- No conditional UI role logic unless derived from store.
- Access validation must use backend-confirmed roles.

Backend:

- No inline role string comparison inside controllers.

---

# 12. No Structural Drift

If a domain adopts:

components/
store/
utils/
services/

All domains must follow identical structure.

No partial modular adoption.

---

# 13. Violation Protocol

If AI detects:

- Layer mixing
- Naming violation
- Missing JSDoc
- Missing AI header
- Business logic in wrong layer
- External SDK inside domain
- Structural inconsistency

AI must:

- STOP
- State violated rule
- Request clarification
- Not continue generation

Hard stop by default.

---

# 14. Build & Validation Expectation

Before considering feature complete:

- Backend must pass FastAPI/Pydantic validation and unit tests (pytest).
- Frontend must build without warnings and run type / lint checks where configured.
- No unused imports.
- No dead functions.
- No commented-out code blocks.

Clean code is mandatory.
