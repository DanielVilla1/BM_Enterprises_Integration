---
description: "Rules for frontend reusable hooks (React)"
applyTo: "frontend/**/hooks/**/*.{js,jsx,ts,tsx}"
---

# Hooks Folder Rules

Hooks encapsulate reusable logic for components: stateful behaviors, data fetching orchestration, and encapsulated side effects. Hooks must be composable, well-documented, and tested.

## 1. Architecture Rules

- Purpose: Encapsulate reusable behavior (data fetching orchestration, form state, subscriptions) so components remain simple.
- Naming: Prefix hook names with `use` (e.g., `useReservation`, `useTodoList`). Follow naming doctrine.
- AI header & JSDoc: AI-generated/modified hooks must include AI header and JSDoc for parameters and return values.

## 2. Purity & Side-effects

- Side-effects allowed: Hooks may perform side-effects (fetching, subscriptions) but must expose a clean API and cleanup logic.
- No rendering: Hooks must not return JSX or act as components.
- No direct SDK usage: Wrap SDKs in `services/` and call through them inside hooks.

## 3. Type & Return Rules

- JSDoc: Document return shape and types in JSDoc. Prefer explicit object shapes over ambiguous arrays.
- Error handling: Return error and loading states consistently (`{ data, error, loading }`).

## 4. Testing & Performance

- Unit tests: Test hook behavior using React Testing Library hooks utilities or similar.
- Performance: Avoid recreating functions/values unnecessarily; memoize with `useCallback`/`useMemo` where appropriate.

## 5. Consistency Enforcement

- Location: Hooks should live under `frontend/src/hooks/` or per-domain under `frontend/src/modules/<domain>/hooks/`.
- CI checks: Ensure JSDoc presence and exported name prefix `use` in lint rules.

---

Hooks provide composable behavior; keep them typed, documented, and side-effect-aware.
