from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app

LOCAL_DATABASE_URL = "postgresql+psycopg://reconai:reconai@localhost:5432/reconai"
LOCAL_FRONTEND_ORIGIN = "http://127.0.0.1:5173"


def test_cors_allows_local_frontend_origin() -> None:
    """Verifies local Vite can call the FastAPI Base API in M2.2.

    Summary:
        Sends a browser-style CORS preflight request to a Base API route.
    Mocks:
        FastAPI TestClient exercises middleware without opening a socket.
    Assertions:
        The configured origin is allowed, GET is accepted, and credentials are
        not enabled for the local Base API surface.
    """
    settings = Settings(
        DATABASE_URL=LOCAL_DATABASE_URL,
        BACKEND_CORS_ORIGINS=LOCAL_FRONTEND_ORIGIN,
    )
    client = TestClient(create_app(settings))

    response = client.options(
        "/v1/reconciliation-cases",
        headers={
            "Origin": LOCAL_FRONTEND_ORIGIN,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == LOCAL_FRONTEND_ORIGIN
    assert "GET" in response.headers["access-control-allow-methods"]
    assert "content-type" in response.headers["access-control-allow-headers"].lower()
    assert "access-control-allow-credentials" not in response.headers
