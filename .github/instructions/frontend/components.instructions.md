---
description: "Rules for frontend presentational components (React)"
applyTo: "frontend/**/components/**/*.{js,jsx,ts,tsx}"
---

# Components Folder Rules

Components are presentational UI units. They should be pure UI: receive props, render UI, and emit events via callbacks. Components must not perform API calls or implement business rules.

## 1. Architecture Rules

- Purpose: Presentational rendering and composition only. Keep components small and focused (single responsibility).
- Naming: Files and component names must be descriptive and follow naming doctrine from `.github/copilot-instructions.md`.
- AI header & JSDoc: Any AI-generated or AI-modified component file must include an AI header comment and JSDoc for exported components and props.

## 2. Props & State Rules

- Props: Validate via PropTypes or JSDoc types. Prefer explicit prop shapes over free-form objects.
- Local state: Keep local UI state only (form inputs, toggle UI state). Do not keep domain/business state in components.
- Lifting state: Lift domain state to stores/hooks and use props or hooks to consume.

## 3. Side-effects & Lifecycle

- No API calls: Components must not call services directly. Use hooks or services for data fetching.
- Effects: Use effects (`useEffect`) only for UI lifecycle concerns; keep effects idempotent and well-cleaned-up.

## 4. Styling & Accessibility

- Styles: Prefer CSS modules/Tailwind or design-system tokens. Keep styles isolated.
- Accessibility: Add `aria-*` attributes, semantic HTML, and focus management for interactive components.

## 5. Testing & Docs

- Unit tests: Components must have unit tests for rendering and basic interactions.
- Storybook: Prefer story examples for complex components.
- Documentation: Exported components must have concise JSDoc describing props and usage.

---

Components are presentation-only: typed, documented, accessible, and testable.
