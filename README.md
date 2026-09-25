# BM Enterprises Integration Architecture Proposal

**Integrated Truck Hauling Dispatch, Proof of Delivery, Payroll, and Billing Management System**

Systems Integration and Architecture 2 — Section TB42
Professor Jocelyn Tejada — September 2026

**Authors:** Adrian Aldave, Karmelo Cortes, Jefferson Petronio, John Patrick San Roque, Daniel Villa

## Proposal Scope

A modular web application for a ten-truck subcontracted hauling company, with documented interfaces to authentication, document storage, and mapping services.

## Executive Summary

BM Enterprises is a subcontracted trucking hauler (~10 trucks) working for a steel company client. It assigns trucks/drivers, monitors deliveries, collects proof of delivery, records driver compensation, and prepares invoices. This system brings those activities into one controlled workflow.

**Stack:**
- React administrative portal + React PWA for drivers
- FastAPI backend (single source of truth for validation, authorization, business rules)
- PostgreSQL on Supabase (system of record)
- Clerk for identity/auth
- Supabase Storage for private delivery documents
- Mapping service for address lookup, route distance, ETA

**Architecture:** Three-tier modular monolith (delivery, fleet, payroll, billing, maintenance, reporting logic kept in one backend, separated by module) — chosen over microservices as appropriate for this team/operation size.

## Organizational Context

The steel company's system is **not** integrated in v1 — dispatchers encode delivery orders manually. This avoids dependency on external access BM Enterprises doesn't control. Manual coordination today causes: inaccurate truck/driver visibility, overloaded trucks, duplicate data entry, lost/delayed receipts, inconsistent billing calculations, and no unified management view.

## Modules

| Module | Responsibility | Primary Users |
|---|---|---|
| Delivery order management | Client order, locations, schedule, steel weight, hauling rate | Dispatcher |
| Fleet and driver management | Truck capacity, availability, maintenance, license details, assignments | Fleet Manager, Dispatcher |
| Dispatch and trips | Splits orders into trips, assigns eligible truck/driver | Dispatcher |
| Proof of delivery | Receipt details and delivery images for approval | Driver, Dispatcher |
| Payroll | Trip allowance entries, payroll periods | HR and Payroll |
| Billing | Amount due, invoices, payments | Accounting |
| Reports | Deliveries, utilization, payroll, revenue, expenses | Manager |

### System Boundaries
- React clients consume the FastAPI contract only — no direct DB access, no privileged credentials.
- FastAPI owns validation, authorization, capacity checks, status transitions, payroll/billing rules, audit.
- PostgreSQL is system of record; Supabase Storage is a separate service despite shared provider.
- Clerk owns login/session identity; BM Enterprises owns roles/permissions in PostgreSQL.

### Alternatives Considered
| Alternative | Decision | Reason |
|---|---|---|
| Separate spreadsheets/standalone modules | Rejected | Duplicate records, no reliable audit trail |
| Multiple microservices | Rejected (for now) | Unjustified deployment/monitoring overhead for 10 trucks |
| Three-tier modular monolith | **Selected** | Transactional integrity + logically separated, testable modules |

### Scope Measures
~13 internal API groups, ~61 REST endpoints total design; first prototype targets ~35–40 endpoints.

## Architecture & Integration Interfaces

| Integration point | Protocol/format | Data exchanged |
|---|---|---|
| React → FastAPI | HTTPS REST + JSON | Orders, assignments, trip updates, payroll/billing requests, reports |
| React → FastAPI (upload) | HTTPS multipart form | Receipt image, receipt number, recipient name, received time |
| Clerk → FastAPI | Bearer JWT + signed webhook | User identity, session claims, account lifecycle events |
| FastAPI → PostgreSQL | SQLAlchemy | Employees, trucks, orders, trips, payroll, invoices, expenses, audit |
| FastAPI → Supabase Storage | HTTPS object storage | Private receipt images and delivery documents |

### Authentication & Authorization Flow
1. Employee signs in through Clerk.
2. React receives a Clerk session token.
3. React sends the token to FastAPI in the `Authorization` header.
4. FastAPI verifies signature, issuer, expiration, audience, authorized party.
5. FastAPI maps the Clerk subject ID to an active employee record.
6. FastAPI applies the employee's role from PostgreSQL.
7. FastAPI performs the operation and writes an audit record when required.

### Operational Workflow
1. Dispatcher encodes the delivery order from the steel company.
2. System validates weight, date, and client info.
3. Dispatcher assigns trips based on truck capacity/availability.
4. Driver accepts and updates trip progress.
5. Driver uploads receipt + recipient details after delivery.
6. Dispatcher reviews and completes the trip.
7. System releases the truck, records trip allowance, updates order progress, and flags the order for invoicing once all trips are complete.

## Interface Contract & Standards

Maintained as an **OpenAPI 3.1** document, published by FastAPI at `/api/v1/openapi.json`.

| Area | Convention |
|---|---|
| Versioning | All endpoints under `/api/v1`; breaking changes require a new major version |
| Data format | JSON, snake_case; file uploads via multipart form data |
| Identifiers | UUIDs |
| Time | ISO 8601, UTC |
| Measurements | Weight in metric tons, distance in kilometres |
| Money | Philippine pesos, fixed-precision DB columns; rates/allowances are configurable records |
| Authentication | Clerk bearer token + local employee role check |
| Errors | `application/problem+json` (type, title, status, detail, error code, trace ID) |
| Retries | Idempotency key required on completion operations |
| Compatibility | No removing/renaming required fields within v1; new fields must be optional |

### Coding Standards
- **Backend:** PEP 8, type hints, routes separated from services/repositories; Pydantic for validation; Ruff + Black; SQLAlchemy + Alembic for migrations.
- **Frontend:** TypeScript strict mode, ESLint, Prettier; PascalCase components, camelCase functions/vars; API calls isolated in service modules.
- All changes via reviewed PRs; CI runs formatting, linting, type checks, unit/contract/integration tests before merge.

### Status Model
| Record | Permitted statuses |
|---|---|
| Delivery order | PENDING → PARTIALLY_ASSIGNED → SCHEDULED → IN_PROGRESS → COMPLETED / CANCELLED |
| Trip | SCHEDULED → DISPATCHED → IN_TRANSIT → ARRIVED → POD_SUBMITTED → COMPLETED / FAILED / CANCELLED |
| Truck | AVAILABLE, ASSIGNED, IN_TRANSIT, MAINTENANCE |
| Invoice | DRAFT, ISSUED, PARTIALLY_PAID, PAID, VOID |

## Testing Strategy

| Test type | Purpose | Example |
|---|---|---|
| Unit | One function/class in isolation | Truck capacity function: 20t truck vs 25t load |
| Integration | Components working together | Trip completion via FastAPI + PostgreSQL record checks |
| Interface | Communication across a real boundary | Clerk token verification, receipt upload |
| Contract | Each side validated against shared OpenAPI spec | React request / FastAPI response vs same operation |

Contract tests run independently on both provider (FastAPI) and consumer (React) sides to catch interface drift early, before full integration.

**Tools:** Pytest + FastAPI TestClient, Vitest, a dedicated PostgreSQL test DB (via Alembic), mock/sandbox for Clerk & Supabase Storage, staging environment, deterministic seed data.

### Contract Clause Register
| Clause | Requirement |
|---|---|
| DO-01 | Valid delivery order → 201 + schema-valid PENDING order |
| TRIP-04 | Trip completion requires approved POD; returns documented representation |
| AUTH-01 | Valid Clerk identity must map to an active local employee |
| POD-01 | Only the assigned driver may upload an approved receipt for an eligible trip |
| DISPATCH-03 | Assigned load must not exceed registered truck capacity |
| TXN-01 | Completion commits all related records in one transaction, or none |
| IDEM-01 | Repeating a completion command with the same idempotency key can't duplicate effects |

### Key Test Cases
- **CT-01 Create Delivery Order** — `POST /api/v1/delivery-orders` → 201, schema-valid PENDING order (DO-01)
- **CT-02 Complete Trip** — `POST /api/v1/trips/{trip_id}/complete` with `Idempotency-Key` → 200, TripCompletion schema (TRIP-04, IDEM-01)
- **IT-01 Clerk Authentication** — `GET /api/v1/trips/assigned` with bearer token → 200, only that driver's trips (AUTH-01)
- **IT-02 Proof of Delivery Storage** — `POST /api/v1/trips/{trip_id}/proof-of-delivery` → private file storage, no public URL exposed (POD-01)
- **FP-01 Truck Capacity Failure** — overloading a truck → 409 `CAPACITY_EXCEEDED`, no assignment created (DISPATCH-03)
- **FP-02 Completion Transaction Failure & Retry** — DB failure mid-commit → 503, no partial change; retry succeeds exactly once (TXN-01, IDEM-01)

## Scrum Working Arrangement

Two-week sprints, each delivering a vertical slice (UI + API + DB + tests).

**Definition of Done:**
- Acceptance criteria demonstrated
- Peer code review
- Formatting/linting/type checks pass
- Unit + affected integration tests pass
- Affected interface/contract tests pass
- OpenAPI contract & examples match implementation
- Migrations apply cleanly
- Role/permission checks present
- Works in shared staging
- No open critical defects

## Principal Technical Risk

**Operational/financial data desynchronization during delivery completion** — one completion touches trip, truck availability, order progress, POD, trip allowance, invoice eligibility, audit log, and a notification record. A failure mid-process could release a truck without recording pay, or duplicate an allowance/invoice.

### Mitigations
- Receipt uploaded before the completion transaction begins
- Private storage bucket; only the object reference is stored in PostgreSQL
- Single PostgreSQL transaction covers trip, truck, order progress, payroll, invoice eligibility, audit log, and outbox record
- Idempotency key required on the completion endpoint
- Unique DB constraints prevent duplicate payroll/invoice entries
- Transactional outbox pattern (PostgreSQL-backed, no separate broker needed initially) for post-commit notifications
- Audit records for completion/financial changes
- Failure-path tests cover DB, storage, auth, and mapping interruptions

### Security Requirements
HTTPS, Clerk token validation, role-based access control, secrets in environment variables, file type/size validation, audit logging for financial changes, regular DB backups, rate limits on auth and public endpoints. Drivers cannot view other employees' salary records.

## Development Roadmap

| Sprint | Primary Delivery |
|---|---|
| 1 | Project skeleton, OpenAPI contract, Clerk auth, employees, roles |
| 2 | Clients, trucks, drivers, delivery order encoding |
| 3 | Dispatch, capacity validation, trip assignment, trip statuses |
| 4 | Proof of delivery, private storage, approval |
| 5 | Trip allowances, payroll periods, billing, invoices, payments |
| 6 | Reports, security review, staging validation, presentation prep |

## Conclusion

A modular monolith gives BM Enterprises one controlled operational record with clear contracts to independently managed services (Clerk, Supabase Storage, mapping). OpenAPI, versioned endpoints, standard error responses, contract tests, and CI prevent interface drift. Release 1 focuses on auth, fleet records, delivery orders, dispatch, trip status, POD, and a basic dashboard — payroll, billing, mapping, and advanced reports follow once the core delivery workflow is stable.

## References

- [Clerk — Verify token documentation](https://clerk.com/docs/reference/backend/verify-token)
- [FastAPI — Metadata and documentation URLs](https://fastapi.tiangolo.com/tutorial/metadata/)
- [OpenAPI Initiative — OpenAPI Specification 3.1](https://spec.openapis.org/oas/v3.1.0.html)
- [RFC 9457 — Problem Details for HTTP APIs](https://www.rfc-editor.org/info/rfc9457/)
- [SQLAlchemy — Transactions and Connection Management](https://docs.sqlalchemy.org/en/stable/orm/session_transaction.html)
- [Supabase — Storage access control](https://supabase.com/docs/guides/storage/security/access-control)
- [Richardson, Chris — Transactional outbox pattern](https://microservices.io/patterns/data/transactional-outbox.html)
- [GitHub — Continuous integration with GitHub Actions](https://docs.github.com/en/actions/get-started/continuous-integration)
