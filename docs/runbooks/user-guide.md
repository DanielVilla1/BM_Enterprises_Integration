# User feature guide

**Sprint 5–6 branch:** The financial and report screens now use persistent APIs. Use the procedures below and the [finance and presentation guide](sprint-5-6.md). DEMO records are fictional, and production financial release remains gated.

**Want to practice?** Start with [the guided delivery exercise](delivery-walkthrough.md).

[Index](../README.md) · [Choose your role](roles/README.md) · [Terms and statuses](../taxonomy.md)

These procedures cover persistent operational and financial screens on the Sprint 5–6 branch. Only the separate `/preview.html` design harness uses sample-only screens. Seeded `DEMO` records persist in the development database and are fictional; they must not be used as actual pay or invoices. The [financial policies](../decisions/financial-policies.md) describe working defaults and release gates.

## Find your task quickly

**The three phases of a delivery: plan, deliver and close the paperwork.**

```mermaid
flowchart TB
    accTitle: Delivery in three stages
    accDescr: Plan and clear the trip, deliver and upload evidence, then hand over the OR and confirm receipt.
    subgraph plan["1 · PLAN"]
        order["Dispatcher: record order + assign crew"]:::action --> accept["Driver: accept"]:::action
        accept --> clear["Dispatcher: check + clear"]:::action
    end
    subgraph haul["2 · DELIVER"]
        depart["Driver: depart + deliver"]:::action --> upload["Authorized crew: upload signed OR"]:::wait
    end
    subgraph finish["3 · CLOSE THE PAPERWORK"]
        handover["Driver: hand OR to steel company"]:::action --> receipt["Driver: confirm actual receipt"]:::done
        receipt --> complete["Trip completed"]:::done
    end
    clear --> depart
    upload --> handover
    classDef action fill:#e8f1ff,stroke:#2563eb,color:#163566,stroke-width:2px
    classDef done fill:#e7f6ec,stroke:#208448,color:#16452a,stroke-width:2px
    classDef wait fill:#fff3d6,stroke:#b77910,color:#62420d,stroke-width:2px
```

| Prepare                                                                                  | Deliver                                                                            | Resolve an issue                                                  |
| ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| [People](#2-people-and-accounts) · [Licenses](#3-driver-licenses)                        | [Dispatch](#7-dispatch-and-assignment) · [My trips](#8-my-trips-driver-and-helper) | [Troubleshooting](#11-troubleshooting-and-interrupted-operations) |
| [Clients](#4-clients) · [Orders](#5-delivery-orders) · [Fleet](#6-fleet-and-maintenance) | [OR and completion](#9-signed-or-stamped-copy-and-completion)                      | [Owner corrections](service-workflow.md#3-exceptions)             |

## 1. Sign in and understand your access

**Open app → sign in → check My account.** Owner must link and activate your employee first.

<details>
<summary><strong>Full procedure and exception rules</strong></summary>

Prerequisite: the Owner has linked your sign-in account to an active employee and assigned appropriate roles.

1. Open the application URL supplied by your administrator. Local use is normally `http://localhost:5173`; a shared development URL works only while its host is running.
2. Sign in with your assigned email and application password, or an enabled sign-in method. Enter the actual email verification code when requested. A normal Gmail alias is not a test-code account.
3. Open **My account** to check your name, roles and access levels. Tell the Owner if incorrect; changing Clerk metadata does not change your system permissions.
4. Use the sidebar; on small screens open the menu or bottom navigation. Only permitted pages appear. Sun/moon switches appearance, not access.
5. Sign out through the account control when finished, especially on a shared device. Do not share accounts or passwords.

If sign-in succeeds but the workspace is blocked, ask the Owner to check the Clerk link and employee activation. Repeatedly creating new sign-ins will not grant a role. If another person's information appears, stop using that session and report it to the administrator.

</details>

## 2. People and accounts

**Create → assign roles → link sign-in → activate.** HR can create/edit; Owner controls access.

<details>
<summary><strong>Full procedure and exception rules</strong></summary>

**Who:** Owner/HR create/edit. Owner alone manages roles, identity linking, activation/deactivation. Fleet/Dispatcher see limited employee data for license tasks.

1. Open **People → Add employee**. Enter name, email and optional phone; save.
2. New records are inactive. The Owner opens the person's action menu → **Roles**, selects duties and saves. Forbidden combinations require an Owner exception reason; use a genuine documented reason, not placeholder text.
3. For people who will sign in, an administrator creates/invites the identity in Clerk using the team's sign-in setup. The Owner uses **Link sign-in account** and the correct Clerk user ID. This links an existing identity; it does not create a password in the BM database.
4. Owner selects **Activate** when the person is authorized. Drivers need a linked account; helpers may remain without a sign-in account if they perform no app actions.
5. To edit contact details, use **Edit details**. To remove access, Owner selects **Deactivate**. History is preserved; discuss any outstanding assigned trips with Dispatcher.

Search by name (and email/role when your access exposes those fields), or use Active/Inactive tabs. Limited viewers see only names/status; hidden email, role and account fields are deliberately omitted. Do not infer “no account” from an omitted field.

</details>

## 3. Driver licenses

**People → Driver license → save number and expiry.** Fleet/Owner write; other grants are read-only or limited.

<details>
<summary><strong>Full procedure and exception rules</strong></summary>

**Who:** Fleet/Owner enter and update; HR reads details; Dispatcher sees validity only. Backend also supports a Driver reading their own license; no separate Driver license editor is provided.

1. Open **People**, find the driver by name and open **Driver license** (or **License status** for read-only access).
2. Review existing validity. Fleet/Owner enters the license number and expiry date and selects **Save license**.
3. Confirm the saved expiry and status. Updating a license does not automatically clear a trip; return to Dispatcher for eligibility recheck.

Limited employee records do not include roles, so license actions can appear beside a non-driver. Saving is still rejected unless the person has the Driver role. “No license on record” means a license must be recorded for a driver before assignment. A license must remain valid for the scheduled trip and actual dispatch date.

</details>

## 4. Clients

**Search before adding.** Dispatcher writes; Owner/Accounting read. Rates are not stored here.

<details>
<summary><strong>Full procedure and exception rules</strong></summary>

**Who:** Dispatcher writes; Owner/Accounting read.

1. Open **Clients**, search for an existing record before adding another.
2. Select **New client**, enter the organization name and available contact details; save.
3. Use the row action to edit incorrect contact details. Confirm the correct client before creating an order.

Expected result: the client is available in the order form. This page currently stores operational contact information, not client hauling rates.

Use the client action menu to deactivate an unused client or reactivate one when appropriate. Existing history stays recorded; verify the correct active client before new orders.

</details>

## 5. Delivery orders

**New order → client, locations, date and tons → save.** Only Pending orders can be edited/cancelled.

<details>
<summary><strong>Full procedure and exception rules</strong></summary>

**Who:** Dispatcher writes; Owner/Accounting read. An Owner who also performs order entry needs the Dispatcher role; Owner alone has VIEW here.

1. Obtain the steel company's delivery instructions outside the app.
2. Open **Delivery orders → New order**. Select client, enter pickup and delivery locations, scheduled date, total weight in metric tons, reference and notes where applicable.
3. Check the load and save. The order starts Pending; assignment and trip progress derive its status.
4. Correct permitted fields through **Edit**. Only Pending orders can be edited.
5. If the request is withdrawn, use **Cancel** with a reason. Only Pending orders can be cancelled; coordinate existing trip commitments first.

Expected result: Dispatcher can select the order in **Dispatch → Assign trip**. A 40-ton order might need two trips on 25-ton trucks; each trip must respect capacity and remaining unassigned load. Do not lower the order weight below existing assigned load.

</details>

## 6. Fleet and maintenance

**Register → maintain → explicitly return to service.** Coordinate assigned-truck breakdowns with Dispatcher.

<details>
<summary><strong>Full procedure and exception rules</strong></summary>

**Who:** Fleet/Owner write; Dispatcher reads.

1. Open **Fleet → Register truck**. Enter plate, description and capacity in metric tons; save.
2. Use the truck action menu to edit its record, inspect maintenance or start maintenance with a reason.
3. A truck already assigned/in transit cannot be retired or placed into ordinary maintenance directly. Coordinate **Replace truck** with Dispatcher and mark the original truck as needing maintenance.
4. After the real repair, choose **Complete maintenance**. Confirm its availability before recommending assignment.

Expected result: maintenance trucks cannot be assigned. Completing a delivery does not repair a truck. If capacity is corrected after assignment, clearance/departure recheck it and may reject the current load.

To retire an unused truck, open **Edit truck**, switch off **Active in the fleet**, and save. Assigned/in-transit trucks cannot be retired. Keep the record for history; use the same field to reactivate an eligible vehicle when appropriate.

</details>

## 7. Dispatch and assignment

**Assign → Driver accepts → Dispatcher clears.** Check every truck/crew member and prior OR restriction.

**A signed OR permits a reservation; receipt confirmation and eligibility permit dispatch.**

```mermaid
flowchart TB
    accTitle: Reserve does not mean depart
    accDescr: Signed OR upload permits one next reservation; company receipt and current eligibility are needed for dispatch.
    signed{"Previous signed OR uploaded?"}:::wait -->|No| no["No next assignment"]:::stop
    signed -->|Yes| reserve["One next reservation allowed"]:::action
    reserve --> receipt{"Previous company receipt confirmed?"}:::wait
    receipt -->|No| hold["Keep reservation; block next dispatch"]:::stop
    receipt -->|Yes| checks["Recheck truck, crew, license + conflicts"]:::action
    checks -->|Pass| clearance["Dispatcher clears; Driver may depart"]:::done
    checks -->|Fail| hold
    classDef action fill:#e8f1ff,stroke:#2563eb,color:#163566,stroke-width:2px
    classDef done fill:#e7f6ec,stroke:#208448,color:#16452a,stroke-width:2px
    classDef wait fill:#fff3d6,stroke:#b77910,color:#62420d,stroke-width:2px
    classDef stop fill:#ffebec,stroke:#c93b49,color:#72232c,stroke-width:2px
```

<details>
<summary><strong>Full procedure and exception rules</strong></summary>

**Who:** Dispatcher/Owner. Driver actions occur separately under My trips.

1. Open **Dispatch → Assign trip**. Select the order, truck, trip load, one Driver and one or two distinct Helpers.
2. Unavailable choices show a reason. Check capacity, license and crew; save the assignment.
3. Ask the assigned Driver to select **Accept trip**. Scheduled is not permission to depart.
4. When Accepted, select **Clear for dispatch**. If rejected, follow the returned reason and blocking trip ID. For an outstanding OR, the prior assigned Driver must record actual company receipt.
5. The Driver then selects **Record departure**. Eligibility is checked again, so a previously cleared trip can still be blocked by a subsequent change.
6. Follow the board through delivery, paperwork and closed stages. Completion comes from the Driver's receipt confirmation.

The board shows only a limited set of recent closed cards, not a full historical report. Data loads on page entry and after actions; refresh/reopen to observe changes made by another employee. There is no live GPS tracking.

### Crew, truck and exception actions

- **Change crew:** before departure only. New Driver must accept again; changed helpers invalidate existing clearance.
- **Replace truck:** before departure or in transit. Select a suitable replacement, give a reason, and tick original truck needs maintenance where true. The same trip continues; no new charge/pay is created by replacement.
- **Cancel:** before departure; mandatory reason.
- **Mark as failed:** after departure in eligible states; mandatory reason. Earnings for failed/partial work are not implemented.
- **Correct confirmation:** Owner only, completed trip, mandatory reason. Rejected if a later trip sharing a resource already departed, even if now closed. A later clearance can be revoked and must be obtained again.

</details>

## 8. My trips: Driver and Helper

**Driver:** accept, depart, deliver. **Helper:** assist and view own assignments; no Driver actions.

<details>
<summary><strong>Full procedure and exception rules</strong></summary>

1. Open **My trips**, check date, load, pickup and destination against instructions. Only assigned trips are listed.
2. Driver selects **Accept trip**, waits for Dispatcher clearance, then **Record departure** at departure.
3. At delivery, obtain the receiving party's signature and select **Record delivery**.
4. Follow the OR procedure below. Helper does not accept, depart, deliver or confirm on behalf of the Driver.

If a trip is missing, refresh and contact Dispatcher. Do not use another driver's login. If assigned information is wrong, have Dispatcher correct it before departure.

</details>

## 9. Signed OR, stamped copy and completion

**Signed OR upload → physical company handover → Driver confirms receipt.** JPEG/PNG, at most 5 MB; stamped copy is optional.

<details>
<summary><strong>Full procedure and exception rules</strong></summary>

**Who:** assigned Driver; assigned Helper only if explicitly enabled for upload. Only assigned Driver confirms receipt.

1. After recording delivery, open **Signed OR** on the trip card.
2. Select a legible **JPEG or PNG no larger than 5 MB** and upload. A PDF/HEIC or renamed non-image is rejected; export a genuine JPEG/PNG if needed.
3. Wait for success and **OR Uploaded** status. If the wrong image was selected, replace the signed OR before confirmation. Do not assume upload succeeded after a timeout—reload and inspect.
4. Physically submit the OR to the steel company for receipt. The app does not perform this handover.
5. After actual receipt, Driver opens **Confirm receipt**, checks the date/time and submits. Time must not precede recorded delivery or be in the future (subject to small server clock tolerance). Use the real receipt time, not a value chosen to unblock dispatch.
6. Verify **Completed**. The prior OR restriction is removed; any already reserved next trip stays reserved.
7. Upload a **Stamped copy (optional)** when available. It can be added after completion. It supports checking but is not required for completion.

Document buttons request temporary signed links. Reopen from the app if a link expires; never make the bucket public to solve access. Helpers without the enabled grant see no upload or document-opening controls. If confirmation was mistaken, notify Owner; Dispatcher cannot approve or undo it.

</details>

## 10. Dashboard, audit, permissions and finance

**Dashboard:** operations. **Audit/Permissions:** Owner review. **Finance/Reports:** persistent, role-scoped records on this branch.

<details>
<summary><strong>Full procedure and exception rules</strong></summary>

- **Dashboard:** Owner/Dispatcher review current trips and resource summaries; open the relevant operational screen to act.
- **Audit log:** Owner searches actions/entity/trace, and loads older entries. Records are read-only. Use the trace ID when reporting a failed request; omit private data from the report.
- **Permissions:** Owner inspects the stored role-capability table. This is a viewer, not a permission editor; role assignment happens in People. Conditional helper grants still depend on the configured flag.
- **Trip expenses, Payroll, Cash advances, Billing, Reports:** follow [the current financial procedures](sprint-5-6.md). Owner can enter/review expenses and inspect payroll/billing; HR records payroll payments and Accounting records client collections. DEMO amounts are fictional.

</details>

### Trip expenses and charge review

**Enter:** Owner, Dispatcher or the assigned Driver. **Review:** Accounting or an independent Owner. Helper has no expense-entry grant.

1. Open **Trip expenses → Add an expense line**, select the trip and Fuel/Toll, then enter the actual amount, description, purchase date, evidence reference and reason. Save each line while the sheet is **Entering**.
2. If no expenses occurred, use **Declare zero expenses** with a reason instead; missing lines are not a zero declaration.
3. Select **Submit for review**. An authorized different reviewer opens **Review declaration**, chooses **Approve** or **Return for changes**, records the reason and saves. Prior contributors and crew beneficiaries cannot approve, even with combined roles.
4. Accounting/Owner uses **Finalize agreed hauling charge** with the final amount, agreed reference amount, agreement reference and variance reason. A variance waits for **Approve variance** by a different non-beneficiary Owner. Dispatcher/crew cannot see commercial charges/rates.
5. Finalized expense/charge values cannot be silently rewritten. Refer disputed values to Owner and the documented correction limits; do not modify database values manually.

Owner configures future percentage versions under **Schedule a future earnings-rate version** on this page. The effective date must be a future Manila date. Departed trips retain their selected version.

### Payroll and personal statements

**HR** prepares/finalizes payroll and records actual payment. **Owner** inspects payroll and independently approves proposals; Owner alone cannot prepare positive adjustments or record payroll payment. **Driver/Helper** see only their own records.

1. Open **Payroll**. A trip stays **Pending Calculation** until completion, final charge and reviewed expenses/zero are ready. Earnings are attempted when the last prerequisite arrives; HR/Owner can use **Calculate ready trip earnings** to retry pending work.
2. HR opens **Prepare payroll period** with the 1st or 16th as its start. Review each employee’s trip/rate/gross, approved deductions, scheduled repayments, net and unpaid balance. A draft does not post repayments.
3. Where authorized, HR uses **Propose employee adjustment** with a written basis and period. Owner uses **Approve proposal** independently. Ordinary personal deductions and debit adjustments remain disabled by default pending D16.
4. After the period’s final Manila business day ends, HR selects **Finalize reviewed payroll**. Allocation and repayments post together once. Late ready earnings retain their original trip/date and carry forward into an open period.
5. HR opens **Record actual payroll payment**, enters actual amount/date/method/reference, and saves. The API refuses overpayment, self-payment or payment against a held statement. This records a transfer already made; it does not send money.
6. Owner may request **Reverse unpaid payroll** with an independent reason. The API restores linked repayments and unallocates earnings; any existing payment blocks this reversal. No paid-history deletion or refund workflow is implied.

Real percentage-pay, deductions and payroll repayments still require the documented D16 review and release approval. The application does not implement attendance, regular salaries, benefits or statutory contributions.

### Personal and operating advances

1. Crew request their own personal advance under **Cash advances → Request personal advance**. HR may prepare a request for an employee.
2. Owner uses **Approve arrangement** to record maximum amount, agreed fixed installment, start period, acknowledgment and reason. A named HR approver needs an unexpired Owner delegation; use **Delegate advance approval** / **Revoke delegation** where available. No requester or beneficiary approves their own request.
3. A different authorized HR actor uses **Record actual release** with the actual amount/date/reference and acknowledgment. Approval alone creates no debt, and partial releases cannot exceed approval.
4. Finalized payroll posts the smaller of the agreed installment, outstanding released balance and available pay after authorized deductions. Inspect movement history and remaining balance; drafts do not post repayments.
5. For business float, HR uses **Request trip operating funds** and selects the assigned crew custodian/trip. It remains separate from personal debt. Record unused funds under **Record unused operating funds returned** and obtain independent **Review operating reconciliation** after expense review. A shortage or unsupported multi-arrangement allocation stays under review.

Operating approval currently shares an arrangement form, but its installment is unused for payroll. There is no general repayment-schedule amendment or paid-record reconciliation screen; see [policy limits](../decisions/financial-policies.md#implementation-coverage-and-limits).

### Billing and collections

**Accounting** builds, issues and records collections. **Owner** has read-only billing plus independent requested-void approval.

1. Open **Billing → Build client billing batch**; select one client, an inclusive past/present delivery cutoff and one or more **Ready unbilled trips for that client**. Set terms (30 days by default) and save.
2. Eligibility requires completed trip, finalized charge, active signed OR, recorded receipt, no hold and no active bill allocation. Earlier delivery periods/orders can carry over. Expense/payroll finalization, client payment, stamped copy and whole-order completion are separate.
3. Inspect **Lines and collections**, then select **Issue reviewed invoice**. Issued amounts/lines are immutable. Invoice state and payment position remain separate.
4. Use **Record actual collection** for actual amount/date/method/reference. Allocation stops at outstanding balance; excess remains visible as unallocated credit. The app does not collect money itself.
5. Accounting uses **Request independent void approval** with a reason; a different Owner can **Approve unpaid invoice void**. Any payment record blocks void/rebilling. Refund, credit-note and excess-credit reallocation workflows are not implemented.

### Reports, presentation and connection handling

**Reports** shows each role’s remit: operations/document exceptions; authorized pay, advance and client balances; and fleet maintenance/replacements. Crew see their own records. Operational counts describe the current page, while financial totals cover authorized records; use **Previous / Next** and **Refresh** deliberately.

The separate `/preview.html` role picker is a design tool, not sign-in or a way to grant access. The presentation seed adds fictional persisted `DEMO` records and a notice, without creating Clerk logins. See [presentation setup](sprint-5-6.md#presentation-dataset). Demo evidence is visibly fictional and still checks authorization.

Only a production frontend build registers the public offline-help worker. It does not cache business records/tokens or queue receipt/payment actions. Reconnect and confirm a saved server result before treating an action as complete.

## 11. Troubleshooting and interrupted operations

**Read the error, refresh the record, contact the responsible role.** Avoid duplicate submissions after timeouts.

| Symptom                              | Action                                                                                                     |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| Cannot open app                      | Ask administrator to check src/frontend/API/database/tunnel; local URLs refer to your own computer         |
| Sign-in works, access denied         | Owner checks active local employee, identity link and role; do not create duplicate identities             |
| Button absent                        | Check My account capabilities and trip state; permissions may intentionally hide it                        |
| `DISPATCH_BLOCKED`                   | Identify the blocking trip and arrange actual OR handover/Driver confirmation                              |
| License/crew/capacity rejection      | Fleet/Owner correct license/capacity, Owner resolves active status, Dispatcher changes eligible crew/truck |
| Upload rejected                      | Check real file type, size, delivery status and assignment; retry only after resolving issue               |
| Signed link expired                  | Open document again within app                                                                             |
| Not found on another person's record | Access may be deliberately concealed; ask authorized staff rather than guessing IDs                        |
| Save/confirmation times out          | Reload current record before retrying; do not create a duplicate trip/order/payment                        |
| Page shows old information           | Refresh or reopen; operational lists are not live push subscriptions                                       |

**Owner expense page unexpectedly forbidden after updating:** ask the developer/operator to apply migrations through `0006`, restart the API and refresh the account/page. That migration repairs the missing read grant. Do not add HR or remove legitimate Owner access to work around a schema mismatch.

During an outage, Dispatcher records a paper log with order/trip reference, actor and actual event times. Follow BM's operational contingency decision; do not claim the application cleared a trip while unavailable. Once restored, authorized roles reconcile records and duplicates in order. There is no offline queue or proven recovery-time guarantee today.
