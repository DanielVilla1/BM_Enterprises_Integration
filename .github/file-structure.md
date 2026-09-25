# Project File Structure (React + FastAPI Strict Modular Architecture)

Root structure:

- backend/
- frontend/

No cross-layer mixing.
No structural drift.
No flat architecture allowed.

---

# 1. Backend Structure

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
- `Dashboard/` : Composite endpoints used by dashboard UIs, coordinating multiple services and read-model queries.

Rules:

- No external SDK inside Domain layer.
- No database logic inside Controller.
- No business logic inside Repository.
- No entity exposure in API response.
- All responses must use DTO or Contract.

---

# 2. Frontend Structure

frontend/src/

- components/
- hooks/
- store/ ( Zustand )
- services/
- utils/

Descriptions:

- `components/` : Presentational React components. Components must remain pure UI; they should receive props and emit events (callbacks).
- `hooks/` : Reusable React hooks for local logic, data fetching orchestration, and encapsulated behaviours.
- `store/` : Global state management (Zustand). One store per domain; prefer explicit state shape and avoid business-rule branching here.
- `services/` : API clients and adapters for network calls and external integrations. All HTTP and SDK usage must be wrapped here and exposed via small functions.
- `utils/` : Pure, side-effect-free helper functions, formatters, and validators. Keep them small, well-documented, and platform-agnostic.

Rules:

- No API call inside `components/`.
- No business rule inside `components/`.
- API calls must go through `services/`.
- State must go through `store/` (choose a library explicitly per project).
- No cross-domain service chaining.
- Shared logic must go under `shared/`.

---

# 3. Structural Discipline

If one backend domain adopts:

- Controller/
- Service/
- Repository/
- DTO/
- Entity/
- Contract/

All backend domains must follow identical structure.

If one frontend domain adopts:

- components/
- store/
- utils/
- services/

All frontend domains must follow identical structure.

No partial modular adoption.
