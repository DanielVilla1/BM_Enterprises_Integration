# Documentation reconciliation — Sprint 5–6

Review date: **18 November 2026**. Branch: `sprint-5-6-finance-and-reporting`, **unmerged**.

This follow-up reviewed **all 27 files under `docs/` at the time of that review** for Sprint 5–6 consistency. It reconciles current guidance against the financial services/DTOs, stored permission seed, frontend forms/navigation, migration files, committed API contract and retained implementation evidence. It does not claim every described policy exception has been implemented.

## What was reconciled

- Replaced stale financial-preview/not-started claims in current guides, diagrams, terminology, QA and all seven role manuals.
- Kept Owner expense Full access, Owner payroll oversight/read-only billing, HR payments and Accounting collections distinct; documented own-record and independent-approval checks.
- Added current financial procedures, exact API states, schema/query/transaction reference, grant-repair migration and presentation setup/limitations.
- Retained honest gaps: D16, live QA/provider/mobile/restore/hosting review, source/paid-record correction, evidence/category exceptions, schedule changes and unsupported allocation/editing controls.
- Kept the original developer-guide entry path. Archived proposal content and earlier verification are explicitly historical, rather than rewritten as newly observed results.

## File-by-file review

| File                                                                                      | Reconciliation / disposition                                                                                                                     |
| ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| [architecture.md](../architecture.md)                                                     | Updated folder/layer map, finance models/migrations/lock/query design, runtime boundaries and generated financial API/capability reference.      |
| [archive/architecture-proposal.md](../archive/architecture-proposal.md)                   | Historical body retained; archive banner points to current implementation and warns that old build status is historical.                         |
| [decisions/financial-policies.md](../decisions/financial-policies.md)                     | Updated diagrams/status; separated working policy from implemented coverage and unsupported exception flows.                                     |
| [decisions/README.md](../decisions/README.md)                                             | Corrected implementation status and linked policy coverage, grant migration and current verification.                                            |
| [decisions/security-hardening.md](../decisions/security-hardening.md)                     | Documented finance/identity/transaction/presentation controls; current production audits separated from historical development advisories.       |
| [DEVELOPER_GUIDE.md](../DEVELOPER_GUIDE.md)                                               | Preserved the original guide path; linked current setup, implementation, QA and this review.                                                     |
| [README.md](../README.md)                                                                 | Current feature inventory, role entry points, presentation versus preview distinction and release gates.                                         |
| [runbooks/delivery-walkthrough.md](delivery-walkthrough.md)                               | Removed reliance on private workstation helpers; added fictional end-to-end finance and provisioned-account/presentation guidance.               |
| [runbooks/development.md](development.md)                                                 | Updated sprint/branch status, schema/configuration, money/audit/transaction semantics, Docker evidence, tests and snapshot-derived route counts. |
| [runbooks/documentation-audit.md](documentation-audit.md)                                 | This review register and validation scope.                                                                                                       |
| [runbooks/qa.md](qa.md)                                                                   | Replaced preview exclusion with financial acceptance cases and explicit manual/legal/hosting sign-off gates.                                     |
| [runbooks/README.md](README.md)                                                           | Indexed financial procedures, seed setup, verification evidence and all-file reconciliation.                                                     |
| [runbooks/roles/accounting.md](roles/accounting.md)                                       | Expense/charge/billing/collection procedures, financial trip summaries, no payroll/audit access, and paid-invoice correction limits.             |
| [runbooks/roles/dispatcher.md](roles/dispatcher.md)                                       | Persistent expense entry/submission and operational reports, without commercial/payroll/approval rights.                                         |
| [runbooks/roles/driver.md](roles/driver.md)                                               | Own persistent expense submission, earnings/statements, advance requests and reports; Driver-only trip/receipt actions retained.                 |
| [runbooks/roles/fleet-manager.md](roles/fleet-manager.md)                                 | Current maintenance/replacement reports and continued limits on financial data/account administration.                                           |
| [runbooks/roles/helper.md](roles/helper.md)                                               | Own financial views/requests/reports, conditional OR actions, and no expense-entry or Driver-progress grant.                                     |
| [runbooks/roles/hr-payroll.md](roles/hr-payroll.md)                                       | Current payroll/advances procedures, no debt at draft/approval, payment authority, delegation independence and D16 restrictions.                 |
| [runbooks/roles/owner-manager.md](roles/owner-manager.md)                                 | Expense Full access, payroll oversight, read-only billing/void approval, independent holds and no HR payment/release powers.                     |
| [runbooks/roles/README.md](roles/README.md)                                               | Current seven-role handoffs, persistent finance scope and own-record versus design-preview distinction.                                          |
| [runbooks/service-workflow.md](service-workflow.md)                                       | Updated financial handoffs, automatic calculation timing, atomic receipt holds, retries and code/test traceability.                              |
| [runbooks/sprint-5-6-evidence/load-postgres.json](sprint-5-6-evidence/load-postgres.json) | Reviewed and preserved generator-owned measured data; no benchmark rerun or fabricated measurement.                                              |
| [runbooks/sprint-5-6-evidence/verification.md](sprint-5-6-evidence/verification.md)       | Reviewed and preserved the recorded implementation/test/audit/runtime evidence and its stated limits; no new application runs claimed.           |
| [runbooks/sprint-5-6.md](sprint-5-6.md)                                                   | Current handoff, initial seed baseline versus later edits, policy limits and review links.                                                       |
| [runbooks/user-guide.md](user-guide.md)                                                   | Added actual financial screen/button procedures, role boundaries, Owner grant-repair troubleshooting, offline limits and demo cautions.          |
| [runbooks/verification.md](verification.md)                                               | Current evidence first; original pre-Sprint-5 observations retained in a clearly labelled historical section.                                    |
| [taxonomy.md](../taxonomy.md)                                                             | Replaced planned finance with exact persistent/derived states and separate invoice/payment/allocation concepts.                                  |

## Validation and evidence boundaries

Documentation validation checks Markdown formatting, links/heading anchors, fenced blocks/disclosures, referenced financial API/capability coverage, diagram class references and stale-current-status assertions. Application code, schema, accounts and business records were not changed by this documentation reconciliation; application tests, provider journeys, staging and legal review were not rerun or invented.

The retained contract currently has **69 paths / 81 operations**, of which finance contributes **31 paths / 32 operations**. The original implementation results remain in [verification](sprint-5-6-evidence/verification.md); [raw load evidence](sprint-5-6-evidence/load-postgres.json) remains generator-owned.

Raw load-evidence SHA-256 at review: `acdd47a811807ed3e1931d1c3ad5b8d5ade9207c701abecfdcc04fa9d36c657f`.

This register covers the current `docs/` tree, including this file; it does not claim that a new document added later has already been reviewed. Merge and production approval remain separate actions.

## Subsequent integration of main

The conflict-resolution update imported the earlier QA report, raw QA evidence and combined technical reference from `main`. They extend the original 27-file inventory above. The imported technical reference and QA report now explicitly identify their historical baseline and link to current finance guidance; raw evidence is retained unchanged. Compose keeps the financial branch health/restart controls alongside main's `.dockerignore` rebuild watches, environment exclusions and fresh-database setup guidance.
