# Security hardening and remaining release gates

[QA acceptance](../runbooks/qa.md) · [Verification](../runbooks/verification.md) · [Architecture](../architecture.md)

**Review date: 18 November 2026.** Scope: rate-limit implementation, authenticated API/upload entry points, request size controls, JWT/role boundaries, private storage, response headers and dependency results. This is a focused developer review; it does not replace manual QA or hosting validation.

## Findings addressed

| Priority | Finding / consequence                                                                                      | Change and regression evidence                                                                                                                              |
| -------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| High     | Key-table saturation cleared all rate counters, allowing existing blocks to disappear                      | Reject new keys at capacity, reclaim expired entries and preserve other counters; key-saturation regression                                                 |
| Medium   | Separate record/count operations were non-atomic; rejected webhook traffic could keep growing event deques | Locked atomic admission; rejected requests add no events; total key/event memory caps; concurrent-admission and event-capacity regressions                  |
| Medium   | Successful API requests and image-processing/storage attempts had no dedicated quotas                      | Per-peer and verified-employee API budgets; separate upload budgets before file decoding/storage; independent-account and upload regressions                |
| Medium   | Trusting forwarding headers through the local Vite proxy could let a client choose its apparent address    | Shipped development launchers and container commands disable Uvicorn proxy headers by default; application quota keys never directly use forwarding headers |
| Low      | Sensitive API responses lacked explicit cache/sniffing/frame restrictions                                  | API trace middleware adds no-store, nosniff, frame denial and no-referrer; success/throttle response regression                                             |

Implementation: [limiter](../../src/backend/src/rate_limiter.py), [dependency gates](../../src/backend/src/providers.py), [upload route](../../src/backend/src/Controller/or_controller.py), [response middleware](../../src/backend/src/problem_details.py), [regression tests](../../src/backend/tests/test_rate_limits.py).

JWT verification remains RS256-only with issuer, expiry, required claims and configured authorized-party checks. Local employee activation, capability grants, record ownership and trip state are enforced by the backend. Existing authentication, permission, OR-access, image-validation and PostgreSQL hardening tests remain part of the full suites. No authentication bypass was added for testing.

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

The frontend production-only npm audit returned **0 vulnerabilities** on the review date. The full development audit still reports **5 High findings** rooted in `picomatch`; the reviewed advisory lists no patched version. The automatic npm suggestion changes major Vite/Vitest versions, so it was not applied as a security fix. Track this as an open build-tool release decision; never use the Vite development server as production hosting. See the [upstream advisory](https://github.com/advisories/GHSA-fc5q-39xc-vjpf).

Record the backend dependency audit and automated results in [verification](../runbooks/verification.md). Keep `.env`, credentials, real JWTs, sign-in tickets and development-account CSV files out of QA evidence and Git.

Before release, QA must still verify real private-bucket upload/signing/expiry, phone usability, real inbox verification, backups/restores, rollback, and the host's TLS, frontend CSP/security headers, database isolation, monitoring and trusted-proxy/shared-limiter configuration. Disable public API docs in production unless approved. Compose/ngrok/Vite commands remain development tooling.

**Release status: pending QA and hosting design.** Financial modules remain previews and are excluded from real financial processing until implemented and reviewed.
