# Accounting

[All roles](README.md) · [Feature guide](../user-guide.md)

> **Your job:** Review trip expenses and charges; bill eligible trips and record client collections separately from payroll.

**Accounting workflow. Review trip expenses and charges; bill eligible trips and record client collections separately from payroll.**

```mermaid
flowchart TB
    accTitle: Accounting: daily workflow
    accDescr: Review trip expenses and charges; bill eligible trips and record client collections separately from payroll.
    read["LIVE: read Clients + Delivery orders"]:::action --> report["Report operational corrections to Dispatcher"]:::done
    report -.-> review["review expenses + finalize charge"]:::action
    review --> batch["Eligible unbilled charges → client batch"]:::action
    batch --> invoice["Issue invoice → record collections"]:::action
    classDef action fill:#e8f1ff,stroke:#2563eb,color:#163566,stroke-width:2px
    classDef done fill:#e7f6ec,stroke:#208448,color:#16452a,stroke-width:2px
```

## What can I use?

| Screen / area                | Your access                                             |
| ---------------------------- | ------------------------------------------------------- |
| Clients / Delivery orders    | Read-only review                                        |
| OR documents                 | Backend access by known reference; no dedicated browser |
| Expenses / Billing / Reports | Persistent financial records within your remit          |

## Quick checklist

- [ ] **Wrong operational detail:** Ask Dispatcher to correct it.
- [ ] **Need OR evidence:** Coordinate references with authorized operations staff.
- [ ] **Need to bill a client:** Open Billing, build a ready-trip batch, review it and issue when appropriate. DEMO bills are fictional.

> **Remember:** Accounting has no operational Dispatch access and cannot read other employees’ payroll. Its financial and report workspaces include authorized trip summaries.

> **Finance status:** persistent modules are available on this branch. [Current procedures and role boundaries](../sprint-5-6.md). DEMO records are fictional; real financial use remains gated.

## When you need the details

<details>
<summary><strong>Current access</strong></summary>

Read Clients and Delivery orders; use **Trip expenses**, **Billing** and **Reports** for authorized persistent financial work. The backend grants stored-OR viewing for a known trip/document reference, but Accounting has no operational trip-list grant or dedicated document browser; its financial/report workspaces provide trip summaries within its remit. Do not assume the Dispatch screen is available. Accounting cannot assign/clear trips, confirm OR receipt, read other employees' payroll or access the Owner audit log. Finance/report pages now use persistent, role-scoped APIs.

</details>

<details>
<summary><strong>Current operational review</strong></summary>

1. Open **Clients/Delivery orders**, search and inspect authorized request details.
2. Report operational corrections to Dispatcher rather than altering them through another account.
3. Coordinate evidence review and references with authorized operations staff. Developer/API support can use the authorized OR-document endpoints with your own session permissions; never request a storage service key.

</details>

<details>
<summary><strong>Expense and charge workflow</strong></summary>

1. Open **Trip expenses → Review declaration** to review Driver/Dispatcher expenses and evidence independently. Reject unsupported lines with a reason; do not approve your own submission.
2. Finalize an approved set or independently confirm an explicitly submitted zero-expense trip. Missing expenses remain unresolved.
3. Record/finalize the agreed fixed trip charge and its agreement reference. Submit variances for independent Owner review. Restrict rate information to Owner/Accounting.
4. Release financial readiness only when these controls pass; do not change operational completion to force financial processing.

</details>

<details>
<summary><strong>Billing and collections</strong></summary>

1. Open **Billing → Build client billing batch**; select one client, a cutoff and eligible unbilled trip charges, including earlier carry-over. The monthly cutoff is a working default, not an automatic scheduler. Preserve original dates; whole-order completion and stamped-copy upload are not prerequisites.
2. Exclude disputed/unready charges; other eligible trips can proceed. Verify the same charge is not on another active bill.
3. Review Draft lines/amounts/references, then issue. Default terms are 30 calendar days unless a recorded client agreement overrides them.
4. Record actual partial/full collections with date, method, reference and allocation. Do not reduce the client charge by crew payroll deductions or shares.
5. To void an issued invoice, request a separate Owner's approval and reconcile payments/credits before rebilling. Retain the audit trail and immutable issued amounts.

For exact button names and the refusal of paid-invoice voids/refund/credit-note operations, see [financial procedures](../user-guide.md#10-dashboard-audit-permissions-and-finance).

Expected outcome: charges are billed once, old unready work carries forward, and collection status remains separate from employee pay. Follow [financial policies](../../decisions/financial-policies.md); do not issue DEMO figures as real business invoices.

</details>

[Troubleshooting](../user-guide.md#11-troubleshooting-and-interrupted-operations) · [Financial policies](../../decisions/financial-policies.md)
