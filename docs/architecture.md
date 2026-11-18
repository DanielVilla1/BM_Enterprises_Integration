# System structure and code conventions

[Index](README.md) · [Developer setup](runbooks/development.md) · [Business workflow](runbooks/service-workflow.md)

> **Follow a request:** browser → API validation → business service → repository/adapter. Each layer has one job.

## Repository folder architecture

This is the current application layout. Start here when deciding where a file belongs.

```text
BM_Enterprises_Integration/
├── README.md                Project entry point and setup links
├── docs/
│   ├── README.md            Handbook navigation
│   ├── architecture.md     This folder map and layer responsibilities
│   ├── taxonomy.md         Business vocabulary, states and access levels
│   ├── decisions/          Financial working policies and decision index
│   ├── runbooks/           Setup, daily workflow, feature guides and checks
│   │   └── roles/          Seven role manuals and role index
│   └── archive/            Superseded proposal; historical reference only
├── tools/
│   ├── README.md           Maintenance and launch commands
│   └── scripts/            Backend launcher, docs checker and isolated PostgreSQL verifier
├── src/
│   ├── backend/            FastAPI, Python dependencies, migrations and tests
│   └── frontend/           React/Vite, npm dependencies and frontend tests
├── .github/                CI, PR template and development conventions
├── compose.yml              Coordinates frontend, API, database and pgAdmin
├── .env.example             Shared configuration template; no real credentials
├── .env                     Local configuration; ignored by Git
├── .editorconfig            Repository-wide editor defaults
├── .prettierrc.json          Shared formatting defaults
├── .prettierignore           Formatting exclusions
└── .gitignore               Git exclusions
```

Local-only folders such as `.venv/`, `node_modules/`, `dist/`, caches and `.git/` are not application source. Dependencies and build output belong inside the relevant application directory. Any ignored workstation helper, virtual environment, database or private development-account file is local-only; supported setup uses the tracked launch commands and configuration templates.

### Backend: business rules and persistence

```text
src/backend/
├── main.py                  FastAPI entry point and application composition
├── src/
│   ├── Controller/          HTTP routes and DTO mapping
│   ├── DTO/                 Request validation and public response shapes
│   ├── Service/             Workflow, authorization, transactions and audit
│   ├── Entity/              Domain values, statuses and pure rules
│   ├── Contract/            Interfaces for repositories and external systems
│   ├── Repository/          SQLAlchemy queries, ORM models and unit of work
│   ├── Infrastructure/
│   │   ├── Clerk/           Identity directory and token/webhook verification
│   │   ├── Supabase/        Private object storage adapter
│   │   └── Imaging/         Image validation and sanitization
│   ├── Data/                Permission seed data
│   ├── config.py            Environment settings
│   ├── database.py          Engine and session creation
│   ├── providers.py         Dependency wiring and capability gates
│   ├── problem_details.py   Shared API error format
│   ├── rate_limiter.py      Shared request-rate control
│   ├── request_limits.py    Request body limits
│   ├── response_security.py Private-response headers
│   └── openapi_contract.py  Stable RFC 9457 error schema
├── migrations/versions/     Versioned database changes
├── scripts/                 Owner bootstrap, reconciliation and API export
├── tests/                   Backend unit, integration and contract tests
├── openapi.snapshot.json    API contract baseline
├── pyproject.toml           Python lint, format and test configuration
├── requirements*.txt        Runtime and development dependencies
├── alembic.ini              Migration configuration
├── Dockerfile               Backend container build
└── .dockerignore            Backend build exclusions
```

### Frontend: feature UI and shared building blocks

```text
src/frontend/
├── src/
│   ├── main.jsx             Browser entry point
│   ├── App.jsx              Session gate and workspace composition
│   ├── index.css            Global theme and Tailwind entry
│   ├── pages/               AppPages.jsx + lazy FinancePage.jsx containers
│   ├── components/          Feature-specific presentation
│   │   ├── account/         Current employee profile
│   │   ├── administration/  People, permissions and audit screens
│   │   ├── clients/         Client records
│   │   ├── dashboard/       Operational overview
│   │   ├── dispatch/        Dispatch board and trip cards
│   │   ├── fleet/           Trucks and maintenance
│   │   ├── orders/          Delivery orders
│   │   ├── trips/           Crew progress, OR upload and receipt forms
│   │   ├── finance/         Persistent finance panels plus isolated design references
│   │   └── reports/         Persistent role-scoped reports plus design reference
│   ├── hooks/               Loading, action orchestration and UI lifecycle
│   ├── services/            Feature API clients
│   ├── store/               Zustand state by feature
│   └── shared/
│       ├── components/      Shell, sign-in layout and reusable UI controls
│       ├── services/        HTTP, Clerk and asynchronous loading wrappers
│       ├── utils/           Pure formatting, navigation and form helpers
│       └── mockups/         Fictional data for explicitly labeled previews
├── tests/
│   ├── unit/                Pure-helper regression tests
│   └── components/          Role-specific screen rendering tests
├── public/                  Manifest, offline-help worker, icons and public help page
├── design-preview/          Isolated sample-data preview harness
├── index.html               Main Vite HTML entry
├── preview.html             Sample preview HTML entry
├── package.json             Frontend scripts and dependencies
├── package-lock.json        Frontend dependency lock
├── vite.config.js           Vite plugins, allowed hosts and API proxy
├── eslint.config.js         JavaScript lint rules
├── Dockerfile               Frontend container build
└── README.md                Frontend commands and architecture links
```

### Where should a new file go?

| File or change                       | Put it here                                       | Example                               |
| ------------------------------------ | ------------------------------------------------- | ------------------------------------- |
| Feature-specific UI                  | `src/frontend/src/components/<feature>/`          | `trips/OrUploadForm.jsx`              |
| Reusable UI                          | `src/frontend/src/shared/components/`             | `ModalDialog.jsx`                     |
| Page composition                     | `src/frontend/src/pages/`                         | `AppPages.jsx`                        |
| Feature loading/actions              | `src/frontend/src/hooks/`                         | `useMyTrips.js`                       |
| Feature HTTP calls                   | `src/frontend/src/services/`                      | `tripService.js`                      |
| Shared SDK/transport                 | `src/frontend/src/shared/services/`               | `clerkSessionService.jsx`             |
| Pure shared calculation/formatting   | `src/frontend/src/shared/utils/`                  | `formatting.js`                       |
| Frontend regression test             | `src/frontend/tests/unit/` or `tests/components/` | `workflowRendering.test.jsx`          |
| Business workflow or permission rule | `src/backend/src/Service/`                        | `trip_service.py`                     |
| Database query/model                 | `src/backend/src/Repository/`                     | `trip_repository.py`                  |
| External provider adapter            | `src/backend/src/Infrastructure/<provider>/`      | `Supabase/supabase_object_storage.py` |
| Schema change                        | `src/backend/migrations/versions/`                | New versioned migration               |
| Operator command                     | `src/backend/scripts/`                            | `bootstrap_owner.py`                  |
| User/developer instructions          | `docs/` or `docs/runbooks/roles/`                 | This architecture page                |

Root files are limited to project-wide coordination, configuration and the entry README. Each app keeps its own dependency manifests, Dockerfile, test tooling and source. App-level files such as `src/backend/main.py`, `src/frontend/index.html`, `vite.config.js` and `src/main.jsx` stay at their expected entry locations so existing commands and containers keep working.

## Runtime structure

**Local frontend and API with database, storage and identity connections.**

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
<summary><strong>Directories, conventions and implementation notes</strong></summary>

The browser gets a Clerk session token; FastAPI verifies it and requires an active linked local employee. Role/capability data lives in PostgreSQL, not Clerk public metadata. The local development database is PostgreSQL; Supabase is used for private files. Hosting the database on Supabase remains compatible with the database configuration; the browser must not query application tables directly.

For temporary public sharing, ngrok can forward to Vite port 5173. Vite serves the app and proxies `/api/v1` to FastAPI port 8000. The frontend uses an empty API base URL for same-origin calls. Direct local API docs are `/api/v1/docs`. This is a development arrangement, not a production hosting design. pgAdmin is an operator tool, not part of user request processing.

</details>

## Backend ownership

**Request processing through the frontend and backend layers.**

```mermaid
flowchart TB
    accTitle: One request through the code
    accDescr: UI calls services, FastAPI validates and authorizes, business services apply rules, repositories persist, and DTOs return permitted fields.
    view["Component + hook<br/>Collect input"]:::action --> client["Frontend service<br/>Send request"]:::action
    client --> controller["Controller + DTO + authorization<br/>Validate request and access"]:::action
    controller --> service["Business service<br/>Rules + audit + transaction"]:::action
    service --> repository["Repository / adapter<br/>Database or external storage"]:::action
    repository --> result["Response DTO<br/>Only permitted fields"]:::done
    classDef action fill:#e8f1ff,stroke:#2563eb,color:#163566,stroke-width:2px
    classDef done fill:#e7f6ec,stroke:#208448,color:#16452a,stroke-width:2px
```

<details>
<summary><strong>Directories, conventions and implementation notes</strong></summary>

| Location                          | Responsibility                                                | Keep out                                       |
| --------------------------------- | ------------------------------------------------------------- | ---------------------------------------------- |
| `src/backend/main.py`             | App/router/middleware configuration                           | Business workflow branches                     |
| `src/Controller/`                 | HTTP input, dependency checks, DTO output                     | SQL, storage SDKs, financial calculations      |
| `src/DTO/`                        | Typed validation and explicit public projections              | Persistence/side effects                       |
| `src/Service/`                    | Ownership/state rules, orchestration, audit, commit boundary  | Direct SQL or vendor SDK operations            |
| `src/Entity/`                     | Domain data/statuses/pure rules                               | FastAPI, SQLAlchemy, vendor SDKs               |
| `src/Contract/`                   | Repository/adapter interfaces                                 | Concrete infrastructure                        |
| `src/Repository/`                 | Queries, ORM/domain mapping, flush                            | Business approvals or independent commits      |
| `src/Infrastructure/`             | Clerk, Supabase, image sanitization adapters                  | Route-specific business authorization          |
| `src/Data/permission_matrix.json` | Seeded role grants and conditional flag names                 | User account credentials                       |
| `src/providers.py`                | Per-request dependency wiring and shared capability gate      | Feature-specific workflow logic                |
| `migrations/`                     | Versioned schema, seeds, constraints and lockdown             | Editing already applied migration history      |
| `tests/`                          | Contract, ownership, lifecycle, retries and database controls | Real personal data or live account credentials |

A trip references one order/truck and retained crew entries. OR documents and receipt fields belong to trips. Replacement records preserve original/replacement identities. Order and truck state is derived after changes. Audit records are append-only. Financial models and ledgers are separate from operational status; see the financial implementation map below. Do not add money calculations to controllers.

</details>

## Frontend ownership

**Component** displays · **Hook** coordinates · **Store** holds state · **Service** calls APIs · **Utility** stays pure.

<details>
<summary><strong>Directories, conventions and implementation notes</strong></summary>

| Location                                | Responsibility                                                          |
| --------------------------------------- | ----------------------------------------------------------------------- |
| `src/App.jsx`, `src/pages/AppPages.jsx` | Root and page containers joining hooks to screens                       |
| `src/components/<feature>/`             | Feature presentation, form input and callbacks; no direct API/SDK calls |
| `src/shared/components/`                | Shared UI, application shell and sign-in layout                         |
| `tests/unit/`, `tests/components/`      | Frontend checks, kept outside production source                         |
| `src/hooks/`                            | Loading/action orchestration and lifecycle                              |
| `src/store/`                            | Domain Zustand state; no business approval decisions                    |
| `src/services/`                         | Feature API clients                                                     |
| `src/shared/services/`                  | HTTP/Clerk wrappers and asynchronous collection loading                 |
| `src/shared/utils/`                     | Pure formatting, navigation, forms and action-visibility helpers        |
| `src/shared/mockups/`                   | Invented data for explicitly labeled previews                           |
| `design-preview/`                       | Isolated UI preview harness; not production business data               |

This change moves `collectionLoader` from `shared/utils/` to `shared/services/` because it performs asynchronous loading and store writes. Pure action selectors combine backend capabilities, assignment and trip status; they only control presentation. FastAPI still authorizes each operation. Limited employee records must render without guessing missing private fields. Missing Helper upload grants hide the upload controls.

Keep feature screens in their named component folder and reusable UI in `shared/components/`. Hooks, stores and API clients retain the established layer directories and descriptive feature names. Update imports and tests when moving a module; do not leave duplicate compatibility copies at old paths.

</details>

## Formatting and language rules

<details>
<summary><strong>Directories, conventions and implementation notes</strong></summary>

| Language/files | Standard/tool                                                                                               |
| -------------- | ----------------------------------------------------------------------------------------------------------- |
| Python         | Python 3.12 contract baseline, explicit type hints, 4 spaces, Black 110 columns, Ruff import/lint checks    |
| JavaScript/JSX | JavaScript + JSDoc, named descriptive exports, 2 spaces, single quotes, no semicolons, Prettier 100 columns |
| CSS/HTML       | Prettier; theme tokens in `src/index.css`, reusable UI primitives                                           |
| JSON           | Prettier/double-quoted keys; generated lockfiles and OpenAPI snapshots kept generator-owned                 |
| Markdown/YAML  | Prettier; relative documentation links and fenced commands                                                  |
| Shell/config   | EditorConfig UTF-8, final newline, spaces; Windows command/PowerShell files use CRLF                        |

`.editorconfig` and `.prettierrc.json` define these defaults. Frontend `npm run format` formats its sources/configs, documentation, main README, Compose and CI workflow. `npm run format:check` verifies the same scope in CI. Generated files, dependencies, build output, secrets and virtual environments are excluded. Python keeps its existing Black/Ruff configuration.

Use exported-function JSDoc and Python signatures; explicit response DTOs; descriptive business names; AI change markers per repository governance. Keep comments about invariants/decisions rather than narrating trivial expressions. The `.github` governance files remain the detailed layer reference; existing business code patterns in the developer guide govern incremental changes.

</details>

## Extension and review

**Read rules, implement in the correct layer, test, document and review.**

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

<details>
<summary><strong>Directories, conventions and implementation notes</strong></summary>

For changes to finance, extend the existing typed values, fixed-precision persistence, ports, transactional services, explicit DTOs, capability checks and regression tests; update the corresponding frontend service/hook/store/screen integration. Implement [financial policies](decisions/financial-policies.md) as versioned configuration/ledger rules, not UI-only branches.

Test changed rules before broad formatting and preserve an API snapshot baseline. Financial routes and response shapes are included in the committed OpenAPI snapshot; regenerate it when changing the API. PostgreSQL checks must use a dedicated test database because the suite recreates its public schema.

Prettier is pinned as a development dependency following its [official installation guidance](https://prettier.io/docs/install.html); it is not bundled as a runtime application feature. Record runtime and development dependency audit results separately. Do not force an unrelated major downgrade to silence an audit finding.

</details>

## Financial implementation map

Paths below are relative to the repository root. This extends the layer-level folder map above.

| Area                   | Current files / responsibility                                                                                                                                                                                                                                          |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Domain                 | `src/backend/src/Entity/finance.py` defines financial records, exact rounding and payroll periods; `finance_query.py` defines bounded batch facts.                                                                                                                      |
| Ports and persistence  | `Contract/i_financial_repository.py`, `Repository/financial_repository.py`, and `Repository/finance_models.py` separate services from SQL. Existing order/client/document/employee/fleet/trip ports include bulk reads for reports.                                     |
| Schema                 | `migrations/versions/0005_financial_ledgers.py` creates private financial tables; `migrations/financial_schema_0005.py` freezes its schema; `0006_financial_permissions_and_review_history.py` upgrades existing grants and contributor history.                        |
| Commands               | `Service/financial_workflow.py` coordinates the financial lock, retry fingerprints, audit and transaction. Trip finance, payroll, advance and billing services own their business rules.                                                                                |
| Queries                | `Service/finance_query_service.py` projects role-scoped workspaces/reports. Trip facts and display-only employee names are loaded in batches to avoid a database query per report row.                                                                                  |
| HTTP contract          | `Controller/finance_controller.py`, `DTO/finance_dto.py`; `openapi_contract.py` normalizes documented RFC 9457 error responses across supported Python versions.                                                                                                        |
| Headers                | `response_security.py` and `problem_details.py` provide the configured no-store, content-sniffing/frame/referrer controls and traceable errors.                                                                                                                         |
| Frontend               | `pages/FinancePage.jsx` loads lazily from `AppPages.jsx`; `components/finance/*Panel.jsx` and `components/reports/ReportsPanel.jsx` display persistent DTOs.                                                                                                            |
| Frontend orchestration | `hooks/useFinanceWorkspace.js`, `services/financeService.js`, `store/financeStores.js` and `shared/utils/finance.js` handle account-scoped loading, strict payloads and retained retry keys.                                                                            |
| Demonstration          | `scripts/seed_presentation.py` validates a local nonproduction destination; `Repository/presentation_seed_repository.py` commits a repeatable fictional seed transaction. Demo images use `Infrastructure/Imaging/presentation_document.py`, not live Supabase uploads. |
| Installation support   | `src/frontend/public/manifest.webmanifest`, `service-worker.js`, `offline.html`, `icons/`, and `src/shared/services/offlineService.js`. Only production builds register the public offline-help worker.                                                                 |
| Verification           | Financial workflow, migration, presentation, readiness/query-growth, permission-matrix and load tests; `tools/scripts/verify_postgres.py` creates/removes a local scratch database.                                                                                     |

The financial tables are `finance_lock`, `expense_sheets`, `earning_rates`, `trip_financials`, `earnings`, `payrolls`, `pay_statements`, `pay_adjustments`, `advances`, `advance_movements`, `advance_delegations`, `invoices`, `invoice_lines`, `financial_payments` and `financial_operations`. Monetary columns use fixed precision; a unique employee/trip key protects original earnings, a partial unique index protects active billing allocation, and repayment/reversal/retry constraints prevent duplicate postings. Migration 0005 enables RLS and revokes Data API grants for the new tables.

Financial commands acquire one short database write lock before balance/allocation checks. Receipt correction uses the same finance-before-trip lock order and atomically holds related earnings/invoices. Receipt completion commits operations first; automatic earnings calculation then uses a separate transaction. Request-path repositories flush without committing; the presentation seed is an operator-only command with its own seed commit.

The browser never computes authoritative money. A draft payroll does not post repayments, UI grants do not replace service checks, and no action here transfers bank funds. Production/multi-worker validation and unsupported correction flows are listed in [the handoff](runbooks/sprint-5-6.md#remaining-release-gates).

### Financial API reference

All paths below start with `/api/v1/finance`. Every command requires `Idempotency-Key`; service rules add ownership, independence and state checks to the capability shown. Request/response fields are authoritative in [OpenAPI](../src/backend/openapi.snapshot.json).

| Method | Path                                       | Capability                     |
| ------ | ------------------------------------------ | ------------------------------ |
| GET    | `/presentation-documents/{document_id}`    | `or.view_files`                |
| GET    | `/expenses`                                | `expense.view`                 |
| GET    | `/payroll`                                 | `payroll.view`                 |
| GET    | `/advances`                                | `cash_advance.view`            |
| GET    | `/billing`                                 | `billing.manage`               |
| GET    | `/reports`                                 | `report.view`                  |
| POST   | `/expenses/{trip_id}`                      | `expense.enter`                |
| POST   | `/expenses/{trip_id}/submit`               | `expense.enter`                |
| POST   | `/expenses/{trip_id}/review`               | `expense.approve`              |
| POST   | `/charges/{trip_id}`                       | `charge.finalize`              |
| POST   | `/charges/{trip_id}/approve-variance`      | `earning_percentage.set`       |
| POST   | `/earnings/{trip_id}/calculate`            | `earnings.calculate`           |
| POST   | `/holds/{trip_id}/release`                 | `earning_percentage.set`       |
| POST   | `/rates`                                   | `earning_percentage.set`       |
| POST   | `/advances`                                | `cash_advance.request`         |
| POST   | `/advances/{identifier}/approve`           | `cash_advance.approval_action` |
| POST   | `/advances/{identifier}/release`           | `cash_advance.release_repay`   |
| POST   | `/advances/{identifier}/return`            | `cash_advance.release_repay`   |
| POST   | `/advances/{identifier}/reconcile`         | `cash_advance.approve`         |
| POST   | `/advance-delegations`                     | `cash_advance.approve`         |
| POST   | `/advance-delegations/{identifier}/revoke` | `cash_advance.approve`         |
| POST   | `/adjustments`                             | `deduction.record`             |
| POST   | `/adjustments/{identifier}/approve`        | `deduction.approve`            |
| POST   | `/payrolls`                                | `payroll.prepare`              |
| POST   | `/payrolls/{identifier}/finalize`          | `payroll.prepare`              |
| POST   | `/payrolls/{identifier}/reverse`           | `payroll.reverse`              |
| POST   | `/statements/{identifier}/payments`        | `payroll_payment.record`       |
| POST   | `/invoices`                                | `billing.manage`               |
| POST   | `/invoices/{identifier}/issue`             | `billing.manage`               |
| POST   | `/invoices/{identifier}/request-void`      | `billing.manage`               |
| POST   | `/invoices/{identifier}/approve-void`      | `invoice.void_approve`         |
| POST   | `/invoices/{identifier}/payments`          | `billing.manage`               |
