# Fleet Manager

[All roles](README.md) · [Feature guide](../user-guide.md)

> **Your job:** Keep trucks and Driver licenses ready for dispatch.

**Fleet Manager workflow. Keep trucks and Driver licenses ready for dispatch.**

```mermaid
flowchart TB
    accTitle: Fleet Manager: daily workflow
    accDescr: Keep trucks and Driver licenses ready for dispatch.
    inspect["Check truck condition + capacity"]:::action --> ready{"Vehicle ready?"}:::wait
    ready -->|No| repair["Record maintenance<br/>Coordinate replacement if assigned"]:::wait
    repair --> close["Complete maintenance after repair"]:::action
    ready -->|Yes| license["Check Driver license + expiry"]:::action
    close --> license
    license --> notify["Tell Dispatcher resources are ready"]:::done
    classDef action fill:#e8f1ff,stroke:#2563eb,color:#163566,stroke-width:2px
    classDef done fill:#e7f6ec,stroke:#208448,color:#16452a,stroke-width:2px
    classDef wait fill:#fff3d6,stroke:#b77910,color:#62420d,stroke-width:2px
```

## What can I use?

| Screen / area           | Your access                                |
| ----------------------- | ------------------------------------------ |
| Fleet                   | Register/edit trucks and maintenance       |
| People → Driver license | Save number and expiry                     |
| Limited employee list   | Select by name; private fields stay hidden |

## Quick checklist

- [ ] **Assigned truck breaks down:** Dispatcher replaces it; you manage repair.
- [ ] **Missing/expired license:** Update license → notify Dispatcher to recheck.
- [ ] **Wrong role or inactive person:** Ask Owner; Fleet cannot activate or assign roles.

> **Remember:** Trip completion never repairs a truck or closes its maintenance automatically.

## When you need the details

<details>
<summary><strong>Responsibility and access</strong></summary>

Maintain trucks, capacity, condition, maintenance and Driver license details. People access is limited to names/status for selecting employees; private contact/account/role fields are not exposed. No dispatch clearance, order entry, payroll, billing or role administration.

</details>

<details>
<summary><strong>Keep trucks eligible</strong></summary>

1. Follow [Fleet and maintenance](../user-guide.md#6-fleet-and-maintenance) to register plate/capacity and maintain descriptions.
2. Review truck state before recommending it to Dispatcher. Assigned does not always mean unavailable for a next reservation; Dispatcher checks the prior OR and all crew conflicts.
3. Start maintenance for an available truck with a clear operational reason.
4. For a breakdown on an assigned/in-transit trip, tell Dispatcher to **Replace truck** and mark the original as needing maintenance. You do not replace/clear a trip yourself.
5. After real repairs, **Complete maintenance** and notify Dispatcher. A trip's completion never repairs or auto-releases a maintenance truck.

</details>

<details>
<summary><strong>Maintain licenses</strong></summary>

1. Follow [Driver licenses](../user-guide.md#3-driver-licenses): **People → employee actions → Driver license**.
2. Select the known Driver by name, enter/correct number and expiry, then **Save license**.
3. Confirm validity and notify Dispatcher. License actions may also appear for limited employee rows whose roles are hidden; the server rejects saving a license for a non-driver.
4. Resolve missing/expired licenses before assignment. A later capacity/license change is rechecked at clearance and departure.

Expected outcome: accurate fleet and license data supports dispatch eligibility. Report wrong crew roles or employee status to Owner; you cannot activate or reassign roles. Expanded maintenance/replacement reports remain planned, while maintenance history is available on Fleet.

</details>

[Troubleshooting](../user-guide.md#11-troubleshooting-and-interrupted-operations) · [Financial policies](../../decisions/financial-policies.md)
