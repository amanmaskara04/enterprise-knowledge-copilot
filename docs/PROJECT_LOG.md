# Project Log

## Project

**Enterprise Knowledge Copilot**

Repository:

`amanmaskara04/enterprise-knowledge-copilot`

Development environment:

- Windows 11
- PowerShell
- Python 3.12
- Docker Desktop
- PostgreSQL 16 with pgvector
- Git and GitHub
- VS Code

---

# Phase 0 — Environment and Tooling

## Objective

Prepare the Windows development environment and project repository before application development begins.

## Completed

The following were installed and verified:

- Python
- pip
- Git
- Docker Desktop
- Docker Compose
- VS Code

The project repository was created and connected to GitHub.

The project virtual environment was created at:

`D:\dev\enterprise-knowledge-copilot\.venv`

Python is installed at:

`D:\tools\Python312`

Docker Desktop is installed at:

`D:\tools\Docker`

Docker persistent data is configured to use:

`D:\Docker\DockerDesktopWSL`

Development cache locations include:

- `D:\cache\pip`
- `D:\cache\temp`

Node.js and npm were intentionally not installed during Phase 0 because they are not required yet. They are planned for a later phase.

## Storage Rule

Existing software and data on the C: drive were not moved, deleted, or uninstalled.

New project-related files, caches, and large data are placed on the D: drive whenever practical.

## Verification

Python was verified from the project virtual environment.

Docker client and server were verified.

Docker Desktop was started and the Linux Docker context was confirmed.

Git and GitHub repository connectivity were verified.

---

# Phase 1 — Foundation

## Objective

Build the initial backend foundation, establish database connectivity, containerize the application, and create a basic test suite.

## Task 1 — Project Structure

Created the initial backend structure:

- `backend/app/`
- `backend/app/api/`
- `backend/app/core/`
- `backend/app/db/`
- `backend/app/models/`
- `backend/app/schemas/`
- `backend/tests/`

Created the initial project configuration files including:

- `.gitignore`
- `.env.example`
- `docker-compose.yml`
- `backend/requirements.txt`
- `backend/requirements-dev.txt`

The project uses a project-local Python virtual environment.

---

## Task 2 — Python Dependencies

Runtime dependencies were installed and pinned.

Runtime versions:

```text
fastapi==0.142.2
uvicorn[standard]==0.54.0
pydantic-settings==2.15.0
sqlalchemy==2.1.3
psycopg[binary]==3.3.6
```

Development dependencies:

```text
pytest==9.1.1
httpx==0.28.1
```

The PostgreSQL driver uses the SQLAlchemy URL scheme:

`postgresql+psycopg://`

---

## Task 3 — Environment Configuration

Environment-based configuration was implemented with Pydantic Settings.

Supported configuration variables:

```text
APP_NAME
ENVIRONMENT
DEBUG
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

`.env` is ignored by Git.

`.env.example` contains placeholder values and is safe to commit.

The application loads `.env` from the project root rather than depending on the current working directory.

A database password is present in the local `.env` file but is intentionally not recorded in this project log.

---

## Task 4 — FastAPI and Health Endpoints

The FastAPI application was created.

The application exposes:

### `GET /health`

A liveness endpoint that does not require database connectivity.

Expected response:

```json
{
  "status": "ok"
}
```

### `GET /health/db`

A database readiness endpoint.

It executes:

```sql
SELECT 1
```

through SQLAlchemy.

When the database is unavailable, the endpoint returns HTTP `503 Service Unavailable` with a safe error message.

### Documentation

FastAPI-generated documentation is available through:

- `/docs`
- `/redoc`
- `/openapi.json`

The `/docs` endpoint was verified successfully with HTTP status `200`.

---

## Task 5 — SQLAlchemy Database Foundation

Created the SQLAlchemy database foundation.

Components:

- SQLAlchemy engine
- Session factory
- FastAPI database dependency
- Declarative ORM base

The engine uses:

- `pool_pre_ping=True`
- a five-second connection timeout

No application tables have been created yet.

Tables are planned for Phase 2.

### Issue and Fix

An early database-unavailable test caused a long connection wait and an SQLAlchemy cleanup error when the request was interrupted.

The connection configuration was updated with:

```python
connect_args={"connect_timeout": 5}
```

This provides a bounded connection attempt instead of allowing the request to hang indefinitely.

---

# Task 6 — PostgreSQL and pgvector

PostgreSQL was added through Docker Compose.

Database image:

```text
pgvector/pgvector:pg16
```

The database service uses:

- PostgreSQL 16
- pgvector
- environment-based credentials
- a health check using `pg_isready`
- a Compose-managed named volume
- initialization scripts

The host database port is:

`5432`

The initialization script is:

`db/init/01-extensions.sql`

It contains:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Verification

The database container was confirmed healthy.

The PostgreSQL `vector` extension was verified with `psql`.

The installed extension was reported as:

```text
vector 0.8.7
```

The API database health endpoint was also verified successfully.

---

# Task 7 — Dockerize the API

The FastAPI application was containerized.

Created:

- `backend/Dockerfile`
- `backend/.dockerignore`

The API image uses Python 3.12 slim.

The container runs Uvicorn on:

`0.0.0.0:8000`

The API container runs as a non-root user.

Docker Compose was configured with two services:

- `db`
- `api`

The API depends on the database health check before starting.

Inside Docker Compose, the API connects to PostgreSQL using:

`db`

rather than:

`localhost`

## Verification

The API image built successfully.

Both services started successfully.

The API container reported:

```text
Uvicorn running on http://0.0.0.0:8000
```

Host verification:

```text
GET /health     -> 200 OK
GET /health/db  -> 200 OK
GET /docs       -> 200 OK
```

Docker Compose logs confirmed successful application startup and successful health requests.

---

# Task 8 — Pytest

Pytest was added for automated testing.

A root-level `pytest.ini` was created so that the project root is included in Python's import path.

Configured markers:

- `unit`
- `integration`

Tests currently cover:

- database URL configuration
- `/health`
- `/health/db`

The database test is marked as an integration test.

## Results

Full test suite:

```text
3 passed
```

Non-integration tests:

```text
2 passed, 1 deselected
```

Integration tests:

```text
1 passed, 2 deselected
```

Pytest produced a deprecation warning involving the current Starlette/httpx test-client combination. The tests themselves passed, so the dependency set was not changed merely to remove the warning.

---

# Important Decisions

## No Application Tables Yet

SQLAlchemy and PostgreSQL connectivity were established before creating application tables.

Tables are intentionally deferred to Phase 2.

## No Node.js Yet

Node.js and npm are intentionally absent because they are not required for the current backend foundation.

## No Authentication Yet

Authentication was not added because it is outside the current Phase 1 scope.

## No Redis Yet

Redis was not introduced because it is not required for the current foundation.

## No LlamaIndex

The project uses direct FastAPI, SQLAlchemy, and PostgreSQL/pgvector foundations rather than adding an additional RAG framework at this stage.

## No Database Migration Tool Yet

Database migrations are planned for a later phase when application tables are introduced.

---

# Problems Encountered and Fixes

## Docker Daemon Initially Unavailable

Docker commands initially failed because the Docker daemon was not running.

Docker Desktop was started, after which Docker client/server operations worked normally.

## Dockerfile Build Failure

The initial Dockerfile creation contained an incorrect PowerShell line-continuation character.

The Dockerfile was corrected and the image subsequently built successfully.

## Database Connection Timeout

The database health route initially waited too long when PostgreSQL was unavailable.

A five-second SQLAlchemy connection timeout was added.

## Pytest Import Configuration

Tests initially had an import-path problem because the project root was not on Python's import path.

A root-level `pytest.ini` was created with:

```ini
[pytest]
testpaths = backend/tests
pythonpath = .
markers =
    unit: tests that do not require external services
    integration: tests that require the PostgreSQL database
```

The earlier `backend/pytest.ini` was removed.

## Test Assertion Error

An early test incorrectly expected the database password not to appear in the constructed database URL.

The test was corrected to verify the URL scheme, host/port, and username without exposing the password.

---

# Current Architecture

```text
Client
  |
  v
FastAPI
  |
  +--> /health
  |
  +--> /health/db
  |
  v
SQLAlchemy
  |
  v
PostgreSQL + pgvector
```

Docker Compose currently provides:

```text
api: 8000
 |
 +----> db:5432
```

---

# Phase 1 Exit Criteria

The following foundation requirements have been verified:

- Virtual environment works
- FastAPI application starts
- `/health` works
- `/health/db` works
- `/docs` works
- PostgreSQL starts successfully
- pgvector extension is enabled
- API runs inside Docker
- API connects to PostgreSQL through Compose
- Pytest suite passes
- `.env` is ignored by Git
- No database password is recorded in project documentation
- Project changes are committed and pushed to GitHub

---

# Next Phase

Phase 2 will introduce the database model layer and begin building the data foundation for document ingestion and retrieval.

The project will continue to introduce technologies deliberately rather than adding infrastructure before it is required.


---

# Phase 2: Document Data Layer

Phase 2 gave the project its relational foundation. Users and documents now live in PostgreSQL with enforced relationships, schema changes go through Alembic migrations, and the API can create, list, read, update, and delete document records with strict per-owner isolation. No file bytes are stored yet. A document is a metadata record, and actual upload and storage arrive in Phase 3.

## What was built

- Alembic migrations, with revision `5b45bb480d7c` creating `users` and `documents`
- SQLAlchemy 2.x models (`User`, `Document`) with a one-to-many relationship
- Pydantic schemas for users, documents, and a generic paginated response
- A service layer for users and documents, plus a document status state machine
- Endpoints: `POST /users`, `GET /users/me`, and `POST/GET/PATCH/DELETE` on `/documents`
- A separate `enterprise_knowledge_test` database, built by running the real migrations
- 20 tests (12 unit, 8 integration)

## Design decisions

Primary keys are UUIDs rather than sequential integers, which makes identifiers harder to guess. This is not a substitute for authorization, which is why every document query also filters by owner. Requesting another user's document returns 404, not 403, so the API doesn't reveal that the document exists.

Document status is a `varchar` with a `CHECK` constraint instead of a native PostgreSQL enum, because enums are awkward to change in migrations. The allowed transitions are `pending -> processing`, `processing -> ready`, `processing -> failed`, and `failed -> pending`. Anything else raises a domain error that the API maps to HTTP 409.

Documents reference users with `ON DELETE CASCADE`, so deleting a user deletes their documents. Constraint and index names follow a naming convention on the metadata, so migrations produce predictable names. API-created emails are lowercased in the service layer. A database-level lowercase check was considered and deliberately not added.

Authentication is intentionally not implemented. A development-only `X-Dev-User-Id` header identifies the caller and works only when `ENVIRONMENT=development`. It is marked as temporary in the code and will be replaced by real authentication in Phase 7. It must never reach production.

## Problems found and fixed

- Postgres and the API were published on all network interfaces. Both ports are now bound to `127.0.0.1`.
- The Docker build failed because `psycopg` was installed without the binary extra. The requirements now pin `psycopg[binary]`.
- Introducing a root `requirements.txt` required changing the Docker build context to the repository root and updating the `COPY` paths.
- `alembic.ini` contained a UTF-8 BOM that broke the config parser. It was rewritten without one.
- `alembic current` hung because the migration environment reused the application's engine. It now builds its own engine with `NullPool` and a connect timeout.
- Selecting the test database through `DATABASE_URL` did not work. The fix is `alembic -x test_db=true`, which makes `env.py` use the test database URL.
- The test fixtures ran migrations when `conftest.py` was imported, so even unit tests touched the database. Migrations now run inside the database fixture, and `pytest -m unit` runs with no database at all.

## Exit criteria verified

- Migrations apply, downgrade, and re-apply cleanly on both databases
- Table structure, constraints, and indexes inspected directly in `psql`
- A real SQL join across `documents` and `users` returns the expected rows
- Cross-user access is blocked (another user's document returns 404, their list is empty)
- Duplicate email returns 409, invalid input returns 422, a missing identity header returns 401
- Invalid state transitions return 409
- The test fixture refuses to run against any database whose name does not end in `_test`
- Full suite passes: `20 passed`

## Known limitations

- There is no real authentication or password handling yet.
- No file upload or storage yet (`storage_key` is metadata only).
- `ready` is a terminal state, so re-processing a document will need a new transition later.
- The README has not been refreshed for Phase 2.

# Next Phase

Phase 3 introduces PDF upload, file storage, and text extraction, turning document records into content the system can read.