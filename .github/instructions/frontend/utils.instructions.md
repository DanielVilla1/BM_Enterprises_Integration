---
description: "Rules for frontend utility functions"
applyTo: "frontend/**/utils/**/*.{js,ts}"
---

# Utils Folder Rules

Utils contain pure helper functions, formatters, and validators. They must be side-effect free and easily testable.

## 1. Architecture Rules

- Purpose: Provide small, deterministic functions used across modules.
- Naming: Use descriptive names and keep functions small (single responsibility).
- AI header & JSDoc: AI-generated/modified utils must include AI header and JSDoc types for inputs/outputs.

## 2. Purity & Side-effects

- Pure functions: Avoid mutations and side-effects. If a util needs side-effects (e.g., storage access), place under `shared/` or `services/` and document it.
- Deterministic: Given same inputs, functions must return same output.

## 3. Type & Docs

- JSDoc: Document parameters, return types, and edge cases.
- Small helpers: Prefer composing small helpers rather than large monoliths.

## 4. Testing & Reuse

- Unit tests: Provide tests for edge cases and typical inputs.
- Reuse: Keep utils generic; domain-specific helpers belong in domain modules.

---

Utils are pure, typed, and well-tested helpers for the frontend.
