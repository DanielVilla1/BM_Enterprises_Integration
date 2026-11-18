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

Render Free has no interactive shell, so run this operator command on your PC. The website and database remain hosted remotely. See [Render Free limitations](https://render.com/docs/free) and the [development guide](development.md) for local environment setup.
