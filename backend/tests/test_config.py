import pytest
from pydantic import ValidationError

from app.core.config import Settings, load_settings


def test_settings_require_only_database_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifies that Phase 1 only requires the database URL.

    Mocks:
        monkeypatch: Clears environment variables so settings validation is
            isolated from the developer machine.

    Assertions:
        - `load_settings.cache_clear()` is called before and after
          environment mutation so cached settings cannot leak between tests.
        - Env-file loading is disabled for this test so local developer `.env`
          files do not affect the missing `DATABASE_URL` path.
        - Missing `DATABASE_URL` raises a validation error.
        - Redis and AI worker settings are not required in Phase 1.
        - A valid PostgreSQL URL is enough to load settings.
    """
    load_settings.cache_clear()
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.delenv("STORAGE_ROOT", raising=False)
    monkeypatch.delenv("WORKER_CONCURRENCY", raising=False)
    monkeypatch.setitem(Settings.model_config, "env_file", None)

    with pytest.raises(ValidationError) as exc_info:
        load_settings()

    error_text = str(exc_info.value)
    assert "DATABASE_URL" in error_text
    assert "REDIS_URL" not in error_text

    load_settings.cache_clear()
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://reconai:reconai@localhost:5432/reconai",
    )

    settings = load_settings()

    assert settings.database_url == "postgresql://reconai:reconai@localhost:5432/reconai"
    assert not hasattr(settings, "redis_url")

    load_settings.cache_clear()
