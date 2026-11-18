# BM Enterprises — Technical Documentation

**Parts 1 and 2 · Sections 1–8**

Verified against repository files on **18 November 2026, Asia/Manila**. Reviewed source baseline: `main` at commit `2558de4`. The `service_workflow` branch had the same tracked file contents when this document was prepared. Versions below describe declarations and lockfile resolutions, not an independently inspected production deployment.

[Handbook](../README.md) · [Architecture](../architecture.md) · [QA acceptance](../runbooks/qa.md)

| Part | Section                                                                                     |
| ---- | ------------------------------------------------------------------------------------------- |
| 1    | [1. Project Overview](#1-project-overview)                                                  |
| 1    | [2. Tech Stack & Dependencies](#2-tech-stack--dependencies)                                 |
| 1    | [3. System Architecture & Directory Structure](#3-system-architecture--directory-structure) |
| 1    | [4. Database Schema & Data Models](#4-database-schema--data-models)                         |
| 2    | [5. Routing & API Reference](#5-routing--api-reference)                                     |
| 2    | [6. User Roles, Permissions & Security](#6-user-roles-permissions--security)                |
| 2    | [7. Local Setup & Installation Guide](#7-local-setup--installation-guide)                   |
| 2    | [8. Deployment & Build Notes](#8-deployment--build-notes)                                   |

## 1. Project Overview

### 1.1 Project identity and purpose

| Item                                   | Verified information                                                                                                                     |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Project name                           | **BM Enterprises Hauling System**, identified in `README.md`                                                                             |
| API title/version                      | **BM Enterprises Hauling API**, version `1.0.0`, in `src/backend/main.py`                                                                |
| Frontend package                       | `frontend`, version `0.0.0`, in `src/frontend/package.json`; package metadata is not an approved business release number                 |
| Purpose                                | Internal hauling operations: employees, clients, fleet, delivery orders, dispatch, crew progress, signed OR evidence and company receipt |
| Production hosting target              | [To be completed by team]                                                                                                                |
| Approved production release identifier | [To be completed by team]                                                                                                                |

The implemented delivery sequence is: Dispatcher records an order and assigns a truck/crew; assigned Driver accepts; Dispatcher clears; Driver records departure and delivery; authorized crew uploads the signed OR; Driver confirms actual company receipt; the trip completes.

Uploading the signed OR and confirming receipt are separate events. Upload can permit one next reservation, while the next trip's dispatch remains subject to prior receipt and current resource eligibility checks. Workflow logic lives in `src/backend/src/Service/trip_service.py`, `or_service.py`, `trip_state_synchronizer.py` and `src/backend/src/Entity/dispatch.py`.

### 1.2 Target users

The seven roles are defined in `src/backend/src/Entity/access.py` and seeded by `src/backend/src/Data/permission_matrix.json`.

| Role            | Code            | Current purpose                                                                                                 |
| --------------- | --------------- | --------------------------------------------------------------------------------------------------------------- |
| Owner / Manager | `OWNER`         | Access administration, operational oversight, permitted dispatch actions, audit viewing and receipt corrections |
| Dispatcher      | `DISPATCHER`    | Client/order entry, trip assignment, clearance and operational exceptions                                       |
| Fleet Manager   | `FLEET_MANAGER` | Trucks, maintenance and Driver licenses                                                                         |
| Driver          | `DRIVER`        | Assigned-trip acceptance/progress, signed OR upload and receipt confirmation                                    |
| Helper          | `HELPER`        | Assigned-trip viewing; conditional OR upload/document access                                                    |
| HR and Payroll  | `HR_PAYROLL`    | Permitted employee administration; financial screens remain previews                                            |
| Accounting      | `ACCOUNTING`    | Permitted client/order/document reads and financial previews                                                    |

Roles combine through capability grants; they are not a blanket administrator hierarchy. Access levels are `FULL`, `VIEW`, `LTD` and `OWN`. Missing grants mean no access. See Section 6 for the effective route restrictions.

### 1.3 Implemented features

| Area               | Implemented functionality                                                                                                 | Principal source                                                                                                         |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Authentication     | Clerk sign-in, bearer-token bridge and JWT verification                                                                   | `src/frontend/src/shared/services/clerkSessionService.jsx`; `src/backend/src/Infrastructure/Clerk/`                      |
| Employees/access   | Employee records, role assignment, identity linking and activation/deactivation                                           | `src/backend/src/Service/employee_service.py`                                                                            |
| Permissions        | Database-backed grants, conditional flags and permission viewing                                                          | `src/backend/src/Service/authorization_service.py`; `src/backend/src/Data/permission_matrix.json`                        |
| Clients/orders     | Contact records, delivery instructions, dates, weights, updates and cancellation                                          | `src/backend/src/Service/client_service.py`; `delivery_order_service.py`                                                 |
| Fleet/licenses     | Truck capacity/status, maintenance history and Driver license records                                                     | `src/backend/src/Service/truck_service.py`; `driver_license_service.py`                                                  |
| Dispatch           | Assignment, eligibility, acceptance, clearance, departure/delivery, crew changes, truck replacement, cancellation/failure | `src/backend/src/Service/trip_service.py`                                                                                |
| OR/receipt         | Private image upload, signed URLs, supersession, idempotent receipt confirmation and restricted corrections               | `src/backend/src/Service/or_service.py`                                                                                  |
| Dashboard          | Operational summaries from live orders, trips, trucks and resource data                                                   | `src/frontend/src/hooks/useDashboard.js`                                                                                 |
| Audit/webhooks     | Audit history and protections; signature-verified webhook processing and deduplication                                    | `src/backend/src/Service/clerk_webhook_service.py`; `src/backend/migrations/versions/0001_initial_identity_and_audit.py` |
| Request protection | Body limits, rate budgets, trace IDs and API response headers                                                             | `src/backend/src/request_limits.py`; `rate_limiter.py`; `providers.py`; `problem_details.py`                             |

### 1.4 Preview-only scope

Trip expenses, payroll, cash advances, billing and expanded reports are sample-data screens. `src/frontend/src/pages/AppPages.jsx` renders preview components from `components/finance/` and `components/reports/`; fictional data resides in `src/frontend/src/shared/mockups/sampleData.js`.

The schema has no expense, payroll, advance, invoice or payment tables. Related seed permissions and working policies do not establish a persistent financial subsystem. Financial implementation and its production acceptance remain **[To be completed by team]**.

## 2. Tech Stack & Dependencies

### 2.1 Version sources

Frontend exact resolutions come from `src/frontend/package-lock.json` (lockfile version `3`); ranges come from `src/frontend/package.json`. Backend pins come from `src/backend/requirements.txt` and `requirements-dev.txt`, which are not a complete transitive dependency lock. Container/CI major-version selections do not establish exact deployed patch versions.

### 2.2 Frontend runtime dependencies

| Dependency     | Manifest  | Exact lockfile version | Purpose               |
| -------------- | --------- | ---------------------- | --------------------- |
| `react`        | `^19.2.0` | `19.3.1`               | Browser UI            |
| `react-dom`    | `^19.2.0` | `19.3.1`               | React DOM rendering   |
| `@clerk/react` | `6.18.8`  | `6.18.8`               | Identity/session UI   |
| `axios`        | `^1.13.6` | `1.21.1`               | HTTP client           |
| `zustand`      | `^5.0.11` | `5.0.11`               | State stores          |
| `daisyui`      | `5.8.1`   | `5.8.1`                | UI styling/components |

### 2.3 Frontend development dependencies

| Dependency                    | Manifest   | Exact lockfile version |
| ----------------------------- | ---------- | ---------------------- |
| `vite`                        | `^7.3.1`   | `7.3.8`                |
| `@vitejs/plugin-react`        | `^5.1.1`   | `5.1.4`                |
| `tailwindcss`                 | `^4.2.1`   | `4.2.1`                |
| `@tailwindcss/vite`           | `^4.2.1`   | `4.2.1`                |
| `postcss`                     | `^8.5.6`   | `8.5.33`               |
| `autoprefixer`                | `^10.4.27` | `10.4.27`              |
| `vitest`                      | `^5.1.0`   | `5.1.0`                |
| `eslint`                      | `^9.39.1`  | `9.39.3`               |
| `@eslint/js`                  | `^9.39.1`  | `9.39.3`               |
| `eslint-plugin-react-hooks`   | `^7.0.1`   | `7.0.1`                |
| `eslint-plugin-react-refresh` | `^0.4.24`  | `0.4.26`               |
| `globals`                     | `^16.5.0`  | `16.5.0`               |
| `prettier`                    | `3.10.1`   | `3.10.1`               |
| `@types/node`                 | `^25.3.3`  | `25.3.3`               |
| `@types/react`                | `^19.2.7`  | `19.2.14`              |
| `@types/react-dom`            | `^19.2.3`  | `19.2.3`               |

Application source is JavaScript/JSX; type declaration packages do not establish a TypeScript implementation. Tailwind/daisyUI integration is in `src/frontend/vite.config.js` and `src/frontend/src/index.css`, which defines dark/light application themes.

### 2.4 Backend dependencies

| Dependency           | Pin       | Purpose                           |
| -------------------- | --------- | --------------------------------- |
| FastAPI              | `0.162.7` | REST API and dependency injection |
| Starlette            | `1.10.0`  | ASGI infrastructure               |
| Uvicorn `[standard]` | `0.54.0`  | ASGI server                       |
| Pydantic             | `2.14.3`  | DTO validation                    |
| pydantic-settings    | `2.16.3`  | Environment settings              |
| SQLAlchemy           | `2.1.8`   | ORM and sessions                  |
| Alembic              | `1.20.1`  | Migrations                        |
| psycopg2-binary      | `2.9.13`  | PostgreSQL driver                 |
| PyJWT                | `2.15.1`  | JWT verification                  |
| cryptography         | `50.0.2`  | Cryptographic dependency          |
| HTTPX                | `0.28.1`  | Provider HTTP integrations        |
| Pillow               | `13.0.0`  | Image validation/sanitization     |
| Svix                 | `2.10.0`  | Webhook verification              |
| python-dotenv        | `1.2.4`   | Environment-file support          |
| python-multipart     | `0.0.33`  | Upload parsing                    |

Development requirements pin pytest `9.2.0`, Ruff `0.17.5` and Black `26.10.1`. `pip-audit` is declared without a version: **[To be completed by team]** if a reproducible pin is required. Tool configuration resides in `src/backend/pyproject.toml`.

### 2.5 Runtimes and infrastructure

| Component                 | Repository selection                                             | Limitation                                               |
| ------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------- |
| Python container          | `python:3.12-slim`                                               | Patch/digest not pinned                                  |
| Python CI                 | `3.12`                                                           | Patch selected by setup action                           |
| Node container            | `node:20-alpine`                                                 | Patch/digest not pinned                                  |
| Node CI                   | `22`                                                             | Different major from container                           |
| PostgreSQL Compose        | `postgres:15`                                                    | Minor/patch/digest not pinned                            |
| PostgreSQL CI             | `postgres:16`                                                    | Different major from Compose                             |
| SQLite                    | Supported by database factory; fallback URL `sqlite:///./dev.db` | SQLite engine version not pinned                         |
| pgAdmin                   | `dpage/pgadmin4`                                                 | No explicit tag/digest                                   |
| Production infrastructure | [To be completed by team]                                        | No approved deployed versions established by these files |

Sources: `compose.yml`, `.github/workflows/ci.yml`, both application Dockerfiles and `src/backend/src/database.py`.

### 2.6 Third-party integrations

Clerk supplies authentication through the React SDK and backend JWT/JWKS, identity-directory and webhook adapters in `src/backend/src/Infrastructure/Clerk/`. Supabase supplies private object storage through HTTPX REST calls in `src/backend/src/Infrastructure/Supabase/supabase_object_storage.py`; no Supabase JavaScript SDK is declared in the frontend manifest. Hosted Clerk/Supabase service releases are not pinned by this repository.

GitHub Actions supplies CI through `.github/workflows/ci.yml`. No Composer manifest was found; the reviewed application manifests are npm and Python files.

## 3. System Architecture & Directory Structure

### 3.1 Architecture and request flow

This is a client-rendered React SPA with a layered FastAPI REST backend, not a server-rendered MVC website. React mounts through `createRoot` in `src/frontend/src/main.jsx`. `App.jsx` handles session gates and workspace composition; `pages/AppPages.jsx` joins hooks to feature presentation.

```mermaid
flowchart LR
    browser["Browser: React SPA"] --> clerk["Clerk sign-in"]
    browser -->|"REST /api/v1 + bearer token"| api["FastAPI controllers"]
    api --> services["Business services"]
    services --> repos["Repositories + unit of work"]
    repos --> database["PostgreSQL / SQLite support"]
    api --> identity["JWT / JWKS verification"]
    services --> adapters["Infrastructure adapters"]
    adapters --> storage["Private Supabase Storage"]
```

| Layer           | Location                                             | Responsibility                                                       |
| --------------- | ---------------------------------------------------- | -------------------------------------------------------------------- |
| UI              | `src/frontend/src/components/`, `shared/components/` | Render props and emit callbacks                                      |
| Page/hook       | `src/frontend/src/pages/`, `hooks/`                  | Coordinate screens, loading and actions                              |
| Frontend state  | `src/frontend/src/store/`                            | Zustand state                                                        |
| API clients     | `src/frontend/src/services/`, `shared/services/`     | Feature requests, token attachment and error normalization           |
| Controller      | `src/backend/src/Controller/`                        | HTTP input, access dependencies and response mapping                 |
| DTO             | `src/backend/src/DTO/`                               | Pydantic request/response shapes                                     |
| Service         | `src/backend/src/Service/`                           | Business rules, ownership/state, audit and transaction orchestration |
| Entity/Contract | `src/backend/src/Entity/`, `Contract/`               | Domain values and persistence/provider interfaces                    |
| Repository      | `src/backend/src/Repository/`                        | Queries, ORM/domain mapping and persistence                          |
| Infrastructure  | `src/backend/src/Infrastructure/`                    | Clerk, Supabase and imaging adapters                                 |

`src/backend/src/providers.py` wires sessions, services, identity, capability checks and request budgets. The browser does not directly query business tables.

Clerk supplies a session token; Axios attaches it; the backend verifies it, resolves an active linked employee and reads database-backed permissions. Services then enforce ownership and state. Clerk metadata is not the authoritative application role store.

### 3.2 Runtime boundaries

`src/frontend/src/shared/services/httpClient.js` uses `VITE_API_BASE_URL` plus `/api/v1`. An empty origin uses the same-origin development proxy configured in `src/frontend/vite.config.js`; its target is `http://127.0.0.1:8000`.

API endpoints use `/api/v1`. Development docs and schema are `/api/v1/docs` and `/api/v1/openapi.json` when enabled. `src/backend/openapi.snapshot.json` is the committed contract baseline.

There is no dedicated dashboard API in that contract: `useDashboard.js` loads live orders, trips, trucks and dispatch resources. Page selection is application state, not separately declared `/dashboard` or `/dispatch` web routes.

Rate budgets in `src/backend/src/rate_limiter.py` are process-local. Shared enforcement across multiple workers/replicas is a hosting decision: **[To be completed by team]**.

### 3.3 Annotated source tree

Installed dependencies, environments, caches and build output are omitted.

```text
BM_Enterprises_Integration/
├── README.md                         Project entry point
├── compose.yml                       Development database/API/UI/pgAdmin
├── .env.example                      Placeholder configuration template
├── .editorconfig                     Editor conventions
├── .prettierrc.json                   Formatting defaults
├── .prettierignore                   Formatting exclusions
├── .gitignore                        Git exclusions
├── .github/
│   ├── workflows/ci.yml              Tests, formatting, audits and secret scanning
│   ├── instructions/                 Layer-specific conventions
│   ├── copilot-instructions.md       Development governance
│   ├── file-structure.md             Placement rules
│   └── pull_request_template.md      Review template
├── docs/
│   ├── README.md                     Handbook index
│   ├── architecture.md               Architecture and ownership
│   ├── taxonomy.md                   Vocabulary and statuses
│   ├── decisions/                    Financial/security working decisions
│   ├── runbooks/                     Setup, workflows, QA and verification
│   │   └── roles/                    Seven role manuals
│   ├── technical/                    This combined technical reference
│   └── archive/                      Superseded proposal
├── tools/
│   ├── README.md                     Tool usage
│   └── scripts/
│       ├── backend.py                Backend module launcher
│       └── check_docs.py             Markdown reference checks
└── src/
    ├── backend/
    │   ├── main.py                   FastAPI factory and app instance
    │   ├── Dockerfile                Python API container
    │   ├── alembic.ini               Migration configuration
    │   ├── pyproject.toml            Ruff/Black/pytest configuration
    │   ├── requirements*.txt         Runtime/development requirements
    │   ├── openapi.snapshot.json     API contract
    │   ├── migrations/
    │   │   ├── env.py                Alembic metadata wiring
    │   │   └── versions/             Four migration revisions
    │   ├── scripts/                  Owner bootstrap, reconciliation, API export
    │   ├── tests/                    Unit/integration/contract tests
    │   └── src/
    │       ├── Controller/           HTTP routers
    │       ├── DTO/                  Validated request/response models
    │       ├── Service/              Business use cases
    │       ├── Entity/               Domain objects/enums
    │       ├── Contract/             Interfaces
    │       ├── Repository/
    │       │   └── orm_models.py     All 16 application table mappings
    │       ├── Infrastructure/
    │       │   ├── Clerk/            Identity/token/webhook adapters
    │       │   ├── Supabase/         Private storage adapter
    │       │   └── Imaging/          Image sanitizer
    │       ├── Data/permission_matrix.json
    │       ├── config.py             Environment settings
    │       ├── database.py           Engine, Base and sessions
    │       ├── providers.py          Dependency and access gates
    │       ├── problem_details.py    Errors, trace IDs and API headers
    │       ├── rate_limiter.py       Request budgets
    │       └── request_limits.py     Body-size middleware
    └── frontend/
        ├── index.html                Main HTML entry
        ├── preview.html              Sample-data preview entry
        ├── package.json              Scripts/dependencies
        ├── package-lock.json         Exact npm resolutions
        ├── vite.config.js            Plugins and development proxy
        ├── eslint.config.js          Lint configuration
        ├── Dockerfile                Development container
        ├── design-preview/           Isolated sample UI harness
        ├── tests/
        │   ├── unit/                 Helper tests
        │   └── components/           Rendering tests
        └── src/
            ├── main.jsx              React mount
            ├── App.jsx               Session/workspace root
            ├── index.css             Global styling/themes
            ├── pages/AppPages.jsx    Page composition
            ├── components/
            │   ├── account/
            │   ├── administration/
            │   ├── clients/
            │   ├── dashboard/
            │   ├── dispatch/
            │   ├── finance/          Preview screens
            │   ├── fleet/
            │   ├── orders/
            │   ├── reports/          Preview screen
            │   └── trips/
            ├── hooks/                Loading/action orchestration
            ├── services/             Feature API clients
            ├── store/                Zustand stores
            └── shared/
                ├── components/       Shared controls/shell/sign-in layout
                ├── services/         HTTP/Clerk/loading wrappers
                ├── utils/            Pure helpers
                └── mockups/          Fictional preview records
```

`tools/scripts/backend.py` adds repository `src/` to `PYTHONPATH` and keeps the working directory at the root, preserving `backend.*` imports and root `.env` lookup. Production topology is not established by the development Compose/Vite configuration.

## 4. Database Schema & Data Models

### 4.1 Sources and migrations

ORM definitions are in `src/backend/src/Repository/orm_models.py`; database setup is in `src/backend/src/database.py`. There are **16 application tables**. Alembic's framework metadata table `alembic_version` is also referenced by the initial migration but is not a business model.

| Revision | File under `src/backend/migrations/versions/` | Scope                                                                                 |
| -------- | --------------------------------------------- | ------------------------------------------------------------------------------------- |
| `0001`   | `0001_initial_identity_and_audit.py`          | Roles, employees, grants, audit, webhook tracking, seed data and database protections |
| `0002`   | `0002_fleet_clients_orders.py`                | Clients, trucks, maintenance, licenses and orders                                     |
| `0003`   | `0003_trips_and_dispatch.py`                  | Trips, crew history, replacements and assignment-view capability                      |
| `0004`   | `0004_or_documents_and_completion.py`         | OR metadata, receipt fields and idempotency keys                                      |

Migration order: `0001 → 0002 → 0003 → 0004`. Permission seeds come from `src/backend/src/Data/permission_matrix.json`.

In the summaries below, PK means primary key, FK means foreign key and timestamp means `DateTime(timezone=True)`. Optional fields are identified as nullable.

### 4.2 Identity, permissions and audit

All listed ORM classes reside in `src/backend/src/Repository/orm_models.py`.

| Table / class                                      | PK                                   | FKs                                                                                        | Fields and important constraints                                                                                                                                               |
| -------------------------------------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `roles` / `RoleRow`                                | `code` String(32)                    | None                                                                                       | `name` String(64); seeded role vocabulary                                                                                                                                      |
| `employees` / `EmployeeRow`                        | `employee_id` UUID                   | None                                                                                       | `full_name` String(120), `email` String(254), nullable `phone` String(32), nullable unique `clerk_user_id` String(64), `is_active`, `created_at`; unique lowercase-email index |
| `employee_roles` / `EmployeeRoleRow`               | Composite `employee_id`, `role_code` | Employee → `employees.employee_id`; role → `roles.code`; nullable `assigned_by` → employee | `assigned_at`, nullable `exception_reason` Text                                                                                                                                |
| `role_permissions` / `RolePermissionRow`           | Composite `capability`, `role_code`  | Role → `roles.code`                                                                        | `capability` String(64), `access_level` String(8), nullable `conditional_setting` String(64)                                                                                   |
| `audit_log` / `AuditLogRow`                        | `audit_id` UUID                      | Nullable `actor_employee_id` → employee                                                    | `occurred_at`, `action`/`entity_type` String(64), nullable `entity_id` String(64), `details` JSON, nullable `trace_id` String(64); append-only protections                     |
| `processed_webhook_events` / `ProcessedWebhookRow` | `event_id` String(128)               | None                                                                                       | `event_type` String(64), `processed_at`                                                                                                                                        |

There is no separate local `users` or `capabilities` table. Clerk identity is linked by `employees.clerk_user_id`; local tables do not store Clerk passwords. `audit_log.entity_id` is a generic reference, not a declared FK to every audited entity.

### 4.3 Clients, fleet and orders

| Table / class                                        | PK                          | FKs                                                    | Fields and important constraints                                                                                                                                                                                                           |
| ---------------------------------------------------- | --------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `clients` / `ClientRow`                              | `client_id` UUID            | None                                                   | `name` String(160), nullable `address` String(300), `contact_person` String(120), `contact_phone` String(32), `is_active`, `created_at`; unique lowercase-name index                                                                       |
| `trucks` / `TruckRow`                                | `truck_id` UUID             | None                                                   | Unique `plate_number` String(16), nullable `description` String(120), positive `capacity_tons` Numeric(10,3), `status` String(16), `is_active`, `created_at`                                                                               |
| `truck_maintenance_records` / `MaintenanceRecordRow` | `record_id` UUID            | `truck_id` → truck; nullable `started_by` → employee   | `reason` Text, `started_at`, nullable `ended_at`                                                                                                                                                                                           |
| `driver_licenses` / `DriverLicenseRow`               | `employee_id` UUID, also FK | Employee → `employees.employee_id`                     | Unique `license_number` String(32), `expiry_date` Date, `updated_at`; at most one row per employee                                                                                                                                         |
| `delivery_orders` / `DeliveryOrderRow`               | `order_id` UUID             | `client_id` → client; nullable `created_by` → employee | Nullable `client_reference` String(64); pickup/delivery locations String(300), `scheduled_date` Date, positive `total_weight_tons` Numeric(12,3), `status` String(24), nullable notes/cancellation reason, `created_at`; status/date index |

Client/order tables do not contain hauling rates, finalized charges, invoice totals or payment fields.

### 4.4 Trips and resource history

| Table / class                                | PK                    | FKs                                                                                                                | Fields and important constraints                                                                                                                                                                                     |
| -------------------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `trips` / `TripRow`                          | `trip_id` UUID        | `order_id` → order; `truck_id` → truck; nullable `created_by`, `or_uploaded_by`, `receipt_confirmed_by` → employee | Positive `load_tons` Numeric(12,3), `status` String(24), nullable acceptance/clearance/departure/delivery timestamps, `closed_reason`, `created_at`, `or_uploaded_at`, `receipt_confirmed_at`, `receipt_received_at` |
| `trip_crew` / `TripCrewRow`                  | `crew_entry_id` UUID  | `trip_id` → trip; `employee_id` → employee                                                                         | `crew_role` String(8), `assigned_at`, nullable `removed_at`; partial unique indexes for one active Driver and no duplicate active member on a trip                                                                   |
| `truck_replacements` / `TruckReplacementRow` | `replacement_id` UUID | Trip → trip; `original_truck_id` and `replacement_truck_id` → trucks; nullable `replaced_by` → employee            | `reason` Text, `effective_at`                                                                                                                                                                                        |

Trip timestamp column names are `accepted_at`, `cleared_at`, `departed_at`, `delivered_at`, `or_uploaded_at`, `receipt_confirmed_at` and `receipt_received_at`. Indexes cover order, truck/status and trip status. Crew assignment history is retained through `removed_at`.

`driver_id` and `helper_ids` exist on the domain `Trip` in `src/backend/src/Entity/dispatch.py`, not as columns on `trips`: persisted crew membership is in `trip_crew`. The database enforces at most one active Driver; services enforce exactly one Driver and one or two Helpers for an assignment.

### 4.5 Documents and idempotency

| Table / class                            | PK                                           | FKs                                                 | Fields and important constraints                                                                                                                                    |
| ---------------------------------------- | -------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `or_documents` / `OrDocumentRow`         | `document_id` UUID                           | `trip_id` → trip; nullable `uploaded_by` → employee | `kind` String(16), unique `storage_path` String(200), `content_type` String(32), positive `size_bytes` Integer, `uploaded_at`, nullable `superseded_at`; trip index |
| `idempotency_keys` / `IdempotencyKeyRow` | Composite `key` String(128), `actor_id` UUID | Actor → employee                                    | `scope` String(100), `created_at`                                                                                                                                   |

Image bytes reside in private Supabase Storage, not database BLOBs. `document_repositories.py` retains superseded document metadata and stores idempotency records. Receipt confirmation updates trip fields and the idempotency ledger; it does not create financial records.

### 4.6 Relationships

| Parent            | Relationship                       | Child / association                                    |
| ----------------- | ---------------------------------- | ------------------------------------------------------ |
| Employees ↔ roles | Many-to-many                       | `employee_roles`                                       |
| Roles             | One-to-many                        | `role_permissions`                                     |
| Clients           | One-to-many                        | `delivery_orders`                                      |
| Delivery orders   | One-to-many                        | `trips`                                                |
| Trucks            | One-to-many                        | Current `trips` and maintenance records                |
| Employees         | One-to-zero-or-one                 | `driver_licenses`                                      |
| Trips/employees   | Each one-to-many                   | Historical `trip_crew` entries                         |
| Trips             | One-to-many                        | Truck replacements and OR documents                    |
| Trucks            | Referenced as original/replacement | `truck_replacements`                                   |
| Employees         | One-to-many                        | Creator/operator/audit references and idempotency keys |

Relationships are declared through FK columns. The reviewed mappings do not define SQLAlchemy `relationship()` navigation attributes; repositories query and map explicitly.

### 4.7 States, constraints and exclusions

| Record        | Allowed stored values                                                                                                                    |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Truck         | `AVAILABLE`, `ASSIGNED`, `IN_TRANSIT`, `MAINTENANCE`                                                                                     |
| Order         | `PENDING`, `PARTIALLY_ASSIGNED`, `SCHEDULED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`                                                    |
| Trip          | `SCHEDULED`, `ACCEPTED`, `CLEARED_FOR_DISPATCH`, `IN_TRANSIT`, `DELIVERED_OR_PENDING`, `OR_UPLOADED`, `COMPLETED`, `FAILED`, `CANCELLED` |
| Crew role     | `DRIVER`, `HELPER`                                                                                                                       |
| Document kind | `SIGNED_OR`, `STAMPED_COPY`                                                                                                              |

Database check constraints enforce these state vocabularies and positive quantities. Services enforce cross-record capacity, availability, license/role eligibility and workflow transitions. `trip_state_synchronizer.py` recalculates operational order/truck states.

PostgreSQL migrations enable RLS and revoke table grants from Supabase `anon`/`authenticated` roles when present. Audit triggers prohibit update/delete/truncate on PostgreSQL; SQLite gets update/delete protection triggers. Most entity UUIDs are generated by ORM-side `uuid.uuid4`, not a migration-installed database UUID generator. `utc_now()` supplies UTC timestamps; Manila business dates are handled in `src/backend/src/Entity/clock.py`.

No ORM/migration implementation exists for expenses, earnings/payroll ledgers, deductions/releases, personal advance balances/repayments, invoices or client payment records. Their persistent models and migrations are **[To be completed by team]**.

## 5. Routing & API Reference

### 5.1 Browser entry points

| Method | Path                   | Handler / source                                        | Access                                                                           | Purpose                                            |
| ------ | ---------------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------- |
| GET    | `/`                    | `src/frontend/index.html` → `src/main.jsx` → `App.jsx`  | Sign-in UI when signed out; operational workspace requires active linked account | Main SPA                                           |
| GET    | `/preview.html`        | `src/frontend/preview.html` → `design-preview/main.jsx` | No Clerk/backend connection in the preview harness                               | Sample-data UI preview, not saved operational work |
| GET    | `/api/v1/docs`         | FastAPI-generated UI in `src/backend/main.py`           | Public when enabled                                                              | Interactive API documentation                      |
| GET    | `/api/v1/openapi.json` | FastAPI-generated schema in `src/backend/main.py`       | Public when enabled                                                              | Machine-readable API contract                      |

Sidebar pages such as Dashboard, Dispatch and My trips are selected through application state and `src/frontend/src/pages/AppPages.jsx`; no separate `/dashboard`, `/dispatch` or `/login` web route is declared. Clerk's sign-in component uses hash routing inside the SPA. Enabling API docs does not itself require a signed-in employee.

### 5.2 API conventions

All paths in the following API tables include `/api/v1`. Except health and the signature-authenticated webhook, business endpoints require a valid Clerk bearer token mapped to an active local employee. Listed roles describe the seeded single-role grants; ownership, conditional flags and state checks still apply.

Controller files named below reside in `src/backend/src/Controller/`. DTO definitions reside in `src/backend/src/DTO/`. The full payload/response contract is in `src/backend/openapi.snapshot.json` and the enabled OpenAPI endpoint.

### 5.3 Account, administration and webhook endpoints

| Method | Path                        | Controller / handler                                  | Authentication / role                                              | Description                                                 |
| ------ | --------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------ | ----------------------------------------------------------- |
| GET    | `/api/v1/health`            | `health_controller.py:read_health`                    | Public                                                             | Application health response                                 |
| GET    | `/api/v1/me`                | `account_controller.py:read_current_account`          | Any active linked employee                                         | Identity, roles and effective capabilities                  |
| GET    | `/api/v1/permission-matrix` | `administration_controller.py:read_permission_matrix` | `audit_user.manage`; Owner                                         | Read grants                                                 |
| GET    | `/api/v1/audit-logs`        | `administration_controller.py:read_audit_log`         | `audit_user.manage`; Owner                                         | Paginated audit records                                     |
| POST   | `/api/v1/webhooks/clerk`    | `webhook_controller.py:receive_clerk_webhook`         | Svix/Clerk signature, not employee bearer auth; webhook rate limit | Process supported identity events and deduplicate event IDs |

### 5.4 Employees and Driver licenses

| Method | Path                                             | Controller / handler                               | Authentication / role                                                         | Description                                     |
| ------ | ------------------------------------------------ | -------------------------------------------------- | ----------------------------------------------------------------------------- | ----------------------------------------------- |
| GET    | `/api/v1/employees`                              | `employee_controller.py:list_employees`            | `employee.manage`: Owner/HR full, Dispatcher/Fleet limited, Driver/Helper own | List with scope/projection restrictions         |
| POST   | `/api/v1/employees`                              | `employee_controller.py:create_employee`           | `employee.manage FULL`; Owner/HR                                              | Create employee                                 |
| GET    | `/api/v1/employees/{employee_id}`                | `employee_controller.py:read_employee`             | Same read grant; OWN cannot read another employee                             | Read employee                                   |
| PATCH  | `/api/v1/employees/{employee_id}`                | `employee_controller.py:update_employee`           | `employee.manage FULL`; Owner/HR                                              | Update permitted employee details               |
| POST   | `/api/v1/employees/{employee_id}/activate`       | `employee_controller.py:activate_employee`         | `employee.activate`; Owner                                                    | Activate access                                 |
| POST   | `/api/v1/employees/{employee_id}/deactivate`     | `employee_controller.py:deactivate_employee`       | `audit_user.manage`; Owner                                                    | Deactivate access                               |
| PUT    | `/api/v1/employees/{employee_id}/identity`       | `employee_controller.py:link_employee_identity`    | `audit_user.manage`; Owner                                                    | Link Clerk user ID                              |
| PUT    | `/api/v1/employees/{employee_id}/roles`          | `employee_controller.py:assign_employee_roles`     | `audit_user.manage`; Owner                                                    | Replace roles; enforce separation-of-duty rules |
| GET    | `/api/v1/employees/{employee_id}/driver-license` | `driver_license_controller.py:read_driver_license` | Owner/Fleet full, HR view, Dispatcher limited, Driver own                     | Read license/detail or limited projection       |
| PUT    | `/api/v1/employees/{employee_id}/driver-license` | `driver_license_controller.py:save_driver_license` | `driver_license.view FULL`; Owner/Fleet                                       | Save license for eligible Driver                |

### 5.5 Clients, orders and fleet

| Method | Path                                             | Controller / handler                                 | Authentication / role                                | Description                    |
| ------ | ------------------------------------------------ | ---------------------------------------------------- | ---------------------------------------------------- | ------------------------------ |
| GET    | `/api/v1/clients`                                | `client_controller.py:list_clients`                  | `delivery_order.manage`; Owner/Dispatcher/Accounting | List clients                   |
| POST   | `/api/v1/clients`                                | `client_controller.py:create_client`                 | Same capability, `FULL`; Dispatcher                  | Create client                  |
| GET    | `/api/v1/clients/{client_id}`                    | `client_controller.py:read_client`                   | Owner/Dispatcher/Accounting                          | Read client                    |
| PATCH  | `/api/v1/clients/{client_id}`                    | `client_controller.py:update_client`                 | Dispatcher                                           | Update permitted fields/status |
| GET    | `/api/v1/delivery-orders`                        | `delivery_order_controller.py:list_delivery_orders`  | `delivery_order.manage`; Owner/Dispatcher/Accounting | List orders                    |
| POST   | `/api/v1/delivery-orders`                        | `delivery_order_controller.py:create_delivery_order` | Same capability, `FULL`; Dispatcher                  | Create order                   |
| GET    | `/api/v1/delivery-orders/{order_id}`             | `delivery_order_controller.py:read_delivery_order`   | Owner/Dispatcher/Accounting                          | Read order                     |
| PATCH  | `/api/v1/delivery-orders/{order_id}`             | `delivery_order_controller.py:update_delivery_order` | Dispatcher; state restrictions                       | Update order                   |
| POST   | `/api/v1/delivery-orders/{order_id}/cancel`      | `delivery_order_controller.py:cancel_delivery_order` | Dispatcher; state/reason restrictions                | Cancel order                   |
| GET    | `/api/v1/trucks`                                 | `truck_controller.py:list_trucks`                    | `truck.manage`; Owner/Fleet/Dispatcher               | List trucks                    |
| POST   | `/api/v1/trucks`                                 | `truck_controller.py:create_truck`                   | `truck.manage FULL`; Owner/Fleet                     | Register truck                 |
| GET    | `/api/v1/trucks/{truck_id}`                      | `truck_controller.py:read_truck`                     | Owner/Fleet/Dispatcher                               | Read truck                     |
| PATCH  | `/api/v1/trucks/{truck_id}`                      | `truck_controller.py:update_truck`                   | Owner/Fleet; state restrictions                      | Update truck                   |
| GET    | `/api/v1/trucks/{truck_id}/maintenance`          | `truck_controller.py:list_truck_maintenance`         | Owner/Fleet/Dispatcher                               | Read maintenance history       |
| POST   | `/api/v1/trucks/{truck_id}/maintenance`          | `truck_controller.py:start_truck_maintenance`        | Owner/Fleet; availability restrictions               | Start maintenance              |
| POST   | `/api/v1/trucks/{truck_id}/maintenance/complete` | `truck_controller.py:complete_truck_maintenance`     | Owner/Fleet                                          | Complete maintenance           |

### 5.6 Dispatch and trip progress

Handlers below reside in `src/backend/src/Controller/trip_controller.py`.

| Method | Path                                        | Handler                   | Authentication / role                                            | Description                                                       |
| ------ | ------------------------------------------- | ------------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------------- |
| GET    | `/api/v1/dispatch/resources`                | `read_dispatch_resources` | `dispatch.assign`; Owner/Dispatcher                              | Resource availability and reasons                                 |
| GET    | `/api/v1/trips`                             | `list_trips`              | `dispatch.assign`; Owner/Dispatcher                              | Dispatch trip list                                                |
| GET    | `/api/v1/trips/assigned`                    | `list_assigned_trips`     | `trip.assignment_view`; Driver/Helper own; Owner/Dispatcher view | Scope-filtered trip list; non-OWN grants can see the broader list |
| GET    | `/api/v1/trips/{trip_id}`                   | `read_trip`               | Same capability; OWN restricted to assigned crew                 | Read trip                                                         |
| POST   | `/api/v1/delivery-orders/{order_id}/trips`  | `assign_trip`             | `dispatch.assign FULL`; Owner/Dispatcher                         | Assign order load, truck and crew                                 |
| POST   | `/api/v1/trips/{trip_id}/accept`            | `accept_trip`             | `trip.progress OWN`; assigned Driver                             | Accept Scheduled trip                                             |
| POST   | `/api/v1/trips/{trip_id}/clear-dispatch`    | `clear_trip_dispatch`     | `dispatch.assign FULL`; Owner/Dispatcher                         | Clear Accepted trip after eligibility checks                      |
| POST   | `/api/v1/trips/{trip_id}/depart`            | `depart_trip`             | `trip.progress OWN`; assigned Driver                             | Record departure                                                  |
| POST   | `/api/v1/trips/{trip_id}/deliver`           | `deliver_trip`            | `trip.progress OWN`; assigned Driver                             | Record delivery                                                   |
| POST   | `/api/v1/trips/{trip_id}/cancel`            | `cancel_trip`             | `trip.cancel_or_fail FULL`; Owner/Dispatcher                     | Cancel an eligible pre-departure trip with reason                 |
| POST   | `/api/v1/trips/{trip_id}/fail`              | `fail_trip`               | Same capability; Owner/Dispatcher                                | Fail an eligible departed trip with reason                        |
| PUT    | `/api/v1/trips/{trip_id}/crew`              | `change_trip_crew`        | `dispatch.assign FULL`; Owner/Dispatcher                         | Change eligible pre-departure crew                                |
| POST   | `/api/v1/trips/{trip_id}/truck-replacement` | `replace_trip_truck`      | `truck.replace FULL`; Owner/Dispatcher                           | Replace truck on an eligible trip                                 |

### 5.7 OR and receipt endpoints

Handlers reside in `src/backend/src/Controller/or_controller.py`.

| Method | Path                                                     | Handler                        | Authentication / role                                                       | Description                                                    |
| ------ | -------------------------------------------------------- | ------------------------------ | --------------------------------------------------------------------------- | -------------------------------------------------------------- |
| POST   | `/api/v1/trips/{trip_id}/or-documents`                   | `upload_or_document`           | `or.upload OWN`; assigned Driver or enabled assigned Helper; upload budgets | Multipart `file` and optional `kind` (default `SIGNED_OR`)     |
| GET    | `/api/v1/trips/{trip_id}/or-documents`                   | `list_or_documents`            | `or.view_files`; Owner/Dispatcher/Accounting view; authorized crew own      | List authorized metadata; OWN view excludes superseded history |
| GET    | `/api/v1/trips/{trip_id}/or-documents/{document_id}/url` | `issue_or_document_url`        | Same capability and scope                                                   | Issue short-lived signed link                                  |
| POST   | `/api/v1/trips/{trip_id}/confirm-receipt`                | `confirm_receipt`              | `or.confirm_receipt OWN`; assigned Driver                                   | Confirm `received_at`; requires `Idempotency-Key`              |
| POST   | `/api/v1/trips/{trip_id}/receipt-correction`             | `correct_receipt_confirmation` | `or.correct_confirmation FULL`; Owner                                       | Correct eligible mistaken receipt with reason                  |

`Idempotency-Key` must be 8–128 characters matching `^[A-Za-z0-9_-]+$`. Repeated confirmation with the same actor/key is handled by the service/ledger; ownership and receipt-time/state rules still apply.

Many collection endpoints use `limit` and `offset` (typically default limit 50, maximum 100, offset 0–100000). Filters differ per route; consult the snapshot rather than applying one universal filter contract.

Errors are rendered by `src/backend/src/problem_details.py` as `application/problem+json`, with stable `code` and `trace_id`. Typical responses include `401` missing/invalid token, `403` access denial, `404` missing/hidden record, `409` workflow conflict, `413` oversized data, `422` validation error, `429` rate limit and `503` unavailable provider/database. Successful create routes shown in decorators use `201`; other normal responses generally use `200`.

## 6. User Roles, Permissions & Security

### 6.1 Role model and assignment rules

Every distinct role is listed in Section 1.2. Runtime grants come from database `role_permissions`, seeded by `src/backend/src/Data/permission_matrix.json`, and are interpreted by `src/backend/src/Service/authorization_service.py`.

The service filters disabled conditional grants and selects the strongest access level per capability: `FULL > VIEW > LTD > OWN`. Routes may additionally require an exact level such as `OWN`; a higher-ranked grant is not an ownership bypass. The matrices below describe single-role behavior. Combined roles must be evaluated against both effective grants and route-specific level filters.

`src/backend/src/Entity/role_rules.py` flags HR+Accounting, Dispatcher+HR, Dispatcher+Accounting, and field-role/back-office combinations. The Owner role-assignment service requires an exception reason for forbidden combinations and audits the exception. It also prevents an Owner removing their own Owner role. These rules are not implemented through Clerk metadata.

### 6.2 Effective implemented access matrix

**F** = permitted full action within business rules; **V** = read; **L** = limited projection; **O** = own/assigned records; **A** = authenticated active employee; **—** = no listed action grant. **†** requires `HELPER_OR_UPLOAD_ENABLED=true` and the relevant conditional grant.

| Module / action                                   | Owner | Dispatcher | Fleet | Driver | Helper | HR  | Accounting |
| ------------------------------------------------- | ----- | ---------- | ----- | ------ | ------ | --- | ---------- |
| `/me` current account                             | A     | A          | A     | A      | A      | A   | A          |
| Clients/orders read                               | V     | V          | —     | —      | —      | —   | V          |
| Clients/orders create/update/cancel               | —     | F          | —     | —      | —      | —   | —          |
| Employees list/read                               | F     | L          | L     | O      | O      | F   | —          |
| Employee contact create/update                    | F     | —          | —     | —      | —      | F   | —          |
| Roles, identity linking, activation/deactivation  | F     | —          | —     | —      | —      | —   | —          |
| Trucks/maintenance read                           | V     | V          | V     | —      | —      | —   | —          |
| Trucks/maintenance write                          | F     | —          | F     | —      | —      | —   | —          |
| Driver license read                               | F     | L          | F     | O      | —      | V   | —          |
| Driver license save                               | F     | —          | F     | —      | —      | —   | —          |
| Dispatch list/resources/assignment/clearance      | F     | F          | —     | —      | —      | —   | —          |
| Trip detail / assignment-view API                 | V     | V          | —     | O      | O      | —   | —          |
| Accept/depart/deliver                             | —     | —          | —     | O      | —      | —   | —          |
| Crew changes, truck replacement, trip cancel/fail | F     | F          | —     | —      | —      | —   | —          |
| OR metadata/signed URL reads                      | V     | V          | —     | O      | O†     | —   | V          |
| OR upload                                         | —     | —          | —     | O      | O†     | —   | —          |
| Confirm company receipt                           | —     | —          | —     | O      | —      | —   | —          |
| Correct mistaken receipt                          | F     | —          | —     | —      | —      | —   | —          |
| Audit log / permission-matrix read                | F     | —          | —     | —      | —      | —   | —          |

The corresponding route families and handlers are in Section 5. Important UI/API distinctions:

- Driver/Helper own employee APIs do not create a general People page; **My account** is the normal profile entry point.
- Dispatcher has `VIEW` seed entries for progress/upload/receipt capabilities, but those POST routes require `OWN`; Dispatcher cannot perform the Driver's action.
- Accounting's OR-read API permission does not provide a general trip list or a dedicated document browser in the current UI.
- Driver own-license API access does not imply a Driver license editor.
- Owner-only order entry is denied; an order-entry user needs the applicable Dispatcher grant.

### 6.3 Seeded financial/report permissions — not persistent features

The following entries exist in the permission seed, but there are no corresponding financial transaction APIs/tables. They must not be documented as working financial processing.

| Seed capability                                          | Owner | Dispatcher | Fleet | Driver | Helper | HR  | Accounting |
| -------------------------------------------------------- | ----- | ---------- | ----- | ------ | ------ | --- | ---------- |
| `expense.enter`                                          | F     | F          | —     | O      | —      | —   | —          |
| `expense.approve`, `charge.finalize`, `client_rate.view` | F     | —          | —     | —      | —      | —   | F          |
| `earning_percentage.set`                                 | F     | —          | —     | —      | —      | —   | —          |
| `payroll.view_others`                                    | F     | —          | —     | —      | —      | F   | —          |
| `payroll.view_own`                                       | —     | —          | —     | O      | O      | —   | —          |
| `deduction.record`                                       | F     | —          | —     | —      | —      | F   | —          |
| `deduction.approve`                                      | F     | —          | —     | —      | —      | —   | —          |
| `payroll_adjustment.prepare`                             | —     | —          | —     | —      | —      | F   | —          |
| `cash_advance.request`                                   | —     | —          | —     | O      | O      | F   | —          |
| `cash_advance.approve`                                   | F     | —          | —     | —      | —      | —   | —          |
| `cash_advance.release_repay`, `payroll_payment.record`   | —     | —          | —     | —      | —      | F   | —          |
| `billing.manage`                                         | V     | —          | —     | —      | —      | —   | F          |
| `invoice.void_approve`                                   | F     | —          | —     | —      | —      | —   | —          |
| `report.view`                                            | F     | F          | F     | O      | O      | F   | F          |

`src/frontend/src/shared/utils/navigation.js` marks financial/report pages as previews. Reports navigation accepts FULL/VIEW, so seeded OWN report grants do not expose that page to Driver/Helper. Future enforcement, persistence and acceptance for these capabilities are **[To be completed by team]**.

### 6.4 Authentication, sessions and webhook trust

- `clerkSessionService.jsx` wraps `ClerkProvider`, `SignIn`, `UserButton`, `useAuth` and signed-in/out `Show` gates. Sign-in is hosted by the Clerk SDK within the application.
- No application `/login`, `/register` or password-reset API is declared. Registration options, identity-provider policy, MFA and Clerk cookie configuration are external settings: **[To be completed by team]**.
- The token bridge registers Clerk's `getToken()` with Axios; application code attaches an explicit bearer header. The reviewed app does not implement a separate local password/session database.
- `clerk_token_verifier.py` accepts RS256, requires `exp`, `iat`, `sub` and checks issuer. Audience and authorized-party checks depend on configuration. JWKS verification failures and provider outages have distinct errors.
- `authentication_service.py` denies absent/invalid tokens and identities not linked to an active employee. UI gates are convenience controls; backend capability and service-level ownership/state checks are authoritative.
- `clerk_webhook_verifier.py` verifies raw-body Svix signatures before accepting JSON. `clerk_webhook_service.py` tracks event IDs, links existing employees by verified primary email when safe and deactivates deleted linked identities. It does not create an employee or grant business roles to every new Clerk sign-up.

### 6.5 CSRF, XSS, input and storage controls

| Concern            | Verified implementation / limit                                                                                                                                                                                                                                                                                                                |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CSRF               | No custom CSRF-token middleware is present in the reviewed app. Protected APIs require the explicit Authorization header rather than an application cookie session. This is not a claim about Clerk's internal cookie protections; reassess if cookie-authenticated business endpoints are added. CORS is not a substitute for authentication. |
| XSS                | Record values are rendered through JSX; no `dangerouslySetInnerHTML`/direct `innerHTML` sink was found in reviewed application source. No application CSP is configured in the supplied frontend HTML or API headers. Host-level CSP and provider-compatible policy are [To be completed by team].                                             |
| Validation         | Pydantic DTOs validate UUIDs, enums, field lengths/patterns, positive weights and Helper list bounds. Services validate ownership, licenses, capacity and legal transitions. See `src/backend/src/DTO/`.                                                                                                                                       |
| Field exposure     | Explicit response models and limited employee/license projections avoid returning every persistence field. `employee_controller.py` projects LTD records separately.                                                                                                                                                                           |
| Uploads            | File limit defaults to 5,242,880 bytes. Pillow checks magic bytes/decoding, limits pixels to 50,000,000, applies orientation and re-encodes images without supplied metadata. See `Infrastructure/Imaging/pillow_image_sanitizer.py`.                                                                                                          |
| Private files      | Backend-only Supabase key; randomized application storage paths, authorization before signed URLs, configurable URL lifetime and document supersession. Files are not public database blobs.                                                                                                                                                   |
| Bodies             | Overall cap is configured upload size plus 1 MiB overhead. Webhook-specific limit defaults to 262,144 bytes.                                                                                                                                                                                                                                   |
| API headers/errors | Trace ID plus `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`; handled error responses avoid raw SQL/stack disclosure. These API headers do not configure the separately served frontend host.                                                                           |
| Database           | SQLAlchemy persistence; FK/check/unique constraints; migration-based audit immutability and PostgreSQL Data API lockdown.                                                                                                                                                                                                                      |
| Secrets            | Root/backend secrets are not `VITE_*` settings. `.gitignore` excludes `.env`, environments and generated output. Exact production secret storage/rotation is [To be completed by team].                                                                                                                                                        |

### 6.6 Rate limiting and proxy boundaries

`rate_limiter.py` implements atomic, bounded, in-memory 60-second budgets. `providers.py` applies them by peer and verified employee; upload budgets precede handler file reads/sanitization/storage, though multipart parsing may already have occurred.

| Budget                             | Default per minute |
| ---------------------------------- | ------------------ |
| Failed authentication / peer       | 20                 |
| Protected API attempts / peer      | 600                |
| Authenticated API calls / employee | 120                |
| Webhook attempts / peer            | 120                |
| Upload attempts / peer             | 30                 |
| Upload attempts / employee         | 10                 |

Over-budget responses use `429`, `RATE_LIMITED` and `Retry-After: 60`. Counters are capped at 10,000 keys and 100,000 timestamps; saturation rejects admission rather than clearing existing blocks. Limits are validated between 1 and 1000.

The supplied backend launcher/container commands disable forwarded-header trust by default. Application code does not directly derive quota keys from arbitrary `X-Forwarded-For`. Trusted ingress configuration, shared budgets across replicas, TLS/HSTS and network isolation are deployment work: **[To be completed by team]**. A process restart resets local counters.

## 7. Local Setup & Installation Guide

### 7.1 Prerequisites and clone

Use Python 3.12 and Node 22 to match CI, Git, and either an accessible PostgreSQL database or Docker with Compose for the development database. Node 20 is selected by the current frontend Dockerfile; runtime alignment remains a team decision. Commands below are for Windows PowerShell and describe actions for the reader to perform.

```powershell
git clone https://github.com/DanielVilla1/BM_Enterprises_Integration.git
cd BM_Enterprises_Integration
```

For a fresh clone, copy the template. Preserve existing local configuration when updating an existing checkout.

```powershell
Copy-Item .env.example .env
```

### 7.2 Environment variables

Sources: `.env.example`, `src/backend/src/config.py`, `src/frontend/vite.config.js`, `shared/services/clerkConfig.js`, `shared/services/httpClient.js`, `compose.yml` and test configuration. Defaults are not proof that a feature works without its provider credentials. No real credentials are included below.

| Variable                                   | Default/example or requirement                                                               | Purpose / scope                                                             |
| ------------------------------------------ | -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `DATABASE_URL`                             | Backend fallback `sqlite:///./dev.db`; supply PostgreSQL URL for native PostgreSQL operation | Backend; consumed by config but absent from template; Compose constructs it |
| `ENVIRONMENT`                              | `development`                                                                                | Environment label; does not automatically disable docs or configure hosting |
| `CORS_ALLOWED_ORIGINS`                     | `http://localhost:5173`; comma-separated                                                     | Allowed browser origins                                                     |
| `ENABLE_API_DOCS`                          | `true`                                                                                       | Controls docs/schema exposure                                               |
| `CLERK_ISSUER`                             | Clerk instance issuer; required for functional token verification                            | Backend                                                                     |
| `CLERK_JWKS_URL`                           | Instance JWKS URL                                                                            | Backend verification keys                                                   |
| `CLERK_AUTHORIZED_PARTIES`                 | Template `http://localhost:5173`; config default empty tuple                                 | Configure intended browser origins; empty skips this check                  |
| `CLERK_AUDIENCE`                           | Empty unless configured                                                                      | Optional audience enforcement                                               |
| `CLERK_WEBHOOK_SECRET`                     | Server-only signing secret                                                                   | Required for accepted webhook signatures                                    |
| `CLERK_SECRET_KEY`                         | Server-only Clerk key                                                                        | Identity directory/reconciliation operations                                |
| `CLERK_API_BASE_URL`                       | `https://api.clerk.com`                                                                      | Optional directory base override; config-only                               |
| `CLERK_CLOCK_SKEW_SECONDS`                 | `5`                                                                                          | JWT clock allowance; config-only                                            |
| `SUPABASE_URL`                             | Project URL                                                                                  | Required for live file storage                                              |
| `SUPABASE_SERVICE_KEY`                     | Server-only storage credential                                                               | Never copy to frontend configuration                                        |
| `SUPABASE_BUCKET`                          | `delivery-documents`                                                                         | Must match an existing private bucket                                       |
| `SIGNED_URL_TTL_SECONDS`                   | `120`                                                                                        | Signed document URL lifetime                                                |
| `MAX_UPLOAD_BYTES`                         | `5242880`                                                                                    | File cap; config-only                                                       |
| `MAX_WEBHOOK_BODY_BYTES`                   | `262144`                                                                                     | Webhook body cap; config-only                                               |
| `HELPER_OR_UPLOAD_ENABLED`                 | `false`                                                                                      | Conditional Helper upload/document access; config-only                      |
| `RATE_LIMIT_FAILED_AUTH_PER_MINUTE`        | `20`                                                                                         | Failed authentication / peer                                                |
| `RATE_LIMIT_WEBHOOK_PER_MINUTE`            | `120`                                                                                        | Webhook attempts / peer                                                     |
| `RATE_LIMIT_API_IP_PER_MINUTE`             | `600`                                                                                        | Protected attempts / peer                                                   |
| `RATE_LIMIT_API_USER_PER_MINUTE`           | `120`                                                                                        | Calls / verified employee                                                   |
| `RATE_LIMIT_UPLOAD_IP_PER_MINUTE`          | `30`                                                                                         | Upload attempts / peer                                                      |
| `RATE_LIMIT_UPLOAD_USER_PER_MINUTE`        | `10`                                                                                         | Upload attempts / employee                                                  |
| `POSTGRES_DB`                              | `bm_enterprises`                                                                             | Compose database initialization                                             |
| `POSTGRES_USER`                            | `bm_app`                                                                                     | Compose database account, not an app sign-in                                |
| `POSTGRES_PASSWORD`                        | Replace template placeholder                                                                 | Compose database secret                                                     |
| `POSTGRES_PORT`                            | `5432`                                                                                       | Database port used inside Compose connection URL                            |
| `POSTGRES_EXTERNAL_PORT`                   | `5432`                                                                                       | Published host port; may differ from internal port                          |
| `DB_HOST`                                  | `db`                                                                                         | Compose service hostname; not a native Windows hostname                     |
| `BACKEND_EXTERNAL_PORT`                    | `8000`                                                                                       | Published API port                                                          |
| `FRONTEND_EXTERNAL_PORT`                   | `5173`                                                                                       | Published UI port                                                           |
| `PGADMIN_EXTERNAL_PORT`                    | `5050`                                                                                       | Optional pgAdmin host port                                                  |
| `PGADMIN_DEFAULT_EMAIL`                    | Replace template admin email as appropriate                                                  | pgAdmin login only                                                          |
| `PGADMIN_DEFAULT_PASSWORD`                 | Replace template placeholder                                                                 | pgAdmin login only                                                          |
| `VITE_CLERK_PUBLISHABLE_KEY`               | Public Clerk key                                                                             | Required for frontend sign-in; available during build/dev startup           |
| `VITE_API_BASE_URL`                        | Template `http://localhost:8000`; empty for native same-origin proxy                         | Public browser API origin                                                   |
| `VITE_PUBLIC_FRONTEND_URL`                 | Empty or exact public origin                                                                 | Optional Vite hostname allowlist input                                      |
| `TEST_DATABASE_URL`                        | Unset for normal SQLite tests                                                                | Optional isolated PostgreSQL test database; not the operational database    |
| `CHOKIDAR_USEPOLLING`, `CHOKIDAR_INTERVAL` | Compose supplies `true`, `100`                                                               | Container file-watch settings, not required root template entries           |

GitHub supplies `secrets.GITHUB_TOKEN` to the CI secret-scanning action; it is not an application `.env` credential.

### 7.3 Prepare database and external services

For a Compose-managed development database, fill the `POSTGRES_*` variables, then:

```powershell
docker compose up -d db
docker compose exec db pg_isready -U bm_app -d bm_enterprises
```

Use the configured names if different from the template; wait until PostgreSQL accepts connections. Alternatively, use an existing PostgreSQL instance with a suitable database/account. Native database provisioning policy is **[To be completed by team]**.

For a native API connecting to the published development database, add a root setting with the actual host port and URL-encoded password:

```dotenv
DATABASE_URL=postgresql+psycopg2://bm_app:URL_ENCODED_PASSWORD@127.0.0.1:5432/bm_enterprises
```

Replace the placeholder. `DB_HOST=db` belongs to container networking; native connections normally use the published address. `.env.example` does not automatically assemble a native `DATABASE_URL`.

Configure a Clerk development application and supply its public/backend verification settings. Create the intended first Owner's Clerk identity and obtain its user ID. Exact Clerk dashboard settings, enabled sign-in providers and verification policy are **[To be completed by team]**.

Create a **private** Supabase bucket matching `SUPABASE_BUCKET`, and set backend storage credentials. Alembic creates application tables; it does not provision a Supabase bucket. Do not place server keys in `VITE_*` variables.

### 7.4 Install Python dependencies and migrate

From the repository root:

```powershell
py -3.12 -m venv src/backend/.venv
./src/backend/.venv/Scripts/python.exe -m pip install -r src/backend/requirements-dev.txt
./src/backend/.venv/Scripts/python.exe tools/scripts/backend.py alembic -c src/backend/alembic.ini upgrade head
```

Migrations seed roles and permission grants. No separate financial or demo-account seeder is declared. Use the launcher to preserve `backend.*` imports and root `.env` lookup.

On an empty employee database only, bootstrap the first Owner with the actual Clerk user ID:

```powershell
./src/backend/.venv/Scripts/python.exe tools/scripts/backend.py backend.scripts.bootstrap_owner --name "First Owner" --email "owner@example.com" --clerk-user-id "user_REPLACE_ME"
```

Replace the example identity values before execution. `bootstrap_owner.py` refuses when employees already exist. It creates/links the application employee and grants Owner access; it does not create the Clerk password or identity. Do not rerun it as a general role-management command.

### 7.5 Start the API and frontend

Start the API from the root and keep its terminal open:

```powershell
./src/backend/.venv/Scripts/python.exe tools/scripts/backend.py uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

The launcher defaults to `--no-proxy-headers` unless an explicit proxy-header choice is supplied.

In a second terminal, install frontend dependencies and create `src/frontend/.env` containing only public settings:

```powershell
cd src/frontend
npm.cmd ci
```

```dotenv
VITE_CLERK_PUBLISHABLE_KEY=pk_test_REPLACE_WITH_PUBLIC_KEY
VITE_API_BASE_URL=
VITE_PUBLIC_FRONTEND_URL=
```

Then:

```powershell
npm.cmd run dev
```

Vite's current configuration loads its frontend environment, not the root `.env`, for native development. Restart Vite after changing these values. An empty API origin uses the native `/api/v1` proxy to port 8000; an explicit origin must match the running API and CORS configuration.

| Open                                  | Purpose                            |
| ------------------------------------- | ---------------------------------- |
| `http://localhost:5173`               | Real application sign-in/workspace |
| `http://localhost:8000/api/v1/health` | API health                         |
| `http://localhost:8000/api/v1/docs`   | Interactive API docs when enabled  |
| `http://localhost:5173/preview.html`  | Sample-only design preview         |

Sign in as the linked active Owner. Create additional employee records, assign roles, link existing Clerk identities and activate authorized users through **People**. Verify access through **My account**. A Clerk sign-in alone does not grant an employee role.

### 7.6 Validation and optional container workflow

From `src/backend/`:

```powershell
./.venv/Scripts/python.exe -m pytest -q
./.venv/Scripts/python.exe -m ruff check .
./.venv/Scripts/python.exe -m black --check .
```

From `src/frontend/`:

```powershell
npm.cmd run lint
npm.cmd run format:check
npm.cmd test
npm.cmd run build
```

From the root, run `python tools/scripts/check_docs.py` with an available Python interpreter. PostgreSQL test runs use `TEST_DATABASE_URL`; tests recreate the test schema, so use a disposable database, never operational data.

For an all-container development session, fill root `.env`, start/wait for the database, then run `docker compose up --build backend frontend pgadmin`. The backend startup command applies migrations. On a fresh database, bootstrap via `docker compose exec backend python -m backend.scripts.bootstrap_owner` with the same required identity arguments shown above.

Compose supplies `VITE_API_BASE_URL=http://localhost:${BACKEND_EXTERNAL_PORT}` for browser access. The native Vite proxy target `127.0.0.1:8000` is not the backend service address from inside the frontend container; changing Compose to an empty API origin also requires reviewing that proxy target. `depends_on` alone is not an explicit database health/readiness condition.

## 8. Deployment & Build Notes

### 8.1 Build and operator commands

| Area                    | Declared command / artifact                                             | Source                                                         |
| ----------------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------- |
| Frontend dev            | `npm run dev` → `vite`                                                  | `src/frontend/package.json`                                    |
| Frontend build          | `npm run build` → `vite build`; output under frontend `dist/`           | Package scripts/Vite                                           |
| Frontend preview        | `npm run preview` → `vite preview`                                      | Package scripts; no production server deployment defined       |
| Frontend quality        | `lint`, `test`, `format:check`                                          | ESLint, Vitest and Prettier                                    |
| Backend server          | Uvicorn `backend.main:app`                                              | `src/backend/main.py`; Dockerfile/launcher                     |
| Schema upgrades         | `alembic -c src/backend/alembic.ini upgrade head` through root launcher | Alembic configuration/migrations                               |
| API contract export     | `backend.scripts.export_openapi` through launcher                       | `src/backend/scripts/export_openapi.py`                        |
| Identity reconciliation | `backend.scripts.reconcile_clerk` through launcher                      | `src/backend/scripts/reconcile_clerk.py`; schedule not defined |
| Documentation checks    | `python tools/scripts/check_docs.py`                                    | Repository tool                                                |

`VITE_*` settings are frontend build inputs. Changing a production container environment after a static build does not establish a runtime settings injection mechanism; none is implemented here. Ensure the intended public Clerk key and API origin are provided before building.

### 8.2 Supplied containers

| Service    | Implementation                                                                                      | Deployment implication                                                                                      |
| ---------- | --------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Backend    | `python:3.12-slim`; installs requirements, copies source under `/app/backend`, runs Uvicorn on 8000 | Standalone Dockerfile command does not apply migrations; Compose overrides it with migration+reload command |
| Frontend   | `node:20-alpine`; `npm install`, copies source, runs `npm run dev -- --host` on 5173                | Development server, not a defined static production hosting stage                                           |
| PostgreSQL | `postgres:15`, persistent `pgdata` volume, published host port                                      | Backup/restore, network isolation and production account policy need hosting design                         |
| pgAdmin    | `dpage/pgadmin4`, optional host port 5050                                                           | Administrative tool; do not treat as an end-user app module                                                 |

`compose.yml` bind-mounts source, enables reload/file watching and supplies root `.env` to backend and frontend containers. The latter gives the development frontend container the whole root environment; production configuration should restrict it to required public/build inputs. That is not a claim that all those values are automatically exposed in the browser bundle.

The supplied Dockerfiles do not define a production frontend reverse proxy, TLS termination, shared limiter store, secret manager, release rollback process or production deployment account. Those details are **[To be completed by team]**.

### 8.3 CI workflow

`.github/workflows/ci.yml` runs on pull requests and pushes to `main`, with read-only repository contents permission.

| Job      | Checks                                                                                                                                                                            |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Backend  | Python 3.12; development requirements; Ruff; Black; repository-tool checks; Markdown links; SQLite tests; PostgreSQL tests against PostgreSQL 16; `pip-audit -r requirements.txt` |
| Frontend | Node 22; `npm ci`; ESLint; formatting; Vitest; production build; `npm audit --omit=dev --audit-level=high`                                                                        |
| Secrets  | Full-history checkout and `gitleaks/gitleaks-action@v2`, using GitHub's supplied token                                                                                            |

The frontend CI audit excludes development dependencies; it does not establish a clean full-toolchain audit. Record full development dependency findings as part of release review. The workflow has no deployment job, artifact-publishing stage or hosting credentials configured in its steps. CI passing is not deployment approval.

### 8.4 Production configuration gaps and release gate

| Item                                                        | Repository position / required decision                                                                                       |
| ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Provider, domain, region and production URL                 | [To be completed by team]                                                                                                     |
| Exact runtime/database versions and immutable image digests | [To be completed by team]; current Node and PostgreSQL majors differ between Compose and CI                                   |
| Frontend production serving                                 | [To be completed by team]; current container runs Vite development server                                                     |
| API origin and HTTPS                                        | Configure public build-time API origin or reviewed same-origin reverse proxy; TLS/HSTS policy [To be completed by team]       |
| CORS and Clerk origins                                      | Configure exact intended origins and issuer/JWKS/audience/authorized-party policy; no wildcard authorization assumption       |
| API docs                                                    | Explicit production `ENABLE_API_DOCS` decision; `ENVIRONMENT=production` alone does not turn them off                         |
| Secrets                                                     | Production secret storage, rotation, least privilege and separation from preview environments [To be completed by team]       |
| Worker count and rate limits                                | Built-in budgets are per process; shared ingress/store and proxy trust must be designed before scaling                        |
| Database operations                                         | Migration execution/readiness, backups, restore drills, access isolation and rollback compatibility [To be completed by team] |
| Storage                                                     | Validate actual private-bucket upload, signed URL expiry, metadata handling and access denial                                 |
| Browser policy                                              | Host-level frontend CSP/security headers and Clerk-compatible configuration [To be completed by team]                         |
| Monitoring                                                  | Logs, alerts, health/readiness, retention and reconciliation scheduling [To be completed by team]                             |
| Release scope                                               | Financial modules remain previews; real financial processing is not implemented                                               |

Use [the QA acceptance checklist](../runbooks/qa.md) for role/workflow, ownership, upload, retry, receipt correction, rate-limit, recovery and release cases. Record real test evidence against the final commit. Developer-run results in [verification](../runbooks/verification.md) do not constitute QA sign-off.

Deployment/hosting should follow successful required QA cases, resolved or explicitly approved release findings, and QA/business approval of the exact commit and operational scope. Production hosting is not claimed to be configured or approved by this document.
