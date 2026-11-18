# Choose your role

[Documentation home](../../README.md) · [Feature guide](../user-guide.md)

One account can hold several approved roles. Start with the work you actually do.

**Owner, HR and Fleet prepare people/resources; Dispatcher assigns; Driver and Helper deliver; finance is planned.**

```mermaid
flowchart TB
    accTitle: Who hands work to whom?
    accDescr: Owner authorizes staff, Fleet readies resources, Dispatcher plans, and Driver and Helper execute delivery; finance is a later separate module.
    owner["OWNER<br/>People + access + oversight"]:::action --> dispatcher["DISPATCHER<br/>Orders + assignments + clearance"]:::action
    fleet["FLEET MANAGER<br/>Trucks + driver licenses"]:::action --> dispatcher
    hr["HR<br/>Employee records"]:::action --> owner
    dispatcher --> driver["DRIVER<br/>Progress + receipt confirmation"]:::done
    helper["HELPER<br/>Hauling + authorized upload"]:::done --> driver
    driver -.-> finance["PLANNED FINANCE"]:::planned
    finance --> hrpay["HR: payroll + releases"]:::planned
    finance --> account["ACCOUNTING: charges + billing"]:::planned
    classDef action fill:#e8f1ff,stroke:#2563eb,color:#163566,stroke-width:2px
    classDef done fill:#e7f6ec,stroke:#208448,color:#16452a,stroke-width:2px
    classDef planned fill:#f0ebff,stroke:#7856ad,color:#412c65,stroke-width:2px,stroke-dasharray:5 4
```

| I am responsible for…                  | My guide                            |
| -------------------------------------- | ----------------------------------- |
| People, permissions and oversight      | [Owner / Manager](owner-manager.md) |
| Orders, assignments and dispatch       | [Dispatcher](dispatcher.md)         |
| Trucks, maintenance and licenses       | [Fleet Manager](fleet-manager.md)   |
| Delivery progress and company receipt  | [Driver](driver.md)                 |
| Hauling support and authorized upload  | [Helper](helper.md)                 |
| Employee records and future payroll    | [HR and Payroll](hr-payroll.md)     |
| Future trip finance and client billing | [Accounting](accounting.md)         |

> **Roles do not bypass rules.** The backend also checks whose record it is and what state it is in. Owner alone cannot enter orders as Dispatcher or confirm receipts as Driver.

**Live:** operational records. **Preview:** invented financial examples. **Planned:** not yet implemented. Helpers without logins may still be recorded and assigned.
