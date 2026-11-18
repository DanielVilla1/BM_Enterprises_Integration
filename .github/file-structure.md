# Project file structure

The [system folder architecture](../docs/architecture.md#repository-folder-architecture) documents the current repository tree, file ownership and root-file exceptions. Keep it current when modules move.

## Backend placement

Application code belongs in `src/backend/src/`, within its established layer:

- `Controller/`: HTTP input, authorization dependencies and DTO mapping.
- `DTO/`: validated request and response shapes.
- `Service/`: business workflow, ownership, audit and transaction boundaries.
- `Entity/`: framework-independent domain values and rules.
- `Contract/`: interfaces for persistence and external systems.
- `Repository/`: ORM models, queries and unit of work.
- `Infrastructure/`: Clerk, Supabase and imaging adapters.
- `Data/`: permission seed data.

Keep migrations in `src/backend/migrations/`, operator commands in `src/backend/scripts/`, and tests in `src/backend/tests/`. The app entry point, Python configuration, migration configuration and dependency files stay in `src/backend/`. Shared dependency wiring and request controls stay at `src/backend/src/`.

No database queries in controllers, business approvals in repositories, vendor SDKs in entities, or ORM entities in public API responses.

## Frontend placement

- `src/frontend/src/pages/`: compose hooks and presentational screens.
- `src/frontend/src/components/<feature>/`: UI owned by account, administration, clients, dashboard, dispatch, fleet, orders, trips, finance or reports.
- `src/frontend/src/hooks/`: loading/action orchestration and lifecycle.
- `src/frontend/src/services/`: feature API clients.
- `src/frontend/src/store/`: Zustand state by feature.
- `src/frontend/src/shared/components/`: reusable UI, application shell and sign-in layout.
- `src/frontend/src/shared/services/`: HTTP, Clerk and shared asynchronous loaders.
- `src/frontend/src/shared/utils/`: pure shared helpers.
- `src/frontend/src/shared/mockups/`: fictional design-preview data.
- `src/frontend/tests/unit/` and `src/frontend/tests/components/`: regression tests outside production source.
- `src/frontend/design-preview/`: the sample-data preview harness.

Components use props and callbacks; network calls go through services. Shared logic belongs in `shared/`. Keep feature names descriptive across hooks, stores and services. Follow the same placement convention for every new feature.

## Repository boundaries

Keep documentation in `docs/`, role manuals in `docs/runbooks/roles/`, and historical documents in `docs/archive/`. Write diagrams as fenced Mermaid blocks inside Markdown.

Only repository-wide files belong at the root: README, Compose, shared environment template, Git/editor/formatting configuration. Each app owns its dependency manifests, Dockerfile and tooling configuration. Framework entry files remain at their expected app locations.

When moving files, update all imports, preview harnesses, tests and documentation together; remove old copies. Do not introduce unrelated endpoint folders or duplicate layer hierarchies. Private workstation data, credentials, caches, virtual environments, installed dependencies and build output are ignored and are not source files.
