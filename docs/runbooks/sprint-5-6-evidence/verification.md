# Sprint 5–6 verification

Verified locally on 18 November 2026. Branch: `sprint-5-6-finance-and-reporting`, unmerged.

| Check                                       | Result                                                                                               |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Complete SQLite suite, Python 3.14          | 251 passed, 7 skipped; final focused contract/financial checks also passed (5 tests).                |
| Complete PostgreSQL suite, Python 3.12      | 258 passed, 1 skipped. The skipped load test ran separately.                                         |
| PostgreSQL load check                       | 300 requests, 20 users, 30 trips; zero failures; 30.27 seconds; 9.91 requests/second; p95 102.45 ms. |
| Frontend tests                              | 78 passed.                                                                                           |
| Frontend lint, formatting, production build | Passed. Financial screens are a separate lazy-loaded bundle.                                         |
| Backend/tool lint and formatting            | Passed.                                                                                              |
| Documentation links and anchors             | Passed.                                                                                              |
| npm production-dependency audit             | Zero vulnerabilities reported.                                                                       |
| Backend requirements audit                  | No known vulnerabilities reported.                                                                   |
| Running development API contract            | Matches the committed snapshot.                                                                      |
| Running Owner permissions                   | Expenses FULL; billing VIEW; no payroll-payment grant.                                               |
| Presentation records                        | 8 trips, 9 earnings, 4 advances, 2 payrolls, 3 invoices; seed is repeatable.                         |

The initial load diagnostic returned no errors but queued work for 52.42 seconds with p95 5,479.13 ms. Batched trip/document/finance/maintenance lookups and a display-only employee directory removed per-row reads. A query-growth regression now checks that adding trips does not add report queries per trip. See [the measured load report](load-postgres.json).

The initial cross-version contract check exposed Python-dependent HTTP reason phrases for 413 and 422. OpenAPI now describes the actual `application/problem+json` errors with stable descriptions; the final complete Python 3.12/PostgreSQL run passed.

Every PostgreSQL verification used a newly created scratch database, removed afterward. The development presentation database was not reset. The final running Owner workspace check read the actual stored grants and counts without creating or changing sign-in identities.

These checks use test signing keys and fake storage in automated tests. Live Clerk/Supabase journeys, mobile installation, TLS/network capacity, restore timing, D16 review and named human review remain release gates. No production rollout, money transfer, merge or production certification is claimed.
