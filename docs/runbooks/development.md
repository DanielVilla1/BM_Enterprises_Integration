# Developer guide

**Sprint 5–6 branch update:** Expenses, earnings, payroll, advances, billing and reports now have persistent services and screens on `sprint-5-6-finance-and-reporting`. See [the current handoff](sprint-5-6.md) for behavior, role access, migrations, demonstration data and verification. Section 13 lists the remaining release gates.

[Handbook](../README.md) · [System structure](../architecture.md) · [Verification](verification.md)

**Need to run it?** Start at [Local setup](#4-local-setup). **Changing a feature?** Start at [Architecture](#6-architecture-rules-enforced-by-review-partly-by-tests) and [feature checklist](#11-how-to-add-a-feature-checklist).

**Development cycle: read rule, change correct layer, test access and business rules, update docs, review.**

```mermaid
flowchart LR
    accTitle: Change a feature without drifting
    accDescr: Follow business rule to implementation, regression checks and updated documentation before review.
    rule["Read rule"]:::action --> code["Change correct layer"]:::action
    code --> check["Test rule + access"]:::action
    check --> docs["Update guide + contract"]:::action
    docs --> review["Review on feature branch"]:::done
    classDef action fill:#e8f1ff,stroke:#2563eb,color:#163566,stroke-width:2px
    classDef done fill:#e7f6ec,stroke:#208448,color:#16452a,stroke-width:2px
```

| Common job                   | Jump to                                 |
| ---------------------------- | --------------------------------------- |
| Start frontend and API       | [Local setup](#4-local-setup)           |
| Configure credentials/ports  | [Configuration](#5-configuration)       |
| Understand permission checks | [Permission model](#7-permission-model) |
| Run the checks               | [Tests](#8-tests)                       |
| Find unfinished work         | [Left to build](#13-left-to-build)      |

<details>
<summary><strong>Source specification and handbook context</strong></summary>

**Handbook:** [documentation index](../README.md), [role manuals](roles/README.md), [feature procedures](user-guide.md), [service workflow](service-workflow.md), [system structure](../architecture.md), [taxonomy](../taxonomy.md) and [verification record](verification.md). Read these with this guide. On 18 November 2026 the user authorized filling missing financial decisions; [Financial working policies v1](../decisions/financial-policies.md) defines D4–D10 development defaults. The Sprint 5–6 implementation now persists the financial workflows; production release remains gated.

Handover guide for the next developer. It says what exists, how it is built, how to run and extend it, what is not verified, and what is left. Read it with the **Consolidated Developer Specification (9 Nov 2026)**, which is the source of business rules. (It is a Word file kept by the team; it is not committed here. Where it disagrees with the older [archived proposal](../archive/architecture-proposal.md), the specification wins.)

</details>

<details>
<summary><strong>Editing handbook diagrams</strong></summary>

Diagrams are fenced `mermaid` blocks inside the Markdown page that explains them. Edit the block directly, then check the page in a Mermaid-capable Markdown preview. There are no exported diagram images, separate `.mmd` source files or rendering scripts to maintain.

Keep diagrams short and use explicit action/state labels. Blue means action, green completion, amber a check, red a blocked action and dashed purple a planned feature. Preserve `accTitle` and `accDescr` when editing existing diagrams.

For file placement, use the visible [repository folder architecture](../architecture.md#repository-folder-architecture), including its root-file exceptions and examples for new modules.

</details>

## 1. Status

**Implemented on this branch:** operational modules, finance and reports. External production release gates remain; see [Sprint 5–6](sprint-5-6.md).

<details>
<summary><strong>Technical reference and caveats</strong></summary>

| Sprint | Scope                                                                        | Current branch status                                                                                                                              |
| ------ | ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1–4    | Identity, records, dispatch, OR and completion                               | Persistent implementation retained.                                                                                                                |
| 5      | Expenses, charges/rates, earnings, payroll/adjustments, advances and billing | Core persistent workflows implemented; deductions disabled by default; see policy coverage for correction/reconciliation limits.                   |
| 6      | Reports, security checks, load test and installation support                 | Role-scoped reports, automated checks and public offline help implemented; live staging/mobile/restore and production approval remain outstanding. |

The [verification record](verification.md) distinguishes current Sprint 5–6 checks from historical counts: the complete PostgreSQL/Python 3.12 suite recorded 258 passes and one opt-in load skip; the separate 300-request load run passed; 78 frontend tests, lint, formatting, build and production dependency audits passed. The application contract also passed on the local Python 3.14 environment after normalizing HTTP error descriptions. These are developer-run checks, not QA or production sign-off.

Docker development containers were rebuilt/restarted, schema revision `0006` applied, and Owner access and fictional presentation records checked in the running app. Live Supabase behavior, real-device/inbox journeys and restore timing remain separate checks.

</details>

## 2. Branches and pull request targets

**Work on a feature branch; explicitly target `main`.** The original stacked sprint merges have already been consolidated.

<details>
<summary><strong>Technical reference and caveats</strong></summary>

Sprints 1–4 are consolidated into `main`, preserving all sprint commits and the merge commits from PRs #1–#4. The original PRs were stacked: PR #1 targeted `main`, but PRs #2–#4 targeted the preceding sprint branch. Merging those PRs did not carry the later sprints into `main`; the consolidation merge brings all four branch histories together.

The current work is on `sprint-5-6-finance-and-reporting` and remains unmerged. Inspect the working tree before switching branches; preserve uncommitted work. Do not merge or publish this branch without the requested review and authorization.

```bash
git branch --show-current
git status --short
# Switch only when your current work is safely preserved:
git switch sprint-5-6-finance-and-reporting
```

For a future independent feature, create a separate branch from the reviewed base. A review request should explicitly target the intended base; opening one is a separate action from local implementation.

For future stacked PRs, merge the oldest first, then explicitly retarget the next PR to `main` before merging it. Verify the base branch in GitHub; do not depend on automatic retargeting or branch deletion.

CI runs the PostgreSQL migration and hardening tests. Check the workflow result on `main` after integration; see section 12 for checks that still need a live environment.

The spec requires a named human reviewer for any change to authentication, authorization, payroll, billing, uploads or migrations (decision D13). Fill in the PR template checkboxes.

</details>

## 3. Repository map

See the [folder/layer architecture](../architecture.md#repository-folder-architecture) for the current tree and file placement rules.

**Backend:** layered business services. **Frontend:** screens, hooks, stores and API services.

<details>
<summary><strong>Technical reference and caveats</strong></summary>

```
src/backend/
  main.py                    app factory: CORS, body cap, problem+json, routers
  alembic.ini, migrations/   Alembic 0001–0006; includes finance schema snapshot and grant/history upgrade
  pyproject.toml             ruff, black, pytest config
  requirements*.txt          pinned runtime / dev dependencies
  openapi.snapshot.json      committed API contract (a test fails if it drifts)
  scripts/                   bootstrap_owner, reconcile_clerk, export_openapi, seed_presentation
  src/
    Entity/                  domain values and rules (no framework imports)
    Contract/                Protocol interfaces (ports) for repositories and adapters
    Repository/              SQLAlchemy: orm_models.py, finance_models.py + domain repositories; returns Entities, never ORM rows
    Service/                 business rules, transactions, audit
    DTO/                     Pydantic request/response models
    Controller/              FastAPI routers (thin)
    Infrastructure/          external systems: Clerk, Supabase Storage, Pillow
    Data/permission_matrix.json   the permission matrix (seed data)
    providers.py             dependency wiring, authentication, require_capability
    problem_details.py       RFC 9457 errors + trace id middleware
    request_limits.py        global request body cap
    rate_limiter.py          in-process sliding window
    config.py                settings from environment
  tests/                     see section 8
src/frontend/src/
  pages/                     screen containers joining hooks to UI
  components/<feature>/      feature UI (props in, callbacks out)
  shared/components/         reusable UI, shell and sign-in layout
  hooks/                     data loading and actions (call services, write stores)
  store/                     Zustand, one store per domain (createCollectionStore)
  services/                  API clients per domain
  shared/services/           httpClient (axios), Clerk wrapper (the only module touching the SDK)
  shared/utils/              pure helpers: navigation, dispatch rules, forms, problem details
src/frontend/tests/              unit/ and components/ regression suites
.github/                     CI workflow, PR template, Copilot governance and per-layer rules
docs/runbooks/development.md      this file
compose.yml                  Postgres, backend, frontend, pgAdmin (development stack verified)
```

</details>

## 4. Local setup

**Frontend:** `http://localhost:5173` · **FastAPI docs:** `http://localhost:8000/api/v1/docs`.

**Browser frontend at port 5173, FastAPI at port 8000 and configured backing services.**

```mermaid
flowchart TB
    accTitle: Open the app and API locally
    accDescr: Frontend port 5173 proxies API requests to FastAPI port 8000; PostgreSQL uses the configured database connection.
    browser["YOUR BROWSER"]:::done --> ui["Frontend · localhost:5173"]:::action
    browser --> docs["API docs · localhost:8000/api/v1/docs"]:::action
    ui -->|/api/v1 proxy| api["FastAPI · port 8000"]:::action
    docs --> api
    api --> db["PostgreSQL · configured database"]:::action
    api --> storage["Private Supabase files"]:::action
    clerk["Clerk sign-in"]:::action --> browser
    classDef action fill:#e8f1ff,stroke:#2563eb,color:#163566,stroke-width:2px
    classDef done fill:#e7f6ec,stroke:#208448,color:#16452a,stroke-width:2px
```

<details>
<summary><strong>Commands and setup instructions</strong></summary>

Requirements: Python 3.12, Node 20+ (22 in CI), Git. Docker is optional (and untested).

**Backend** (from `src/backend/`; on Linux/macOS use `.venv/bin/python`):

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt
.venv/Scripts/python -m pytest -q
.venv/Scripts/python -m ruff check . && .venv/Scripts/python -m black --check .
```

**Run the API** (from the repo root, with a populated `.env`; see `.env.example`):

```bash
src/backend/.venv/Scripts/python tools/scripts/backend.py alembic -c src/backend/alembic.ini upgrade head
src/backend/.venv/Scripts/python tools/scripts/backend.py backend.scripts.bootstrap_owner --name "Name" --email you@example.com --clerk-user-id user_xxx
src/backend/.venv/Scripts/python tools/scripts/backend.py uvicorn backend.main:app --reload
```

Run the tracked `tools/scripts/backend.py` launcher from the repository root; it invokes the requested module with `src/` on `PYTHONPATH`. A bare `python -m backend.scripts...` needs equivalent module-path/environment setup. Docs are at `/api/v1/docs` when `ENABLE_API_DOCS=true`.

**Frontend** (from `src/frontend/`): `npm ci`, `npm run dev`, `npm run lint`, `npm test`, `npm run build`.
`VITE_CLERK_PUBLISHABLE_KEY` **must be set at build time**; with it empty, Vite folds the check away and drops the whole app from the bundle.

For local Vite development, create `src/frontend/.env` with the public settings `VITE_CLERK_PUBLISHABLE_KEY`, `VITE_API_BASE_URL` and optional `VITE_PUBLIC_FRONTEND_URL`; Vite does not load the repository-root `.env` with the current configuration. Keep backend secrets in the root file. Docker Compose supplies the frontend variables through the container environment instead.

To share the local demo through one ngrok URL, set `VITE_API_BASE_URL=` and `VITE_PUBLIC_FRONTEND_URL=https://YOUR-DEV-DOMAIN.ngrok-free.dev` in the root and frontend environment files. Keep FastAPI on port 8000 and Vite on port 5173, then run `ngrok http 5173 --url https://YOUR-DEV-DOMAIN.ngrok-free.dev`. Vite serves the frontend at `/` and proxies `/api/v1` to FastAPI, so API calls and `/api/v1/webhooks/clerk` use the same public origin. Existing Clerk webhook URLs remain valid when the ngrok domain stays the same.

Add that exact public origin to the backend's comma-separated `CORS_ALLOWED_ORIGINS` and `CLERK_AUTHORIZED_PARTIES`, preserving `http://localhost:5173`, then restart both servers. Vite reads the exact public hostname from `VITE_PUBLIC_FRONTEND_URL`; do not use an unrestricted hostname allowlist. The demo remains available while the PC, local services and ngrok agent are running. Any workstation-specific tunnel helper is local-only; the tracked commands above are the supported starting point.

Authentication uses Clerk Core 3 (`@clerk/react` 6) and `<Show when="signed-in">` / `<Show when="signed-out">` gates. Run `npm ci` after pulling SDK updates and restart Vite. The deprecated `@clerk/clerk-react` 5 package can be rejected by Clerk's minimum-version protection.

Use provisioned Clerk development/staging accounts according to that instance’s testing configuration. Credentials and real inbox codes are never stored in tracked documentation. Presentation seeding creates unlinked fictional employee records, not Clerk users or login credentials.

**Accounts you need:** a Clerk application (dev instance), a Supabase project (dev, not Free in production) with a **private** bucket named `delivery-documents`. Use fake data and staging keys only. Never commit `.env`.

</details>

## 5. Configuration

**Secrets stay server-side.** Copy configuration deliberately; never commit `.env`.

<details>
<summary><strong>Technical reference and caveats</strong></summary>

All settings are environment variables read by `src/config.py` (`.env.example` lists them).

| Variable                                                                            | Purpose                                                                          |
| ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `DATABASE_URL`                                                                      | SQLAlchemy URL (`sqlite:///./dev.db` default; Postgres in real use)              |
| `CORS_ALLOWED_ORIGINS`                                                              | comma list; no wildcard                                                          |
| `ENABLE_API_DOCS`                                                                   | serve `/api/v1/docs` and `/api/v1/openapi.json` (decide for production, spec 11) |
| `CLERK_ISSUER`, `CLERK_JWKS_URL`, `CLERK_AUTHORIZED_PARTIES`, `CLERK_AUDIENCE`      | local JWT verification                                                           |
| `CLERK_WEBHOOK_SECRET`                                                              | webhook signature (`whsec_...`)                                                  |
| `CLERK_SECRET_KEY`                                                                  | used only by the reconciliation job                                              |
| `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_BUCKET`, `SIGNED_URL_TTL_SECONDS` | private document storage                                                         |
| `HELPER_OR_UPLOAD_ENABLED`                                                          | whether helpers may upload ORs (open decision D1)                                |
| `RATE_LIMIT_FAILED_AUTH_PER_MINUTE`, `RATE_LIMIT_WEBHOOK_PER_MINUTE`                | throttles                                                                        |
| `TEST_DATABASE_URL`                                                                 | run the test suite on PostgreSQL                                                 |
| `VITE_CLERK_PUBLISHABLE_KEY`, `VITE_API_BASE_URL`                                   | frontend                                                                         |

`PAYROLL_DEDUCTIONS_ENABLED=false` is the default and keeps ordinary personal deductions/debit adjustments disabled pending the D16 decision. It does not authorize real payroll use or replace legal/QA approval. The API/user/upload rate-budget variables are all documented in [security hardening](../decisions/security-hardening.md#request-budgets).

To load fictional records, explicitly run `docker compose exec -T backend python -m backend.scripts.seed_presentation --presentation` in the local development stack. The command refuses production/remote destinations, does not run during migrations, and does not create sign-in accounts. See [presentation setup](sprint-5-6.md#presentation-dataset).

</details>

## 6. Architecture rules (enforced by review, partly by tests)

**Controllers handle HTTP. Services enforce rules. Repositories handle SQL.**

<details>
<summary><strong>Technical reference and caveats</strong></summary>

These come from `.github/copilot-instructions.md` and the per-layer files in `.github/instructions/`. Follow them.

- **Layers:** Controller (HTTP only) → Service (rules, transactions, audit) → Repository (SQL only) → Entity. Controllers never import ORM, sessions or SDKs. Responses are always DTOs; entities and ORM rows are never returned.
- **Wiring:** Services receive repository _Contracts_; `providers.py` builds them per request around one session.
- **Transactions:** repositories only `flush`; a service commits each business transaction after its checks. Operational completion is one transaction; its subsequent automatic earnings calculation is separate, so a financial failure cannot undo completion. The operator-only presentation seed commits its own seed transaction.
- **Errors:** services raise `BusinessRuleError(status, code, title, detail[, headers, extensions])`. Handlers return `application/problem+json` (RFC 9457) with a `trace_id`. Never put stack traces, SQL or paths in a response. `extensions` add fields such as `blocking_trip_ids`.
- **Naming and comments:** variables 4+ characters, functions 6+; forbidden names `data item obj val thing temp test misc`. Every source file starts with the `# ===== AI GENERATED: <name> =====` header (max 8 lines) describing purpose, inputs, returns, flow. JS uses JSDoc on every exported function (no TypeScript).
- **Frontend:** no API calls or business rules in components; API only through `services/`; state only through `store/`; role-based UI hints come from the backend's `/me` capabilities and only hide links (the backend still decides).
- **Input DTOs** set `extra="forbid"`. PATCH bodies extend `PartialUpdateRequest` (rejects empty bodies and null on required fields).
- **Units and formats:** UUID ids, JSON snake_case, UTC timestamps, weights as `Decimal` metric tons (JSON numbers), Philippine business date = UTC+8 (`Entity/clock.py`). Money inputs use decimal strings, calculations use `Decimal`, and persistence uses fixed-precision numeric columns; never calculate money with binary floats.
- **Audit:** every mutation writes an audit row with action, actor, entity and a trace id. ordinary profile audits record changed field names rather than private values. Financial command audit details retain the validated financial request/reference for accountability and are restricted to Owner audit access. Do not place credentials, JWTs, identity documents or unrelated personal data in reasons/evidence references.
- **Pagination:** list endpoints cap `limit` at 100.

</details>

## 7. Permission model

**Backend-confirmed capabilities + ownership + state.** Hiding a button is not authorization.

**Authentication, activation, permission and record/state gates.**

```mermaid
flowchart LR
    accTitle: Four checks before an action
    accDescr: Sign-in, active employee, capability, and record/state checks all must pass.
    login["Valid sign-in"]:::action --> active["Active linked employee"]:::action
    active --> grant["Capability granted"]:::action
    grant --> record["Correct record + allowed state"]:::action
    record --> yes["Action allowed"]:::done
    classDef action fill:#e8f1ff,stroke:#2563eb,color:#163566,stroke-width:2px
    classDef done fill:#e7f6ec,stroke:#208448,color:#16452a,stroke-width:2px
```

<details>
<summary><strong>Technical reference and caveats</strong></summary>

The matrix (spec section 3.4) is **data**: `src/Data/permission_matrix.json`, seeded into `role_permissions`. Seven roles: OWNER, DISPATCHER, FLEET_MANAGER, DRIVER, HELPER, HR_PAYROLL, ACCOUNTING. Levels: FULL, VIEW, LTD (limited fields), OWN (own records only). A user with several roles gets the strongest level per capability.

Protect every route with a dependency:

```python
access: AccessContext = Depends(require_capability("truck.manage", AccessLevel.FULL))      # minimum level
access: AccessContext = Depends(require_capability("trip.progress", only_levels=(AccessLevel.OWN,)))  # exact levels
```

- Object-level rules (own records, crew membership) live in the **service**; return **404**, not 403, so existence does not leak.
- `test_permission_matrix.py` **fails** if a route has no capability (public/authenticated-only routes are an explicit allowlist in that file) and calls every route as every role, comparing with the stored matrix. New routes are covered automatically.
- **Adding or changing a matrix cell:** edit the JSON _and_ ship an **idempotent** Alembic migration that inserts missing rows (see `0003`). Fresh databases get the JSON via `0001`; existing ones get the migration. Never edit an applied migration.
- Cells marked ‡ in the spec were inferred by its author and need BM's confirmation. One was added by this build: `trip.assignment_view` (the matrix gave helpers no way to see their own assignments, but spec 3.2 requires it). Clients reuse `delivery_order.manage`.
- Forbidden role pairs (spec 3.2) are enforced on role assignment and need an Owner reason to override (audited). No-self-approval is enforced for financial approvals, including combined roles and prior expense contributors.

</details>

## 8. Tests

**Python 3.12 is the contract baseline.** PostgreSQL tests must use a scratch database.

<details>
<summary><strong>Technical reference and caveats</strong></summary>

From `src/backend/`, run `.venv/Scripts/python -m pytest -q`. Runtime depends on the database/environment; PostgreSQL recreates its scratch schema per test. Files:

| File                                                                              | Covers                                                                                                    |
| --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `test_permission_matrix`                                                          | deny-by-default, every role x route                                                                       |
| `test_authentication`, `test_webhooks`, `test_reconciliation`, `test_rate_limits` | Clerk token/webhook/reconciliation interface and throttles                                                |
| `test_employees`, `test_fleet`, `test_delivery_orders`                            | records, ownership, field visibility, audit                                                               |
| `test_dispatch_assignment`, `test_dispatch_flow`                                  | capacity, crew, license, double booking, OR block, crew change, replacement                               |
| `test_or_documents`, `test_or_completion`, `test_storage_adapters`                | upload validation, metadata stripping, storage, signed URLs, confirmation, idempotency, FP-02, correction |
| `test_problem_details`, `test_platform`, `test_contract_snapshot`                 | error format, migrations vs models, seed, audit immutability, OpenAPI                                     |
| `test_postgres_hardening`                                                         | RLS, anon/authenticated lockdown, audit triggers (**only with `TEST_DATABASE_URL`**)                      |

Financial regressions also live in `test_finance_workflows.py`, `test_financial_migration.py`, `test_presentation_and_financial_controls.py` and `test_financial_readiness_and_query_budget.py`. The opt-in `test_sprint6_load.py` uses `RUN_LOAD_TESTS=1`; it exercises 30 completed trips, 20 users and 300 paced report reads, with no external identity/storage traffic. `tools/scripts/verify_postgres.py` creates and removes a local scratch database; use an isolated development server/account with the required test-database/role privileges, never the operational database. [Measured results](sprint-5-6-evidence/verification.md) retain their environment and limitations.

Helpers: `tests/conftest.py` (migrated SQLite per test, signed fake Clerk tokens, signed webhooks, `FakeObjectStorage`, `employees` factory), `dispatch_support.py` (`World`: fake orders/trucks/crews, `delivered_trip()`), `image_support.py` (real JPEG/PNG with metadata). Tests use **fake data only**.

Run on Postgres: `TEST_DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/bm_test python -m pytest -q` (it drops and recreates the `public` schema; use a scratch database). CI does this with a service container.

**Contract test:** after any API change run `src/backend/.venv/Scripts/python tools/scripts/backend.py backend.scripts.export_openapi` (repo root) and commit `src/backend/openapi.snapshot.json`.

SQLite caveats (tests default to SQLite): datetimes come back **naive** (use `as_utc()` in `Service/or_service.py` when comparing); `ALTER` is limited, so migration `0004` uses `batch_alter_table` and re-passes CHECK constraints; row locks (`FOR UPDATE`) are no-ops. Anything touching those needs a Postgres run.

</details>

## 9. What is implemented (domain rules worth knowing)

**Driver receipt completes the trip.** Prior OR restrictions and resource checks still govern the next dispatch.

<details>
<summary><strong>Technical reference and caveats</strong></summary>

**Statuses.** Trip: SCHEDULED → ACCEPTED → CLEARED_FOR_DISPATCH → IN_TRANSIT → DELIVERED_OR_PENDING → OR_UPLOADED → COMPLETED, or FAILED / CANCELLED (spec 4.2). Order: PENDING, PARTIALLY_ASSIGNED, SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED, **derived from trips** (`Entity/dispatch.py: derive_order_status`). Truck: AVAILABLE, ASSIGNED, IN_TRANSIT, MAINTENANCE, derived from open trips and never overriding MAINTENANCE (`Service/trip_state_synchronizer.py`).

**Assignment** (`Service/trip_service.py`): load <= truck capacity (`CAPACITY_EXCEEDED`), load <= unassigned order weight, truck active and not in maintenance, one driver + one or two distinct helpers with the right roles and active, driver license present and not expired _on the trip date_, and no double booking.

**OR restriction (spec 5.2).** A resource holding a trip before OR upload cannot take another. After the signed OR is uploaded it can take **one** advance reservation, but the next trip cannot be cleared or depart until the driver confirms the previous OR was received. The error is `DISPATCH_BLOCKED` with the spec message and `blocking_trip_ids`. Resource conflicts, current truck capacity/condition, crew activity/roles and driver license validity are re-checked at both clearance and departure.

**Completion** (`Service/or_service.py`): only the assigned driver confirms (no dispatcher approval); requires a stored signed OR and an `Idempotency-Key`; one transaction updates the trip, truck/crew restriction, order progress and audit. Repeats with the same key are no-ops. The Owner may reopen a confirmation unless a later trip with the same truck/crew has departed, even if that later trip is now closed or has replaced the truck.

**Uploads:** JPEG/PNG only, judged by content; re-encoded to strip EXIF/GPS; 5 MB (route cap plus global body cap); storage path is server-generated; object is stored **before** the DB transaction and deleted if the commit fails; reads use signed URLs (120 s) issued after the access check.

**Defaults used where BM has not decided** (change them deliberately):
D2 crew locked once the truck departs; D3 cancel only before departure, fail only after, earnings treatment deferred; D15 no override of the dispatch block; D5 fixed charges are finalized per trip by Owner/Accounting under [financial working policies](../decisions/financial-policies.md); no client rate-card module; D14 no outbox; D1 helper upload off (`HELPER_OR_UPLOAD_ENABLED`).

</details>

## 10. API surface

**Contract:** `src/backend/openapi.snapshot.json`: **69 paths / 81 operations**, including **31 finance paths / 32 finance operations**. Counts come from the committed snapshot; all paths use `/api/v1`.

<details>
<summary><strong>Technical reference and caveats</strong></summary>

Auth: bearer Clerk session token. Source of truth: `src/backend/openapi.snapshot.json` or `/api/v1/docs`.

| Area            | Routes                                                                                                                                                                                                             |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Public          | `GET /health`, `POST /webhooks/clerk` (signature only)                                                                                                                                                             |
| Account         | `GET /me` (roles and capability levels)                                                                                                                                                                            |
| Employees       | `GET/POST /employees`, `GET/PATCH /employees/{id}`, `POST .../activate`, `POST .../deactivate`, `PUT .../roles`, `PUT .../identity`, `GET/PUT .../driver-license`                                                  |
| Admin           | `GET /permission-matrix`, `GET /audit-logs` (Owner)                                                                                                                                                                |
| Clients, trucks | `/clients`, `/trucks` (list, create, get, patch), `/trucks/{id}/maintenance` (+ `/complete`)                                                                                                                       |
| Orders          | `/delivery-orders` (list, create, get, patch), `.../cancel`, `POST .../{id}/trips` (assign)                                                                                                                        |
| Dispatch        | `GET /dispatch/resources`, `GET /trips`, `GET /trips/assigned`, `GET /trips/{id}`; `POST` actions: `accept`, `clear-dispatch`, `depart`, `deliver`, `cancel`, `fail`; `PUT .../crew`, `POST .../truck-replacement` |
| OR              | `POST/GET .../or-documents`, `GET .../or-documents/{id}/url`, `POST .../confirm-receipt`, `POST .../receipt-correction`                                                                                            |

| Finance and reports | `/finance/expenses`, `/payroll`, `/advances`, `/billing`, `/reports`; per-trip expense/charge/earning/hold commands; rates, adjustments, payrolls/statements, delegations, invoices/collections and authorized presentation documents. See the [complete financial route/capability table](../architecture.md#financial-api-reference). |

</details>

## 11. How to add a feature (checklist)

**Build the domain and backend rules before wiring the screen.** Include regression tests and documentation.

<details>
<summary><strong>Technical reference and caveats</strong></summary>

1. Read the spec section; if a rule is marked Open/Recommended, confirm with BM or put it behind a setting.
2. **Entity** (`Entity/`), **ORM** (`Repository/orm_models.py` or `Repository/finance_models.py`), **migration** (new file, never edit applied ones; include RLS lock-down for new tables, copy the lockdown pattern in `0002`–`0005`).
3. **Contract** + **Repository** (return entities; `flush` only).
4. **Service**: rules, audit, one `commit()`. Raise `BusinessRuleError` with a stable code.
5. **DTOs**, **Controller** with `require_capability(...)`, register the router in `main.py`, add the service factory to `providers.py`.
6. Matrix: add the capability (JSON + idempotent migration) if new.
7. **Tests first for security rules** (spec section 12), including a Postgres-sensitive check if you rely on locks or constraints.
8. `ruff`, `black`, `pytest`, regenerate the OpenAPI snapshot, update README/this guide.
9. Frontend: service → store → hook → component → add to `NAVIGATION_ITEMS` (`shared/utils/navigation.js`) with its capability.
10. PR: fill the template (AI-assisted checkbox, verification line, security reviewer, dependency review note for any new package).

</details>

## 12. Not verified (do these first)

**Local tests do not certify live storage, mobile, restore time or production deployment.**

<details>
<summary><strong>Technical reference and caveats</strong></summary>

- **CI/database environment:** the tracked workflow uses PostgreSQL 16. Sprint 5–6 local results are recorded separately in [verification](verification.md); older PostgreSQL 18.2 observations are historical. Check the actual CI result for the reviewed commit; no production database version or deployment is certified by local tests.
- **Spec proof of concept (section 12 of the spec):** Clerk token lifetime and outage behaviour (tokens last about 60 s), webhook bad-signature then double replay, Supabase public key cannot read or write any table, backup restore time (the 4 h target is unproven), 5 MB phone upload on mobile data and signed URL expiry.
- **Live Supabase Storage:** `Infrastructure/Supabase/supabase_object_storage.py` is tested against a mock only; confirm upload, signing and delete against a real project.
- **Browser check:** desktop Chrome sign-in and the workspace were verified for all seven roles using the live Clerk development instance and test-email aliases. Mobile behavior and real-inbox verification still need testing.
- **Docker development:** the backend/frontend containers were rebuilt and restarted, migrations through `0006` applied, and the running Owner workspaces checked against stored grants. This does not certify production deployment.
- **Dependencies:** Pillow and python-multipart were added in Sprint 4; the frontend Clerk SDK was migrated to `@clerk/react` 6.18.8 with Core 3 authentication gates after the old SDK was blocked at sign-in. That SDK upgrade had its own historical verification; current branch results are in the verification record. The spec asks for a human dependency review note.

</details>

## 13. Left to build

The persistent Sprint 5 finance modules and Sprint 6 reports are implemented on this branch. Read [the current handoff](sprint-5-6.md) for the complete behavior and role matrix.

Remaining release gates: named human/security review before merge; D16 review before real payroll/deduction use; live staging and Supabase/mobile checks; hosting, MFA/recovery, HTTPS and incident procedure; backup/reconciliation schedules and a timed restore drill. Refund/credit reconciliation and already-paid payroll corrections need their own designed workflow. Driver installation support includes a manifest and public offline help, without an offline action queue.

## 13a. Frontend design system (daisyUI + Tailwind)

**Reuse the theme and shared UI components.** Sample-data screens remain visibly labeled as previews.

<details>
<summary><strong>Technical reference and caveats</strong></summary>

- **Stack:** Tailwind 4 with **daisyUI 5.8.1** (pinned). Two custom themes live in `src/frontend/src/index.css`: `bm-dark` (bold dark navy + orange, default) and `bm-light`. The shell's sun/moon button toggles them and remembers the choice (`shared/utils/theme.js`, `store/themeStore.js`).
- **Shell:** `shared/components/AppShell.jsx` is a responsive frame: sidebar on large screens, slide-in menu plus a bottom dock on phones. Pages, their groups and the capability each needs are declared once in `shared/utils/navigation.js`; the current financial/report entries have no `preview: true` marker and no "Soon" badge. Read and write capabilities remain separate.
- **Building blocks** (all pure components): `PageHeader`, `StatCard`, `StatusBadge` (labels and colours from `shared/utils/statusLabels.js`), `FilterTabs`, `SearchField`, `FormField`, `ModalDialog`, `ReasonDialog`, `RowMenu`, `Toast` (+ `hooks/useToast`), `EmptyState`, `ListSkeleton`, `ErrorNotice`, `Icon` (inline SVGs, no icon package).
- **Persistent screens:** Expenses, Payroll, Cash advances, Billing, Reports, Dashboard, Dispatch board (assign, clear, change crew, replace truck, cancel, fail, correct), Delivery orders (edit/cancel), Clients, Fleet (edit, maintenance history), My trips, People (roles, sign-in link, activation, driver licenses), Audit log, Permissions, My account. Page containers are in `src/pages/AppPages.jsx`; `src/App.jsx` is the root.
- **Design-only reference:** `components/finance/*Preview.jsx` and `components/reports/ReportsPreview.jsx` remain isolated to `/preview.html`. Signed-in finance pages use the persistent panels through `pages/FinancePage.jsx`.
- **Design preview page:** run `npm run dev` and open `http://localhost:5173/preview.html`. It renders the real shell and every screen with sample data (no Clerk or backend), with role and state pickers (normal, loading, error, empty). Resize the window to test phones. It lives in `src/frontend/design-preview/` and is not part of the production build.
- **Rules:** keep components pure (props in, callbacks out); put new colours in the theme, not in components; every new status needs a label and tone in `statusLabels.js`; add unit tests for new helpers in `shared/utils/`.

</details>

## 14. Gotchas found while building

**Check these before debugging from scratch.** They record known framework and platform traps.

<details>
<summary><strong>Technical reference and caveats</strong></summary>

- FastAPI **ignores** length/pattern constraints put on a header's `Annotated` type; pass them to `Header(...)` itself (`or_controller.py`).
- `svix`'s `verify()` returns `None` here; the verifier parses the verified raw body itself.
- pydantic-settings tries to JSON-decode list fields; list settings use `NoDecode` and a comma splitter.
- Vite inlines env at build time (see section 4).
- `blocking_trips()` returns one entry per **trip**; per-resource logic must iterate resource rows (this caused a real bug in the availability list).
- On Windows, `pkill` does not exist; stop dev servers from PowerShell. Git prints harmless LF/CRLF warnings.
- Keep new config out of the repo: `.env`, `*.db` and virtualenvs are git-ignored.

</details>
