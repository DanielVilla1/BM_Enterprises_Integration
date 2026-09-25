---
description: "Rules for backend DTOs (Pydantic models) used across layers"
applyTo: "backend/**/DTO/**/*.py"
---

# DTO Folder Rules

DTOs (Data Transfer Objects) define the shapes of data exchanged between layers and across process boundaries. DTOs must be simple, validated, and free of business logic.

## 1. Architecture Rules

- Purpose: DTOs decouple transport and persistence models; they validate and document API payloads.
- No business logic: DTOs must not contain domain rules or side effects.
- Naming: Use clear names reflecting intent (e.g., `ReservationCreateDTO`, `TodoOutDTO`) following `.github/copilot-instructions.md` naming doctrine.
- AI header & docs: When AI generates or modifies DTOs include the AI header and concise module docstrings. Use Python type hints.

## 2. Modular Interaction Rules

- Location: Place DTOs under `backend/src/DTO/<domain>/` or `backend/src/DTO/` for shared models.
- Layer usage: Controllers accept request DTOs (Pydantic inputs) and return response DTOs; Services accept DTOs or domain Entities; Repositories should not depend on DTOs for internal persistence logic.
- Mapping: Map Entity <-> DTO at service or repository boundaries; avoid leaking ORM models into controllers.

## 3. Type Rules

- Use Pydantic: All DTOs must inherit from `pydantic.BaseModel` with explicit field types.
- Validation: Use Pydantic validators and field constraints to enforce data invariants at the boundary.
- `orm_mode`: For response DTOs that will be created from ORM objects, set `Config.orm_mode = True`.
- Explicit types: Avoid `Any`; prefer `Optional[...]`, `List[...]`, and precise types for nested DTOs.

## 4. Data Fetching Rules

- DTOs are transport-only: DTOs must not perform data fetching or database operations.
- Pagination/filter DTOs: Model pagination and filter parameters as dedicated DTOs rather than free-form dicts.

## 5. Consistency Enforcement

- File layout: Keep DTOs colocated per-domain to ease discovery and reuse.
- Versioning: For breaking DTO changes create new DTO names/versions rather than changing existing public DTO shapes.
- CI checks: Enforce presence of type hints and `orm_mode` where required via linting/CI.

---

DTOs must be small, validated, and descriptive — use them to strictly separate API contracts from persistence models.
