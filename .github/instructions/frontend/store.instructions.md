---
description: "Rules for frontend stores (global state management)"
applyTo: "frontend/**/store/**/*.{js,ts}"
---

# Store Folder Rules

Stores manage cross-component state. Choose a single library per project (React Context, Redux, or Zustand) and follow explicit state shapes and selectors.

## 1. Architecture Rules

- Purpose: Hold domain state, selectors, and simple reducers/mutators. No UI rendering logic here.
- One store per domain: Avoid mega-stores; prefer domain-specific stores.
- Naming: Store files and exported hooks/selectors must be descriptive.
- AI header & JSDoc: AI-generated/modified store files must include AI header and JSDoc for public selectors/actions.

## 2. State & Mutation Rules

- Explicit shape: Define explicit state interfaces in JSDoc and initialize with a clear default shape.
- No business branching: Stores should not contain complex business rules; keep them for derived state and simple transformations.
- Immutable updates: Use immutable patterns or library helpers to avoid accidental mutation.

## 3. API & Side-effects

- No API calls inside stores unless domain-global and centralized. Prefer hooks or services for fetching and then update stores.
- Thunks/effects: If using middleware (Redux Thunk/Saga) keep side-effects centralized and testable.

## 4. Selectors & Performance

- Selectors: Provide memoized selectors for derived data and avoid expensive recomputation in render paths.
- Subscriptions: Keep subscription zones small to avoid re-renders.

## 5. Testing & Consistency

- Unit tests: Test selectors and state transitions.
- CI checks: Enforce naming and JSDoc rules for stores.

---

Stores should be explicit, domain-scoped, and free from heavy business orchestration.
