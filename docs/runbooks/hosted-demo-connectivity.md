# Hosted demo connection failures

The demo frontend runs on Cloudflare and calls the separate Render API. Render Free can sleep after 15 minutes without traffic and take about a minute to wake; see [Render's documented limitations](https://render.com/docs/free#spinning-down-on-idle). A 10-second account-request timeout can therefore fail while the service is starting.

## Frontend startup behavior

The frontend first waits up to 90 seconds for the public `/api/v1/health` endpoint to return `{"status":"ok"}`. It then obtains the Clerk session token and requests `/api/v1/me` with the normal 10-second timeout. This keeps the short-lived token out of the startup wait. The loading screen explains the possible initial delay.

Business commands retain their normal timeout and are not automatically replayed. Timeouts, non-JSON gateway errors and unexpected responses have distinct messages; none requires displaying raw server responses or credentials.

## Immediate operator check

1. Open the deployed backend's `/api/v1/health` address directly and wait for `{"status":"ok"}`.
2. Return to the Cloudflare website and select **Try again**.
3. If it still fails, open the Render service and select **Logs** in its left sidebar. Refresh the Cloudflare website once, then inspect the newest log entries at the matching time. Keep exception types and error messages, but omit credentials, connection strings and bearer tokens when sharing evidence.

A successful health response proves that the API process is responding; it does not prove that authenticated database reads work. A successful CORS preflight proves that the configured browser origin is allowed; it does not prove that the user's token or employee record is valid. A screenshot showing **Service unreachable** alone cannot establish a cold start as the cause.

When the request succeeds but the page shows **Your account is not set up yet**, follow the [first hosted Owner procedure](hosted-demo-owner.md). Local development records are separate from the hosted database.

## Publishing the fix

The startup code must be included in the branch Cloudflare builds, and a new build must succeed before the deployed website uses this behavior. The `VITE_API_BASE_URL` variable belongs in Cloudflare's **build** settings and must name the actual HTTPS API origin, without `/api/v1` or a trailing slash. Changing a build variable or local source alone does not update the deployed assets.
