from collections.abc import Generator
from pathlib import Path
from urllib.parse import urlparse
import subprocess
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from backend.app.api.deps import get_db
from backend.app.core.config import settings
from backend.app.main import app


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEST_DATABASE_URL = settings.test_database_url
TEST_DATABASE_NAME = urlparse(TEST_DATABASE_URL).path.lstrip("/")

if not TEST_DATABASE_NAME.endswith("_test"):
    raise RuntimeError(
        f"Refusing to run tests against non-test database: {TEST_DATABASE_NAME}"
    )

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 5},
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(scope="session")
def test_database_schema() -> Generator[None, None, None]:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            "-x",
            "test_db=true",
            "upgrade",
            "head",
        ],
        cwd=PROJECT_ROOT,
        check=True,
    )
    yield


@pytest.fixture
def db_session(
    test_database_schema: None,
) -> Generator[Session, None, None]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(
    db_session: Session,
) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def clean_database(
    db_session: Session,
) -> Generator[None, None, None]:
    yield

    db_session.execute(
        text("TRUNCATE TABLE documents, users RESTART IDENTITY CASCADE")
    )
    db_session.commit()
