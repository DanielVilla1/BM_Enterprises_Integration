# BM Enterprises Hauling System

Internal hauling operations with seven business roles, React/Vite, FastAPI, PostgreSQL, Clerk sign-in and private Supabase document storage.

Start with the [documentation index](docs/README.md). Business rules come from **BM Enterprises Consolidated Developer Specification, 9 November 2026**. The [original architecture proposal](docs/archive/architecture-proposal.md) is retained for historical reference only.

## Project layout

```text
docs/
  architecture.md           System architecture and complete folder tree
  decisions/                Working policies and decision records
  runbooks/                 Setup, workflows, verification and role manuals
tools/scripts/              Repository maintenance and launch commands
src/
  backend/                  FastAPI, migrations and backend tests
  frontend/                 React/Vite and frontend tests
```

## Current implementation

Working modules: employees and role administration, clients, delivery orders, fleet and licenses, dispatch, crew changes, truck replacement, signed OR upload, driver receipt confirmation, operational dashboard, permission viewer and audit viewer.

On branch `sprint-5-6-finance-and-reporting`, expenses, earnings, payroll, advances, billing and reports now have persistent APIs and working screens. This work is **unmerged**. Read the [Sprint 5–6 handoff and presentation guide](docs/runbooks/sprint-5-6.md) for role access, fictional DEMO data, verification and remaining release gates. Personal deductions stay disabled pending D16 review.

## Operational sequence

Dispatcher records request → assigns truck, driver and 1–2 helpers → Driver accepts → Dispatcher clears → Driver departs and records delivery → authorized crew uploads signed OR → Driver hands OR to steel company outside the app → Driver confirms receipt → trip completes.

Uploading the signed OR permits one next reservation. The next trip cannot clear or depart until the previous receipt is confirmed. Completion, earnings readiness, billing readiness and payment remain separate states.

## Run locally

Follow [Developer Guide: local setup](docs/runbooks/development.md#4-local-setup) for dependencies, environment configuration, migrations and first-Owner setup. From the repository root:

```powershell
src/backend/.venv/Scripts/python tools/scripts/backend.py uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
cd src/frontend
npm.cmd ci
npm.cmd run dev
```

Open `http://localhost:5173` for the frontend and `http://localhost:8000/api/v1/docs` for FastAPI. PostgreSQL must be running and configuration populated. pgAdmin is a database administration client; ngrok supplies a temporary public tunnel. See the developer guide for public sharing.

## Documentation

- [Feature guide](docs/runbooks/user-guide.md): screen procedures and troubleshooting.
- [Role manuals](docs/runbooks/roles/README.md): duties and instructions for all seven roles.
- [Service workflow](docs/runbooks/service-workflow.md): transitions, exceptions and implementation evidence.
- [System folder architecture](docs/architecture.md#repository-folder-architecture): complete repository tree, file placement, dependencies and conventions.
- [Terminology](docs/taxonomy.md): vocabulary, status names and access levels.
- [Financial policies](docs/decisions/financial-policies.md): working rules and production review gates.
- [Developer guide](docs/runbooks/development.md): configuration, tests, extensions and limitations.

[QA acceptance checklist](docs/runbooks/qa.md) defines the manual tests and sign-off required before deployment/hosting. [Security hardening](docs/decisions/security-hardening.md) records the rate budgets and open release gates.

## Validate changes

From `src/backend/`:

```powershell
.venv/Scripts/python -m ruff check .
.venv/Scripts/python -m black --check .
.venv/Scripts/python -m pytest -q
```

From `src/frontend/`, run `npm.cmd run format:check`, `npm.cmd run lint`, `npm.cmd test` and `npm.cmd run build`. Use Python 3.12 for the committed OpenAPI snapshot. PostgreSQL tests require an isolated scratch database; never point `TEST_DATABASE_URL` at operational data.
