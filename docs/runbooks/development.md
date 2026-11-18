# Developer guide

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

**Handbook:** [documentation index](../README.md), [role manuals](roles/README.md), [feature procedures](user-guide.md), [service workflow](service-workflow.md), [system structure](../architecture.md), [taxonomy](../taxonomy.md) and [verification record](verification.md). Read these with this guide. On 18 November 2026 the user authorized filling missing financial decisions; [Financial working policies v1](../decisions/financial-policies.md) defines D4–D10 for future implementation. It does not turn the financial previews into live features.

Handover guide for the next developer. It says what exists, how it is built, how to run and extend it, what is not verified, and what is left. Read it with the **Consolidated Developer Specification (9 Nov 2026)**, which is the source of business rules. (It is a Word file kept by the team; it is not committed here. Where it disagrees with the older [archived proposal](../archive/architecture-proposal.md), the specification wins.)

</details>

<details>
<summary><strong>Editing handbook diagrams</strong></summary>

Diagrams are fenced `mermaid` blocks inside the Markdown page that explains them. Edit the block directly, then check the page in a Mermaid-capable Markdown preview. There are no exported diagram images, separate `.mmd` source files or rendering scripts to maintain.

Keep diagrams short and use explicit action/state labels. Blue means action, green completion, amber a check, red a blocked action and dashed purple a planned feature. Preserve `accTitle` and `accDescr` when editing existing diagrams.

For file placement, use the visible [repository folder architecture](../architecture.md#repository-folder-architecture), including its root-file exceptions and examples for new modules.

</details>

## 1. Status

**Live:** operational Sprints 1–4 plus dashboard/audit UI. **Preview:** financial modules and expanded reports.

<details>
<summary><strong>Technical reference and caveats</strong></summary>

| Sprint | Scope                                                                                                 | State                                                                                       |
| ------ | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| 1      | Skeleton, Clerk auth, employees, roles, permission matrix, audit, webhook, errors, CI                 | Done                                                                                        |
| 2      | Clients, trucks and maintenance, driver licenses, delivery orders                                     | Done                                                                                        |
| 3      | Dispatch: trips, crew, capacity and license checks, OR dispatch block, crew change, truck replacement | Done                                                                                        |
| 4      | OR upload, private storage, signed URLs, driver receipt confirmation, completion, Owner correction    | Done                                                                                        |
| 5      | Expenses, earnings (8/4 and 6/3/3), payroll, deductions, cash advances, billing                       | **Not started**                                                                             |
| 6      | Reports and dashboards, audit viewer, security review, load test, staging                             | Operational dashboard and audit viewer exist; expanded reports and production checks remain |

Verified during sprint consolidation: 203 backend tests on Python 3.12/SQLite (6 PostgreSQL-only tests skipped), 208 application tests on Python 3.14/PostgreSQL 18.2, 25 frontend tests, backend/frontend lint, backend formatting, frontend production build, and runtime dependency audits. The OpenAPI snapshot was checked on Python 3.12, matching CI; that one test was excluded from the Python 3.14/PostgreSQL run because Python 3.14 changes the generated HTTP 422 description.
Browser follow-up verified live Clerk development sign-in for all seven business roles, including password entry, test-email verification, authenticated `/me` responses and the rendered workspace. The Owner-only permission-matrix endpoint returned 200 for Owner and 403 for the other six roles.
**Still unverified:** Docker, live Supabase, real-inbox verification and mobile UI. See section 12.

</details>

## 2. Branches and pull request targets

**Work on a feature branch; explicitly target `main`.** The original stacked sprint merges have already been consolidated.

<details>
<summary><strong>Technical reference and caveats</strong></summary>

Sprints 1–4 are consolidated into `main`, preserving all sprint commits and the merge commits from PRs #1–#4. The original PRs were stacked: PR #1 targeted `main`, but PRs #2–#4 targeted the preceding sprint branch. Merging those PRs did not carry the later sprints into `main`; the consolidation merge brings all four branch histories together.

Start new work from the latest `main` and explicitly target `main`:

```bash
git switch main
git pull --ff-only origin main
git switch -c sprint-5-payroll-and-billing
gh pr create --base main --head sprint-5-payroll-and-billing --title "Sprint 5: payroll and billing"
```

For future stacked PRs, merge the oldest first, then explicitly retarget the next PR to `main` before merging it. Verify the base branch in GitHub; do not depend on automatic retargeting or branch deletion.

CI runs the PostgreSQL migration and hardening tests. Check the workflow result on `main` after integration; see section 12 for checks that still need a live environment.

The spec requires a named human reviewer for any change to authentication, authorization, payroll, billing, uploads or migrations (decision D13). Fill in the PR template checkboxes.

</details>

## 3. Repository map

See the [complete folder architecture](../architecture.md#repository-folder-architecture) for the current tree and file placement rules.

**Backend:** layered business services. **Frontend:** screens, hooks, stores and API services.

<details>
<summary><strong>Technical reference and caveats</strong></summary>

```
src/backend/
  main.py                    app factory: CORS, body cap, problem+json, routers
  alembic.ini, migrations/   Alembic (0001 identity+audit, 0002 fleet/orders, 0003 trips, 0004 OR/idempotency)
  pyproject.toml             ruff, black, pytest config
  requirements*.txt          pinned runtime / dev dependencies
  openapi.snapshot.json      committed API contract (a test fails if it drifts)
  scripts/                   bootstrap_owner, reconcile_clerk, export_openapi
  src/
    Entity/                  domain values and rules (no framework imports)
    Contract/                Protocol interfaces (ports) for repositories and adapters
    Repository/              SQLAlchemy: orm_models.py + one file per domain; returns Entities, never ORM rows
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
compose.yml                  Postgres, backend, frontend, pgAdmin (never run)
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

Scripts must be run **from the repo root** with `-m backend.scripts...` (they import `backend.*`). Docs are at `/api/v1/docs` when `ENABLE_API_DOCS=true`.

**Frontend** (from `src/frontend/`): `npm ci`, `npm run dev`, `npm run lint`, `npm test`, `npm run build`.
`VITE_CLERK_PUBLISHABLE_KEY` **must be set at build time**; with it empty, Vite folds the check away and drops the whole app from the bundle.

For local Vite development, create `src/frontend/.env` with the public settings `VITE_CLERK_PUBLISHABLE_KEY`, `VITE_API_BASE_URL` and optional `VITE_PUBLIC_FRONTEND_URL`; Vite does not load the repository-root `.env` with the current configuration. Keep backend secrets in the root file. Docker Compose supplies the frontend variables through the container environment instead.

To share the local demo through one ngrok URL, set `VITE_API_BASE_URL=` and `VITE_PUBLIC_FRONTEND_URL=https://YOUR-DEV-DOMAIN.ngrok-free.dev` in the root and frontend environment files. Keep FastAPI on port 8000 and Vite on port 5173, then run `ngrok http 5173 --url https://YOUR-DEV-DOMAIN.ngrok-free.dev`. Vite serves the frontend at `/` and proxies `/api/v1` to FastAPI, so API calls and `/api/v1/webhooks/clerk` use the same public origin. Existing Clerk webhook URLs remain valid when the ngrok domain stays the same.

Add that exact public origin to the backend's comma-separated `CORS_ALLOWED_ORIGINS` and `CLERK_AUTHORIZED_PARTIES`, preserving `http://localhost:5173`, then restart both servers. Vite reads the exact public hostname from `VITE_PUBLIC_FRONTEND_URL`; do not use an unrestricted hostname allowlist. The demo remains available while the PC, local services and ngrok agent are running. The ignored local `.venv/start-bm-public.cmd` helper starts this machine's configured public demo; it is not a deployment service or a file supplied by a fresh clone.

Authentication uses Clerk Core 3 (`@clerk/react` 6) and `<Show when="signed-in">` / `<Show when="signed-out">` gates. Run `npm ci` after pulling SDK updates and restart Vite. The deprecated `@clerk/clerk-react` 5 package can be rejected by Clerk's minimum-version protection.

For automated testing without real inboxes, Clerk supports test-email addresses such as `owner+clerk_test@example.com` with verification code `424242` in development Test mode. Regular Gmail role aliases such as `yourname+owner@gmail.com` use actual verification codes delivered to the base Gmail inbox; they are not Clerk test-email addresses. The local role accounts now use Gmail aliases while preserving their existing identity IDs, passwords and database roles. Current login details are kept in the ignored `.venv/development-role-logins.csv`, never in migrations or tracked source. See [Clerk test-email documentation](https://clerk.com/docs/guides/development/testing/test-emails-and-phones).

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

</details>

## 6. Architecture rules (enforced by review, partly by tests)

**Controllers handle HTTP. Services enforce rules. Repositories handle SQL.**

<details>
<summary><strong>Technical reference and caveats</strong></summary>

These come from `.github/copilot-instructions.md` and the per-layer files in `.github/instructions/`. Follow them.

- **Layers:** Controller (HTTP only) → Service (rules, transactions, audit) → Repository (SQL only) → Entity. Controllers never import ORM, sessions or SDKs. Responses are always DTOs; entities and ORM rows are never returned.
- **Wiring:** Services receive repository _Contracts_; `providers.py` builds them per request around one session.
- **Transactions:** repositories only `flush`; a service calls `unit_of_work.commit()` once after all rule checks. A failure leaves nothing behind.
- **Errors:** services raise `BusinessRuleError(status, code, title, detail[, headers, extensions])`. Handlers return `application/problem+json` (RFC 9457) with a `trace_id`. Never put stack traces, SQL or paths in a response. `extensions` add fields such as `blocking_trip_ids`.
- **Naming and comments:** variables 4+ characters, functions 6+; forbidden names `data item obj val thing temp test misc`. Every source file starts with the `# ===== AI GENERATED: <name> =====` header (max 8 lines) describing purpose, inputs, returns, flow. JS uses JSDoc on every exported function (no TypeScript).
- **Frontend:** no API calls or business rules in components; API only through `services/`; state only through `store/`; role-based UI hints come from the backend's `/me` capabilities and only hide links (the backend still decides).
- **Input DTOs** set `extra="forbid"`. PATCH bodies extend `PartialUpdateRequest` (rejects empty bodies and null on required fields).
- **Units and formats:** UUID ids, JSON snake_case, UTC timestamps, weights as `Decimal` metric tons (JSON numbers), Philippine business date = UTC+8 (`Entity/clock.py`). Money is not built yet: use fixed-precision columns and string/Decimal, never float.
- **Audit:** every mutation writes an audit row with action, actor, entity and a trace id. `details` must never hold personal data, license numbers, emails or file names (field _names_ only).
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
- Forbidden role pairs (spec 3.2) are enforced on role assignment and need an Owner reason to override (audited). "No self-approval" is specified but **not built yet**: apply it to expenses, deductions, advances and adjustments in Sprint 5.

</details>

## 8. Tests

**Python 3.12 is the contract baseline.** PostgreSQL tests must use a scratch database.

<details>
<summary><strong>Technical reference and caveats</strong></summary>

`cd src/backend && .venv/Scripts/python -m pytest -q` (about 10-75 s). Files:

| File                                                                              | Covers                                                                                                    |
| --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `test_permission_matrix`                                                          | deny-by-default, every role x route                                                                       |
| `test_authentication`, `test_webhooks`, `test_reconciliation`, `test_rate_limits` | Clerk token/webhook/reconciliation interface and throttles                                                |
| `test_employees`, `test_fleet`, `test_delivery_orders`                            | records, ownership, field visibility, audit                                                               |
| `test_dispatch_assignment`, `test_dispatch_flow`                                  | capacity, crew, license, double booking, OR block, crew change, replacement                               |
| `test_or_documents`, `test_or_completion`, `test_storage_adapters`                | upload validation, metadata stripping, storage, signed URLs, confirmation, idempotency, FP-02, correction |
| `test_problem_details`, `test_platform`, `test_contract_snapshot`                 | error format, migrations vs models, seed, audit immutability, OpenAPI                                     |
| `test_postgres_hardening`                                                         | RLS, anon/authenticated lockdown, audit triggers (**only with `TEST_DATABASE_URL`**)                      |

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
D2 crew locked once the truck departs; D3 cancel only before departure, fail only after, earnings treatment deferred; D15 no override of the dispatch block; D5 hauling rate is **not stored** yet (working fixed-charge policy now defined in FINANCIAL_POLICIES.md); D14 no outbox; D1 helper upload off (`HELPER_OR_UPLOAD_ENABLED`).

</details>

## 10. API surface (38 paths, all under `/api/v1`)

**Contract:** `src/backend/openapi.snapshot.json`. All listed routes use `/api/v1`.

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

</details>

## 11. How to add a feature (checklist)

**Build the domain and backend rules before wiring the screen.** Include regression tests and documentation.

<details>
<summary><strong>Technical reference and caveats</strong></summary>

1. Read the spec section; if a rule is marked Open/Recommended, confirm with BM or put it behind a setting.
2. **Entity** (`Entity/`), **ORM** (`Repository/orm_models.py`), **migration** (new file, never edit applied ones; include RLS lock-down for new tables, copy the pattern in `0002`-`0004`).
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

- **PostgreSQL 16 in CI:** the application suite, including migrations, Row Level Security and audit-trigger tests, passed locally against an isolated PostgreSQL 18.2 instance. Check the workflow result for CI's PostgreSQL 16 environment after pushing.
- **Spec proof of concept (section 12 of the spec):** Clerk token lifetime and outage behaviour (tokens last about 60 s), webhook bad-signature then double replay, Supabase public key cannot read or write any table, backup restore time (the 4 h target is unproven), 5 MB phone upload on mobile data and signed URL expiry.
- **Live Supabase Storage:** `Infrastructure/Supabase/supabase_object_storage.py` is tested against a mock only; confirm upload, signing and delete against a real project.
- **Browser check:** desktop Chrome sign-in and the workspace were verified for all seven roles using the live Clerk development instance and test-email aliases. Mobile behavior and real-inbox verification still need testing.
- **Docker:** `compose.yml` and `src/backend/Dockerfile` were edited, never run.
- **Dependencies:** Pillow and python-multipart were added in Sprint 4; the frontend Clerk SDK was migrated to `@clerk/react` 6.18.8 with Core 3 authentication gates after the old SDK was blocked at sign-in. Frontend lint, 25 tests, build and dependency audit passed after the upgrade. The spec asks for a human dependency review note.

</details>

## 13. Left to build

**Financial policies exist; persistent financial modules do not.** Implement their ledgers and controls before removing preview labels.

<details>
<summary><strong>Technical reference and caveats</strong></summary>

**Sprint 5 (spec sections 7, 8, 9, 13.1):**

- Trip expenses (fuel, toll, other): states _entering / awaiting review / finalized / confirmed-zero_; missing expenses are never silently zero; the enterer cannot approve their own entry. Matrix rows: enter, approve.
- Finalize the hauling charge per trip (Accounting or Owner). Client rates are visible to Owner/Accounting only.
- Earnings: `base = charge - approved expenses`; driver+1 helper 8%/4%, driver+2 helpers 6%/3%/3% **of the base** (example: 20,000 - 5,500 = 14,500 -> 1,160/580 or 870/435/435). One entry per employee per trip; stays _Pending Calculation_ until charge and expenses are final; later percentage changes never alter finalized entries (use adjustments); negative base flagged, not paid.
- Payroll periods, employee deductions (after gross), net pay, statements, payment records (HR). Cash advances: request, Owner approval, release, repayment through payroll, balances; operating advances are separate and never become personal debt.
- Billing: batches of eligible, unbilled trips with carry-over; separate states for billing readiness, batch, invoice (draft/issued/void, two-person void) and payment; a trip charge appears in at most one active bill.
- Make the Owner's receipt correction also reverse/hold earnings and billing once they exist. Add the **no-self-approval** and Owner-delegated advance approver rules.
- Working policies for D4–D10 now exist in [FINANCIAL_POLICIES.md](../decisions/financial-policies.md). Implement their versioned rates, decimal rounding, approvals, schedules and billing eligibility with database constraints and tests. D16 (labour-law check) remains required before payroll goes live. These policy choices are new development defaults, not previously approved text from the supplied specification.

**Sprint 6 remaining:** expanded reports and dashboards (spec 10.1, including "completed without a stamped copy" spot-check flag and ORs awaiting receipt), security review, load test (the plan assumes ~30 trips/day, ~20 users, ~10 req/s peak), staging validation.

**Screens not built:** the real Expenses, Payroll, Advances, Billing and Reports screens (design previews exist, see 13a), and the **PWA** (manifest, service worker, installability) for drivers. The People, Audit, Permissions, crew-change and truck-replacement screens now exist.

**Platform and operations:** hosting and deploy pipeline (D12), Clerk/Supabase production plans (D11), MFA and recovery for Owner/HR/Accounting (D17), scheduled receipt-bucket backup, scheduling `reconcile_clerk` (e.g. hourly), HTTPS scan, decide whether `/docs` is public in production, data-privacy incident procedure and region (spec 11.3), branch protection and required reviewers on GitHub, a shared rate-limit store if more than one server process runs.

</details>

## 13a. Frontend design system (daisyUI + Tailwind)

**Reuse the theme and shared UI components.** Sample-data screens remain visibly labeled as previews.

<details>
<summary><strong>Technical reference and caveats</strong></summary>

- **Stack:** Tailwind 4 with **daisyUI 5.8.1** (pinned). Two custom themes live in `src/frontend/src/index.css`: `bm-dark` (bold dark navy + orange, default) and `bm-light`. The shell's sun/moon button toggles them and remembers the choice (`shared/utils/theme.js`, `store/themeStore.js`).
- **Shell:** `shared/components/AppShell.jsx` is a responsive frame: sidebar on large screens, slide-in menu plus a bottom dock on phones. Pages, their groups and the capability each needs are declared once in `shared/utils/navigation.js`; pages marked `preview: true` show a "Soon" badge.
- **Building blocks** (all pure components): `PageHeader`, `StatCard`, `StatusBadge` (labels and colours from `shared/utils/statusLabels.js`), `FilterTabs`, `SearchField`, `FormField`, `ModalDialog`, `ReasonDialog`, `RowMenu`, `Toast` (+ `hooks/useToast`), `EmptyState`, `ListSkeleton`, `ErrorNotice`, `Icon` (inline SVGs, no icon package).
- **Live screens:** Dashboard, Dispatch board (assign, clear, change crew, replace truck, cancel, fail, correct), Delivery orders (edit/cancel), Clients, Fleet (edit, maintenance history), My trips, People (roles, sign-in link, activation, driver licenses), Audit log, Permissions, My account. Page containers are in `src/pages/AppPages.jsx`; `src/App.jsx` is the root.
- **Design previews (not real yet):** Trip expenses, Payroll, Cash advances, Billing and Reports (`components/finance/*Preview.jsx` and `components/reports/ReportsPreview.jsx`) use invented data from `shared/mockups/sampleData.js` behind a "Design preview" banner. Replace each with a real screen when Sprints 5 and 6 land, and remove its preview entry.
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
