# Sprint 5–6 handoff and presentation

Branch: `sprint-5-6-finance-and-reporting`. **Unmerged.**

Authority: **BM Enterprises Consolidated Developer Specification, 9 November 2026**, sections 3.4, 7–10 and 13. The [financial working policies](../decisions/financial-policies.md) supply documented development defaults for D4–D10. They do not constitute production or legal approval.

## Implemented behavior

| Area                        | Behavior                                                                                                                                                                                   |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Expenses                    | Fuel/toll evidence references, entry, submission, independent approval/return, reviewed zero declarations and contributor history.                                                         |
| Charges and rates           | Final per-trip charges, independent Owner variance approval, future-dated percentage versions and departure snapshots.                                                                     |
| Earnings                    | Exact decimals, half-up centavos, 8/4 and 6/3/3 distributions, separate original entries, rounding variance, pending calculation and negative-base holds.                                  |
| Payroll                     | Semi-monthly drafts, late carry-forward, statements, reviewed adjustments, transactional repayments, unpaid balances, payment records and independent unpaid-payroll reversal.             |
| Advances                    | Requests, independent approvals, named expiring/revocable delegation, acknowledged partial releases, agreed installments, repayments/reversals and separate operating-fund reconciliation. |
| Billing                     | Eligible carry-over trips, one-client batches, unique active charge allocation, issue/terms, independent void approval, collections and excess credit.                                     |
| Reports                     | Assigned crew, receipt/document exceptions, finance readiness, payroll/advance/client balances, maintenance and replacements within each role's remit.                                     |
| Driver installation support | Manifest and production service worker with a public connection-help page. No cached credentials/business records or offline action queue.                                                 |

Expenses, Payroll, Cash advances, Billing and Reports now use persistent APIs. Their **Soon** indicators are removed. `/preview.html` retains labelled sample designs for UI development.

Earnings are attempted when the last financial input is finalized. If finance is ready before receipt, a separate calculation transaction follows committed operational completion. A financial failure cannot undo receipt confirmation or block dispatch; an authorized Calculate action retries pending work.

## Owner permissions: specification section 3.4

| Action                               | Owner alone            | Other responsible role                                          |
| ------------------------------------ | ---------------------- | --------------------------------------------------------------- |
| Enter/review trip expenses           | Full; no self-approval | Dispatcher/assigned Driver enter; Accounting can approve        |
| Finalize charges; view hauling rates | Full                   | Accounting                                                      |
| Set earnings percentages             | Full                   | Owner                                                           |
| Inspect earnings/payroll             | Full read access       | HR prepares/finalizes payroll                                   |
| Approve deductions/adjustments       | Full, independently    | HR prepares adjustments; deductions remain disabled pending D16 |
| Approve advances                     | Full, independently    | Crew/HR request; HR records releases                            |
| Record payroll payment               | No                     | HR and Payroll                                                  |
| Inspect billing                      | Read-only              | Accounting builds/issues bills and records collections          |
| Approve requested invoice void       | Full, independently    | Accounting requests; a different Owner approves                 |
| Reports                              | Within these grants    | Crew see their own records                                      |

Navigation now uses each endpoint's actual read capability; actions use separate write grants. The backend enforces every request. The Owner expense **Forbidden** regression came from an already-migrated `0005` database missing the new read grants. Migration **0006** repairs existing installations and adds expense contributor history. Editing seed JSON or an already-applied migration alone does not upgrade a database.

## Presentation dataset

The recorded presentation seed baseline is **8 DEMO trips, 9 earnings entries, 4 advances, 2 payroll periods and 3 invoices**. Later user actions can change counts/states; rerunning the seed does not reset those edits. Existing records and Clerk links are preserved. Added employees/clients are labelled `DEMO`; generated employees have no Clerk identity or usable sign-in account.

Examples cover the PHP 20,000 less PHP 5,500 calculation, two-helper earnings, reviewed zero expenses, pending review/calculation, a negative-base hold, an OR awaiting receipt, advances before/after release, finalized/part-paid payroll, carry-forward earnings, and draft/part-collected/fully-collected bills.

The financial screens show a presentation notice. Demo evidence images are generated locally, marked **PRESENTATION ONLY**, and require file-view authorization and trip ownership. Their endpoint is disabled outside development/test/presentation. No real signature, external upload, payment or collection is implied.

```powershell
docker compose exec -T backend python -m backend.scripts.seed_presentation --presentation
```

Rerunning reports `already_loaded` without duplicating records. The CLI refuses production environments and remote database hosts. Seeding never runs automatically during application startup or schema migrations.

## Verification

[Final verification results](sprint-5-6-evidence/verification.md) record test counts, audits, runtime permission checks and remaining limits.

Backend verification includes migrations, financial rules, ownership, combined-role self-approval, concurrent billing/retries, rollback, receipt holds and the API contract. The permission inventory must equal OpenAPI, so framework router changes cannot silently skip matrix tests. Conditional Helper grants respect their feature flag.

The PostgreSQL verifier creates a new local scratch database and removes that specific database afterward. **Never point `TEST_DATABASE_URL` at the app database**: test fixtures deliberately reset the test schema.

```powershell
src/backend/.venv/Scripts/python tools/scripts/backend.py backend.scripts.export_openapi
src/backend/.venv/Scripts/python tools/scripts/verify_postgres.py --load
```

The opt-in load check seeds 30 completed trips, then paces 300 authenticated reads across 20 users at 10 requests/second. [PostgreSQL load evidence](sprint-5-6-evidence/load-postgres.json) records measured latency and failures. This is local ASGI/database verification, excluding real Clerk/Supabase, internet/TLS and production capacity.

Frontend verification covers read/menu alignment, Owner/HR/Accounting boundaries, decimal-string payloads, account-scoped cache clearing, lint, tests and production build. Financial screens use a separate bundle.

## Implementation coverage

[Policy coverage and limits](../decisions/financial-policies.md#implementation-coverage-and-limits) documents missing trip-source/paid-record corrections, receipt/category exceptions, per-line expense editing, schedule amendments and operating-fund allocation limits. [Financial procedures](user-guide.md#10-dashboard-audit-permissions-and-finance) and the [QA cases](qa.md#7-financial-scope-and-release-decision) describe the supported paths. See [documentation reconciliation](documentation-audit.md) for all-file review scope.

## Remaining release gates

- Named human review of authorization, money, uploads and migrations before merging (specification section 12).
- D16 review before real percentage-pay/deduction/repayment use. Personal deductions default to disabled: `PAYROLL_DEDUCTIONS_ENABLED=false`.
- Real staging journeys, Supabase upload/link expiry, supported phones and installation checks.
- Production hosting, MFA/recovery, HTTPS scan, incident response, backup/reconciliation schedules and a measured restore drill.
- Refunded/credited collections and already-paid payroll require a designed reconciliation workflow. The API preserves payment evidence and refuses void/reversal while payments remain.

See [QA acceptance](qa.md) and [security hardening](../decisions/security-hardening.md). Passing local checks and a populated demonstration are not production sign-off.
