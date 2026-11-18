# BM Enterprises frontend

React/Vite workspace for hauling operations. See the [system folder architecture](../../docs/architecture.md#repository-folder-architecture) for the complete repository tree and placement rules, or [local setup](../../docs/runbooks/development.md#4-local-setup) for API, database and Clerk configuration.

Run these commands from `src/frontend/`:

```powershell
npm.cmd ci
npm.cmd run dev
```

Open `http://localhost:5173`. The API must be running on port 8000; Vite proxies `/api/v1` requests to it. `/preview.html` uses fictional data for visual review.

With Docker Desktop running Linux containers, start the full development stack from the repository root:

```powershell
docker compose up --build --watch
```

Docker runs Vite inside the frontend container, FastAPI inside the backend container, and PostgreSQL with persistent storage. Do not also start standalone Vite or FastAPI on ports 5173 and 8000. Compose syncs source edits for hot reload and rebuilds services when dependency manifests change. Restart the Compose command after changing `compose.yml` or the root `.env`.

Open `http://localhost:5173` for local use. To share with friends, keep the Docker stack running and start ngrok on the host in another terminal:

```powershell
ngrok http http://127.0.0.1:5173
```

The root `.env` must set `VITE_PUBLIC_FRONTEND_URL` to the exact ngrok HTTPS origin and include it in `CLERK_AUTHORIZED_PARTIES`. Restart Compose if that URL changes. Vite sends `/api/v1` to `backend:8000` over Docker's network, so one ngrok tunnel serves both the frontend and API. Keep the `pgdata` volume to retain employee accounts; `docker compose down` preserves it.

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
