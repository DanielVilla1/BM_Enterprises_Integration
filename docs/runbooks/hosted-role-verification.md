# Hosted sign-in and recovery verification

Verified on **19 November 2026** against the follow-up to merged PR #9. This records automated application checks, not seven live Clerk browser sessions or a completed hosted-data migration.

## Role coverage

The frontend uses the real permission seed as its account fixture and checks explicit expected menus and financial actions after both immediate and delayed health responses. All roles retain a sign-out control when their employee account cannot load; the control uses Clerk's sign-out component and returns to the application entry page.

| Role          | Immediate/delayed startup | Navigation and finance actions | Linked active `/me` | Inactive/expired rejection | Recovery-screen sign-out |
| ------------- | ------------------------- | ------------------------------ | ------------------- | -------------------------- | ------------------------ |
| Owner/Manager | Pass                      | Pass                           | Pass                | Pass                       | Pass                     |
| Dispatcher    | Pass                      | Pass                           | Pass                | Pass                       | Pass                     |
| Fleet Manager | Pass                      | Pass                           | Pass                | Pass                       | Pass                     |
| Driver        | Pass                      | Pass                           | Pass                | Pass                       | Pass                     |
| Helper        | Pass                      | Pass                           | Pass                | Pass                       | Pass                     |
| HR/Payroll    | Pass                      | Pass                           | Pass                | Pass                       | Pass                     |
| Accounting    | Pass                      | Pass                           | Pass                | Pass                       | Pass                     |

Backend account checks exercise both settings of the conditional Helper upload feature. Exact returned capability maps are compared with the seed, so unrelated privileges cannot silently appear. The existing permission-matrix regression covers **78 capability-gated operations × 7 roles = 546 authorization cells**, with separate checks for the authenticated account route, public allowlist and unauthenticated denials. Reachability checks on deliberately incomplete business requests establish authorization boundaries; successful business workflows are covered by the broader backend suite.

## Final automated results

| Check                                            | Result                        |
| ------------------------------------------------ | ----------------------------- |
| Complete frontend suite                          | **117 passed**, 14 test files |
| Complete SQLite/Python 3.14 backend suite        | **302 passed, 7 skipped**     |
| Complete PostgreSQL 16/Python 3.12 backend suite | **308 passed, 1 skipped**     |
| Frontend lint, formatting and production build   | Passed                        |
| Backend/tools Ruff and Black                     | Passed                        |
| Documentation links, anchors and whitespace      | Passed                        |

The opt-in load test was not repeated for this recovery change. PostgreSQL-only checks account for the additional SQLite skips. Existing dependency deprecation and SQLite expression-index reflection warnings remain. The PostgreSQL suite ran against a disposable database and dedicated Docker network; both were removed afterward. No hosted Supabase records were accessed by these automated tests.

## What changed

- Blocked-account, connection-error and loading pages include **Sign out**. Blocked/error pages display the current Clerk email so a different account can be recognized.
- The backend retains `AUTH_NO_ACTIVE_EMPLOYEE` and HTTP 403, while identifying `identity_not_linked` versus `employee_inactive` and returning only the caller's own verified Clerk subject for setup support. Invalid tokens receive no account-setup diagnostics. No route or privilege is added.
- The local operator recovery command verifies a unique primary email through the official Clerk directory, then repairs only an existing Owner's link and activation through audited employee operations. It cannot promote any other role, claim an identity already held by another employee, or create a user. Unverified/mismatched email is refused; repeat recovery is idempotent.

The [hosted Owner runbook](hosted-demo-owner.md) explains first setup, repair and the remaining role provisioning. The [connection runbook](hosted-demo-connectivity.md) distinguishes connectivity from identity linkage. A new deployment is required for the UI/backend diagnostics; an existing hosted account-link mismatch additionally requires the privileged operator repair against the exact database and Clerk instance used by Render. Automated checks alone do not establish that this live-data repair has completed.

## Regression sources

- [Frontend startup and role navigation/actions](../../src/frontend/tests/unit/accountStartup.test.js)
- [Frontend recovery controls](../../src/frontend/tests/components/sessionRecovery.test.jsx)
- [Frontend failure classification](../../src/frontend/tests/unit/problemDetails.test.js)
- [Backend account loading for every role](../../src/backend/tests/test_hosted_role_startup.py)
- [Backend route permission matrix](../../src/backend/tests/test_permission_matrix.py)
- [Operator recovery safeguards](../../src/backend/tests/test_owner_recovery.py)
