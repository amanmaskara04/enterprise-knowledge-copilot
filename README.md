# Enterprise Knowledge Copilot

A portfolio project for building an enterprise knowledge assistant that will eventually let users upload documents, ask questions, and receive grounded answers with citations.

## Current Status

**Phase 1 — Foundation: complete**

The project currently has:

- Python 3.12 development environment
- FastAPI application
- Pydantic Settings configuration
- SQLAlchemy database foundation
- PostgreSQL with pgvector
- Docker Compose development environment
- Containerized API service
- Health and database-readiness endpoints
- Pytest unit and integration tests
- Environment-variable based configuration

Document ingestion, embeddings, retrieval, and question answering are planned for later phases.

## Project Structure

```text
enterprise-knowledge-copilot/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── health.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   ├── models/
│   │   ├── schemas/
│   │   │   └── health.py
│   │   └── main.py
│   ├── tests/
│   │   └── test_health.py
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── requirements.txt
│   └── requirements-dev.txt
├── db/
│   └── init/
│       └── 01-extensions.sql
├── docs/
│   └── PROJECT_LOG.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── pytest.ini
└── README.md
```

## Development Environment

The project uses:

- Windows 11
- PowerShell
- Python 3.12
- A project-local virtual environment at `.venv`
- Docker Desktop
- PostgreSQL 16 with pgvector
- Git and GitHub
- VS Code

Project files and development caches are kept on the D: drive according to the project storage rule.

## Configuration

Runtime configuration uses environment variables and the local `.env` file.

Supported environment variable names:

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

`.env` is intentionally ignored by Git.

`.env.example` contains safe placeholder values.

Never commit real passwords or other secrets.

## Python Dependencies

Runtime dependencies are pinned to the versions used during Phase 1:

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

## Running the API Locally

Activate the project virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start the API from the project root:

```powershell
python -m uvicorn backend.app.main:app --reload
```

The API listens on port `8000`.

### API Endpoints

- `GET /health` — application liveness check. Does not require the database.
- `GET /health/db` — database readiness check using `SELECT 1`.
- `/docs` — Swagger UI.
- `/redoc` — ReDoc.
- `/openapi.json` — generated OpenAPI schema.

## Docker Compose

Start the database and API services:

```powershell
docker compose up -d
```

Check service status:

```powershell
docker compose ps
```

The development services are:

| Service | Purpose | Host Port |
|---|---|---:|
| `db` | PostgreSQL 16 + pgvector | 5432 |
| `api` | FastAPI application | 8000 |

Inside Docker Compose, the API connects to PostgreSQL using the service name `db`, not `localhost`.

PostgreSQL data is stored in a Compose-managed named Docker volume.

Stop the services without deleting database data:

```powershell
docker compose down
```

Do not use `docker compose down -v` unless intentionally resetting the database volume.

## Database

The PostgreSQL service uses:

```text
pgvector/pgvector:pg16
```

The initialization script enables the PostgreSQL `vector` extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

The application currently uses SQLAlchemy for database connectivity, but no application tables have been created yet. Tables are planned for Phase 2.

## Testing

Run the complete test suite:

```powershell
pytest
```

Run only non-integration tests:

```powershell
pytest -m "not integration"
```

Run integration tests:

```powershell
pytest -m integration
```

Phase 1 test result:

```text
3 passed
```

The integration test verifies the database-backed `/health/db` endpoint while PostgreSQL is running.

## Git Workflow

The project uses clear commit prefixes such as:

```text
chore:
feat:
test:
docs:
```

GitHub repository:

```text
amanmaskara04/enterprise-knowledge-copilot
```

## Roadmap

Planned phases include:

1. Database models and migrations
2. Document upload and storage
3. PDF text extraction
4. Chunking
5. Embeddings
6. Vector storage and retrieval
7. Grounded question answering
8. Citations and evaluation
9. Production-oriented improvements

Technologies are introduced deliberately by phase rather than added prematurely.

## Storage Rule

Existing software and data on the C: drive are not moved or removed.

New project files, caches, models, and other large project-related data should use the D: drive whenever practical.

Development cache locations include:

```text
D:\cache\pip
D:\cache\temp
```
