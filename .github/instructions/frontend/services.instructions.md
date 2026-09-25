---
description: "Rules for frontend services (API clients and SDK wrappers)"
applyTo: "frontend/**/services/**/*.{js,ts}"
---

# Services Folder Rules

Services are the only place for network calls and SDK usage in the frontend. They provide small, well-tested functions that the UI (components/hooks) consumes.

## 1. Architecture Rules

- Purpose: Wrap HTTP clients and SDKs, provide stable, minimal functions for consumers.
- Naming: Use clear function names (e.g., `getReservations`, `createTodo`). Follow naming doctrine.
- AI header & JSDoc: AI-generated/modified service files must include AI header and JSDoc for all exported functions and parameters.

## 2. API Client Rules

- Base URL: Use `import.meta.env.VITE_API_BASE_URL` (or configured env) and create a single axios/fetch instance.
- Error handling: Normalize errors into a predictable shape; do not throw raw network errors to UI.
- Retries & timeouts: Implement retry/backoff policies only when justified and expose configurable options.

## 3. SDK Wrapping

- Wrap SDKs: External SDKs must be wrapped by small adapters inside `services/` or `shared/services/`.
- No business logic: Services must not implement high-level business orchestration; that belongs to backend `Service` or frontend `store`/`hooks`.

## 4. Type & Docs

- JSDoc: Document inputs and outputs; prefer small DTO-like shapes rather than free-form objects.
- Return values: Return plain JSON/data objects suitable for consumption by hooks/stores.

## 5. Testing & Mocks

- Unit tests: Mock network calls and assert service behavior.
- Test adapters: Provide test adapters or use MSW for integration tests.

---

Services are the single source-of-truth for network and SDK usage; keep them thin, typed, and testable.
