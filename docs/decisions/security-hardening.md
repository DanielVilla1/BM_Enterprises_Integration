# Security hardening and remaining release gates

[QA acceptance](../runbooks/qa.md) · [Verification](../runbooks/verification.md) · [Architecture](../architecture.md)

**Review date: 18 November 2026.** Scope: the recorded rate-limit review plus Sprint 5–6 financial authorization, transaction/idempotency controls, private-data responses, presentation isolation and dependency results. This is a focused developer review; it does not replace manual QA or hosting validation.

## Findings addressed

| Priority | Finding / consequence                                                                                      | Change and regression evidence                                                                                                                              |
| -------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| High     | Key-table saturation cleared all rate counters, allowing existing blocks to disappear                      | Reject new keys at capacity, reclaim expired entries and preserve other counters; key-saturation regression                                                 |
| Medium   | Separate record/count operations were non-atomic; rejected webhook traffic could keep growing event deques | Locked atomic admission; rejected requests add no events; total key/event memory caps; concurrent-admission and event-capacity regressions                  |
| Medium   | Successful API requests and image-processing/storage attempts had no dedicated quotas                      | Per-peer and verified-employee API budgets; separate upload budgets before file decoding/storage; independent-account and upload regressions                |
| Medium   | Trusting forwarding headers through the local Vite proxy could let a client choose its apparent address    | Shipped development launchers and container commands disable Uvicorn proxy headers by default; application quota keys never directly use forwarding headers |
| Low      | Sensitive API responses lacked explicit cache/sniffing/frame restrictions                                  | Problem-details/response-security middleware supplies no-store, nosniff, frame denial and no-referrer; success/throttle/financial regression checks         |

Implementation: [limiter](../../src/backend/src/rate_limiter.py), [dependency gates](../../src/backend/src/providers.py), [upload route](../../src/backend/src/Controller/or_controller.py), [problem-details middleware](../../src/backend/src/problem_details.py), [response-security middleware](../../src/backend/src/response_security.py), [regression tests](../../src/backend/tests/test_rate_limits.py).

JWT verification remains RS256-only with issuer, expiry, required claims and configured authorized-party checks. Local employee activation, capability grants, record ownership and trip state are enforced by the backend. Existing authentication, permission, OR-access, image-validation and PostgreSQL hardening tests remain part of the full suites. No authentication bypass was added for testing.

## Financial and presentation controls

| Boundary                     | Current protection / evidence                                                                                                                                                                                                            |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Function and property access | Separate read/write capabilities; explicit response DTOs; Owner expenses Full, Owner billing View and no Owner payroll-payment grant. Matrix inventory equals OpenAPI, including FastAPI included routers and conditional Helper grants. |
| Ownership and independence   | Own crew records only; no self-/beneficiary/prior-contributor approval even with combined roles. Variance/hold release and unpaid-payroll reversal have additional independence checks.                                                  |
| Financial integrity          | Decimal strings and fixed precision; immutable original earnings/rates; transaction lock, retry fingerprints and SQL uniqueness for earnings, active bills, repayments and reversals.                                                    |
| Operational corrections      | Receipt correction holds dependent finance atomically. Financial generation follows successful receipt completion in a separate transaction.                                                                                             |
| Data API                     | New finance tables are RLS-enabled with anon/authenticated grants revoked in migration 0005. Migration 0006 repairs missing grants in existing app databases and records expense contributors.                                           |
| Presentation isolation       | Explicit CLI, local nonproduction host/environment guards, fictional labels and unlinked demo employees; authenticated demo-image access disabled outside development/test/presentation.                                                 |
| Browser data                 | Financial API responses are no-store. Per-account stores clear prior-account snapshots; the service worker caches only a public allowlist, not identity/business data or writes.                                                         |
| Query growth                 | Batched report facts/display directory; query-growth regression and separate local 30-trip/20-user load evidence.                                                                                                                        |

See [financial regressions](../../src/backend/tests/test_finance_workflows.py), [presentation/concurrency checks](../../src/backend/tests/test_presentation_and_financial_controls.py), [readiness/query checks](../../src/backend/tests/test_financial_readiness_and_query_budget.py), and [load evidence](../runbooks/sprint-5-6-evidence/load-postgres.json). No real provider traffic, internet/TLS capacity or public-key live Supabase probe is certified by this local evidence.

## Request budgets

All windows are **60 seconds**, per process. Configuration is in the root environment; the defaults below appear in [the environment template](../../.env.example). Values must be between 1 and 1000.

| Setting                             | Default | Key / behavior                                                                                     |
| ----------------------------------- | ------- | -------------------------------------------------------------------------------------------------- |
| `RATE_LIMIT_FAILED_AUTH_PER_MINUTE` | 20      | Failed authentication per peer; successful authentication does not consume this failure budget     |
| `RATE_LIMIT_WEBHOOK_PER_MINUTE`     | 120     | Webhook attempts per peer, including invalid signatures                                            |
| `RATE_LIMIT_API_IP_PER_MINUTE`      | 600     | Protected API attempts per peer, before token verification                                         |
| `RATE_LIMIT_API_USER_PER_MINUTE`    | 120     | Protected calls per verified employee; rotating tokens/IPs does not create another employee budget |
| `RATE_LIMIT_UPLOAD_IP_PER_MINUTE`   | 30      | Upload attempts per peer                                                                           |
| `RATE_LIMIT_UPLOAD_USER_PER_MINUTE` | 10      | Upload attempts per verified employee                                                              |

Over-budget responses return `429`, code `RATE_LIMITED` and conservative `Retry-After: 60`. Storage is capped at **10,000 keys** and **100,000 timestamps**. Saturation rejects admission instead of deleting another block. Blocked calls add no timestamps. Old entries expire on subsequent operations.

Uploads still require authorization/assignment, a real supported image and size validation. The endpoint budget precedes file reads, image sanitization and storage in the handler; multipart parsing may already have occurred in the framework. Body/connection limits at ingress remain necessary.

## Proxy and worker deployment gate

The built-in limiter is **single-process**. Restarting a worker resets counters; multiple workers/replicas have separate counters. Before scaling, configure a shared rate-limit store or equivalent account/peer limits at a trusted ingress. These process-local budgets do not enforce a global quota.

For local sharing, forwarded headers are disabled, so users behind one proxy can share its peer budget. Verified-employee quotas still distinguish accounts. For hosting, define trusted proxy addresses, replace untrusted incoming forwarding headers at that proxy, and test client isolation through the actual public entry point. Do not use a blanket trusted-proxy wildcard. See Uvicorn's [HTTP settings](https://uvicorn.dev/settings/#http) and [proxy deployment guidance](https://uvicorn.dev/deployment/#proxies-and-forwarded-headers).

The repository backend launcher defaults to `--no-proxy-headers`. An operator can explicitly choose trusted proxy support for a reviewed hosting configuration; QA case S03 must then pass against that deployed path.

## Dependency and hosting follow-up

The Sprint 5–6 frontend production-only npm audit reported **0 vulnerabilities** and the backend requirements audit reported **no known vulnerabilities** on 18 November 2026. This is audit evidence, not a guarantee against undiscovered vulnerabilities. [Recorded results](../runbooks/sprint-5-6-evidence/verification.md) include scope and limits.

A pre-Sprint-5 full development audit recorded five High findings rooted in `picomatch` and did not force the suggested major tooling change. Treat that as historical toolchain evidence, not a refreshed count or current claim that no patch exists. Rerun the full development audit and review upstream guidance before release; see [historical verification](../runbooks/verification.md#historical-record-before-sprint-56).

Keep `.env`, credentials, real JWTs, sign-in tickets and account CSV files out of QA evidence and Git. Financial command payload/reference history is stored in the private append-only audit trail; Owner alone can read that audit API. Do not enter unrelated personal data or secrets into financial reasons/evidence references.

Before release, QA must still verify real private-bucket upload/signing/expiry, phone usability, real inbox verification, backups/restores, rollback, and the host's TLS, frontend CSP/security headers, database isolation, monitoring and trusted-proxy/shared-limiter configuration. Disable public API docs in production unless approved. Compose/ngrok/Vite commands remain development tooling.

**Release status: pending human review, manual/staging QA, D16 and hosting approval.** Core financial services persist on this branch; DEMO data is fictional. [Policy coverage](financial-policies.md#implementation-coverage-and-limits) lists unsupported correction/refund flows. No real-payroll or production approval is inferred from local checks.
