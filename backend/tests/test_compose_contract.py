from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]


def test_compose_declares_foundation_services() -> None:
    """Verifies that compose declares the services Phase 1 promises.

    Assertions:
        - `postgres`, `redis`, `ollama`, `backend`, `frontend`, and
          `worker` services are present.
        - Stateful services use named volumes so local data is not tied to
          a container ID.
        - Worker service starts as a placeholder and does not run domain
          processing yet.
    """
    compose_text = (ROOT_DIR / "compose.yml").read_text(encoding="utf-8")

    for service_name in (
        "postgres",
        "redis",
        "ollama",
        "backend",
        "frontend",
        "worker",
    ):
        assert f"  {service_name}:" in compose_text

    for volume_name in (
        "postgres-data:",
        "redis-data:",
        "ollama-data:",
        "storage-data:",
    ):
        assert volume_name in compose_text

    assert "python -m app.worker" in compose_text
    assert "RECONAI_PROCESSING_ENABLED=false" in compose_text
    assert "celery" not in compose_text.lower()
