# BM Enterprises frontend

React/Vite workspace for hauling operations. See the [system folder architecture](../../docs/architecture.md#repository-folder-architecture) for the complete repository tree and placement rules, or [local setup](../../docs/runbooks/development.md#4-local-setup) for API, database and Clerk configuration.

Run these commands from `src/frontend/`:

```powershell
npm.cmd ci
npm.cmd run dev
```

Open `http://localhost:5173`. The API must be running on port 8000; Vite proxies `/api/v1` requests to it. `/preview.html` uses fictional data for visual review.

For Docker Desktop, run from the repository root with the root `.env` configured:

```powershell
docker compose up --build --watch
```

Stop standalone Vite and API processes first so ports 5173 and 8000 are free. If a local PostgreSQL server uses port 5432, set `POSTGRES_EXTERNAL_PORT=5433` in the root `.env`. Docker uses its own persistent `pgdata` database; existing local database records are not copied.

A fresh database needs an active employee linked to the Clerk identity, even if that identity is already an Owner in another database. Create the first Owner once, using the same Clerk user ID:

```powershell
docker compose exec backend python -m backend.scripts.bootstrap_owner --name "Owner Name" --email "owner@example.com" --clerk-user-id "user_REPLACE_ME"
```

This audited command refuses to run if employees already exist. Keep the `pgdata` volume to retain accounts between starts; `docker compose down` preserves it.

Compose syncs source edits into the containers. Vite applies hot reload, FastAPI reloads Python changes, and dependency or Dockerfile changes rebuild the affected service. Windows `node_modules`, Python virtual environments and local `.env` files are excluded. After changing the root `.env`, restart the Compose command to apply the new settings.

Keep ngrok running on the host in another terminal:

```powershell
ngrok http http://127.0.0.1:5173
```

Set `VITE_PUBLIC_FRONTEND_URL` in the root `.env` to the exact HTTPS URL ngrok provides, then restart Compose if it changed. The browser uses `/api/v1` on that same origin; Vite forwards those requests to `backend:8000` inside Docker. Include the public origin in `CLERK_AUTHORIZED_PARTIES` for authenticated API access.

| Directory                          | Responsibility                                      |
| ---------------------------------- | --------------------------------------------------- |
| `src/pages/`                       | Screen composition: connects hooks and presentation |
| `src/components/<feature>/`        | Feature-specific screens and forms                  |
| `src/hooks/`                       | Loading and action coordination                     |
| `src/services/`                    | Feature API calls                                   |
| `src/store/`                       | Zustand state                                       |
| `src/shared/components/`           | Reusable UI, shell and sign-in layout               |
| `src/shared/services/`             | HTTP, Clerk and shared asynchronous loading         |
| `src/shared/utils/`                | Pure helpers                                        |
| `src/shared/mockups/`              | Clearly labeled fictional preview records           |
| `tests/unit/`, `tests/components/` | Frontend regression tests                           |
| `design-preview/`                  | Isolated sample-data preview harness                |

Components receive props and emit callbacks. Services handle network access. The API enforces business rules and permissions. Financial pages marked **Soon** are previews.

```powershell
npm.cmd test
npm.cmd run lint
npm.cmd run format:check
npm.cmd run build
```

The application uses JavaScript and JSDoc. Its dependency manifest and lockfile belong here; the repository root has no npm application.
