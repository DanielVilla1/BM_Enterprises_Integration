# Choose your role

[Documentation home](../../README.md) · [Feature guide](../user-guide.md)

One account can hold several approved roles. Start with the work you actually do.

**Owner, HR and Fleet prepare people/resources; Dispatcher assigns; Driver and Helper deliver; HR and Accounting process separate financial workflows.**

```mermaid
flowchart TB
    accTitle: Who hands work to whom?
    accDescr: Owner authorizes staff, Fleet readies resources, Dispatcher plans, and Driver and Helper execute delivery; HR and Accounting process separate financial workflows.
    owner["OWNER<br/>People + access + oversight"]:::action --> dispatcher["DISPATCHER<br/>Orders + assignments + clearance"]:::action
    fleet["FLEET MANAGER<br/>Trucks + driver licenses"]:::action --> dispatcher
    hr["HR<br/>Employee records"]:::action --> owner
    dispatcher --> driver["DRIVER<br/>Progress + receipt confirmation"]:::done
    helper["HELPER<br/>Hauling + authorized upload"]:::done --> driver
    driver -.-> finance["SEPARATE FINANCE"]:::action
    finance --> hrpay["HR: payroll + releases"]:::action
    finance --> account["ACCOUNTING: charges + billing"]:::action
    classDef action fill:#e8f1ff,stroke:#2563eb,color:#163566,stroke-width:2px
    classDef done fill:#e7f6ec,stroke:#208448,color:#16452a,stroke-width:2px
```

| I am responsible for…                  | My guide                            |
| -------------------------------------- | ----------------------------------- |
| People, permissions and oversight      | [Owner / Manager](owner-manager.md) |
| Orders, assignments and dispatch       | [Dispatcher](dispatcher.md)         |
| Trucks, maintenance and licenses       | [Fleet Manager](fleet-manager.md)   |
| Delivery progress and company receipt  | [Driver](driver.md)                 |
| Hauling support and authorized upload  | [Helper](helper.md)                 |
| Employee records, payroll and advances | [HR and Payroll](hr-payroll.md)     |
| Trip finance and client billing        | [Accounting](accounting.md)         |

> **Roles do not bypass rules.** The backend also checks whose record it is and what state it is in. Owner alone cannot enter orders as Dispatcher or confirm receipts as Driver.

**Persistent on this branch:** operations, finance and reports. The separate `/preview.html` page uses sample designs; seeded `DEMO` records are fictional presentation data stored in the development database. Helpers without logins may still be recorded and assigned. Real financial use remains subject to release gates.
