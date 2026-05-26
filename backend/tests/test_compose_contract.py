from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]


def test_compose_declares_database_only() -> None:
    """Verifies that Compose only declares the Phase 1 database service.

    Assertions:
        - `postgres` is present for local database development.
        - Redis, Ollama, backend, frontend, and worker containers are
          deferred until their own phases.
        - PostgreSQL uses a named volume so local data is not tied to a
          container ID.
    """
    compose_text = (ROOT_DIR / "compose.yml").read_text(encoding="utf-8")

    assert "  postgres:" in compose_text

    for deferred_service in (
        "redis",
        "ollama",
        "backend",
        "frontend",
        "worker",
    ):
        assert f"  {deferred_service}:" not in compose_text

    assert "postgres-data:" in compose_text
    assert "redis-data:" not in compose_text
    assert "ollama-data:" not in compose_text
    assert "storage-data:" not in compose_text
