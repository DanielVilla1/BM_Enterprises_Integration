# First Owner in the hosted demo

The Cloudflare frontend and Render backend can connect successfully while sign-in displays **Your account is not set up yet**. Clerk authenticates the person; the application also requires an active employee linked to that Clerk user ID in the database used by Render. A new hosted database does not inherit the local development employees.

## One-time setup from your PC

1. In the Clerk Dashboard, select the same **Development** instance used by the deployed frontend and backend. Open **Users**, select the account you signed in with, and copy its `user_...` ID and sign-in email.
2. In Render's backend **Environment** page, copy the working `DATABASE_URL` privately. Preserve the password encoding that allowed migrations to complete.
3. Open PowerShell in the repository root and run:

   ```powershell
   .\src\backend\.venv\Scripts\python.exe .\tools\scripts\bootstrap_hosted_owner.py
   ```

4. Paste the hosted database URL at the hidden prompt and press Enter. Enter your name, sign-in email and Clerk user ID at the following prompts.
5. When it reports **Owner created**, refresh the Cloudflare website. No Render or frontend redeployment is needed for this database change.

The command uses the local backend virtual environment. It accepts only hosted Supabase PostgreSQL URLs, requires TLS, keeps the database URL in process memory, suppresses raw database exception details and delegates to the existing audited Owner bootstrap service. It creates only the first Owner and refuses when any employee already exists. It does not reset or copy records, modify local `.env` files, or provision Clerk users. If it refuses because employees already exist, investigate the existing records and use the existing Owner's account-management workflow; do not remove the bootstrap guard.

## Other roles and a blocked Owner

Creating the first Owner does not provision Dispatcher, Fleet Manager, Driver, Helper, HR/Payroll or Accounting accounts. Once signed in as that Owner, use **People** to create the required employees, assign their intended roles, link each employee to its exact Clerk user ID and activate the records. Existing Clerk identities still need those employee records in the database used by Render. Local employee records are not automatically transferred.

On blocked-account screens, the app displays the signed-in email and provides **Sign out** independently of account loading. Sign out and select the exact Owner identity used during bootstrap. Until this UI update is deployed, a private browser window provides a separate sign-in session; in Brave or Chrome on Windows, press **Ctrl + Shift + N**.

If the bootstrapped Owner is also blocked, verify that its stored `clerk_user_id` matches the ID of the current signed-in user in the same Clerk instance, that the employee is active and that the setup command used the same Supabase project/database as Render. A successful bootstrap in a different database, or with a different Clerk user ID, does not authorize the current browser session. Refreshing or rebuilding the frontend does not change employee records. Do not change authentication rules or grant every signed-in user Owner access to work around missing links.

## Repair an existing Owner's link

When the first Owner exists but was linked to a different Clerk user ID, a privileged operator can run:

```powershell
.\src\backend\.venv\Scripts\python.exe .\tools\scripts\repair_hosted_owner.py
```

Enter the working `DATABASE_URL` copied from Render, the existing Owner's email and the `CLERK_SECRET_KEY` copied from Render's Development configuration. Both credentials use hidden local prompts. The command reads the official Clerk directory and finds the unique user whose verified primary email matches. It repairs only the existing Owner's identity link and activation through the audited employee service; it never creates employees or assigns roles. It refuses other roles, mismatched or unverified emails and identities already held by another employee. Repeating a successful repair does not add duplicate change records.

This recovery tool requires direct database-operator and Clerk API credentials and is not exposed through any web endpoint. If it reports the Owner is linked correctly but the website still rejects that identity, compare the website's own **Sign-in account ID** with the verified account ID printed by the operator command and confirm Render points to that same database. The remaining roles still need their intended employee records, links and activation through **People**.

Render Free has no interactive shell, so run this operator command on your PC. The website and database remain hosted remotely. See [Render Free limitations](https://render.com/docs/free) and the [development guide](development.md) for local environment setup.
