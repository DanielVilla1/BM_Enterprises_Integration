# Decisions and working policies

[Handbook](../README.md) · [Architecture](../architecture.md)

| Decision reference                | Read this                                                           | State                                                                                                         |
| --------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| D4–D10                            | [Financial working policies](financial-policies.md)                 | User-authorized development defaults; core services implemented on this branch, with documented release gates |
| Remaining specification decisions | [Unresolved decisions](../runbooks/development.md#13-left-to-build) | Check the developer guide before implementation                                                               |

See [security hardening and release gates](security-hardening.md) for implemented protections and remaining hosting checks.

Keep new policy decisions here with their date, reason, scope and affected runbooks. Label proposals and working defaults clearly; do not present them as production approval.

[Implementation coverage and exception limits](financial-policies.md#implementation-coverage-and-limits) distinguishes implemented controls from unsupported flows. [Current verification](../runbooks/verification.md) separates current evidence from historical audit results. New read grants need a forward migration as well as seed JSON; migration 0006 is the Owner expense-read repair.
