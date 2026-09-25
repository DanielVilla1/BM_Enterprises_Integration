---
description: "Rules for backend Entity classes representing domain models"
applyTo: "backend/**/Entity/**/*.py"
---

# Entity Folder Rules

Entities represent the core domain concepts and invariants. They should be persistence-agnostic and capture business state and behaviours (minimal).

## 1. Architecture Rules

- Purpose: Entities model domain objects and invariants; they are used within Services and Repositories.
- Persistence-agnostic: Entities should avoid direct ORM or SDK concerns; mapping to persistence models is handled in Repositories.
- Naming: Use domain-reflective names (e.g., `Reservation`, `TodoItem`) following naming doctrine.
- AI header & docs: Files created/modified by AI must include AI header and module docstring; use Python type hints.

## 2. Modular Interaction Rules

- Location: Place entities under `backend/src/Entity/<domain>/` or `backend/src/Entity/` for shared concepts.
- Usage: Services operate primarily on Entities; Repositories convert between Entities and persistence representations.
- No external SDKs: Entities must not import external SDKs or database modules.

## 3. Type Rules

- Use Python typing: Declare attributes and methods with explicit type hints.
- Lightweight behaviour only: Entities may include domain helpers and invariants but should avoid complex orchestration.
- Validation: Prefer invariants enforced in Services; Entities can expose `validate()` helpers but avoid side-effectful validation.

## 4. Persistence Mapping Rules

- Mapping in Repositories: Repositories must map Entities to ORM models and vice versa; Entities should remain independent of ORM base classes.
- IDs and timestamps: Keep identity and audit fields explicit in Entities but manage DB-specific defaults in persistence layer.

## 5. Consistency Enforcement

- Replication: New domain Entities must follow folder and naming patterns exactly.
- Tests: Unit-test Entity invariants and helpers.
- CI checks: Enforce type hints and AI header presence.

---

Entities should be clear domain representations, small, and decoupled from persistence specifics.
