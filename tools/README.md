# Repository tools

Keep repository-wide maintenance scripts in `scripts/`. Application-specific operator commands remain with the application, such as the backend Owner bootstrap and Clerk reconciliation commands.

From the repository root:

```powershell
python tools/scripts/check_docs.py
```

The documentation checker uses only the Python standard library. It checks local Markdown links, heading anchors and fenced blocks without contacting external services.

Run backend modules from the root using the Python environment where the backend dependencies are installed:

```powershell
src/backend/.venv/Scripts/python tools/scripts/backend.py uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

`backend.py` adds the repository's `src/` directory to `PYTHONPATH` and keeps the working directory at the root, so backend imports and root `.env` loading work together. It also supports Alembic and operator commands:

```powershell
src/backend/.venv/Scripts/python tools/scripts/backend.py alembic -c src/backend/alembic.ini upgrade head
src/backend/.venv/Scripts/python tools/scripts/backend.py backend.scripts.export_openapi
```

Start Vite separately from `src/frontend/` with `npm.cmd run dev`.

Uvicorn commands through the launcher default to `--no-proxy-headers`. Enable proxy headers only with a reviewed trusted-ingress configuration; see the [security deployment gates](../docs/decisions/security-hardening.md#proxy-and-worker-deployment-gate).
