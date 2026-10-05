import pytest

from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.main import app

client = TestClient(app)


@pytest.mark.unit
def test_database_url_uses_psycopg():
    assert settings.database_url.startswith("postgresql+psycopg://")
    assert f"@{settings.postgres_host}:{settings.postgres_port}/" in settings.database_url
    assert f"{settings.postgres_user}:" in settings.database_url


@pytest.mark.unit
def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.integration
def test_health_db():
    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
