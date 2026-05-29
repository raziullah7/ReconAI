import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    settings = Settings(
        DATABASE_URL="postgresql://reconai:reconai@localhost:5432/reconai",
    )
    return TestClient(create_app(settings))


def test_health_endpoint_returns_ok(client: TestClient) -> None:
    """Verifies that the health endpoint reports a usable app shell.

    Mocks:
        client: Uses the FastAPI test client so the route is exercised
            through the ASGI app without opening a network socket.

    Assertions:
        - Response status is 200 so compose and probes have a stable
          readiness target.
        - Response body contains `status`, `service`, and `version` so
          callers can identify the running service.
        - Response body does not include reconciliation, tenant data, or
          worker state because health stays limited to app metadata.
    """
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "reconai-backend",
        "version": "0.1.0",
    }
    assert "tenant" not in response.json()
    assert "worker" not in response.json()
    assert "reconciliation" not in response.json()
