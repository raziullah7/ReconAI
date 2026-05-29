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

    assert (
        settings.database_url == "postgresql://reconai:reconai@localhost:5432/reconai"
    )
    assert not hasattr(settings, "redis_url")

    load_settings.cache_clear()


def test_settings_loads_reconciliation_threshold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifies the M1.3 review confidence threshold setting.

    Summary:
        Loads the default threshold and rejects values outside 0..1.
    Mocks:
        monkeypatch isolates process environment and disables local `.env`
        loading.
    Assertions:
        The default is 0.80, explicit valid values load, and invalid values
        raise validation errors.
    """
    load_settings.cache_clear()
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://reconai:reconai@localhost:5432/reconai",
    )
    monkeypatch.delenv("EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD", raising=False)

    settings = load_settings()

    assert settings.extraction_review_confidence_threshold == 0.80

    load_settings.cache_clear()
    monkeypatch.setenv("EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD", "0.91")

    settings = load_settings()

    assert settings.extraction_review_confidence_threshold == 0.91

    load_settings.cache_clear()
    monkeypatch.setenv("EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD", "1.01")

    with pytest.raises(ValidationError) as exc_info:
        load_settings()

    assert "EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD" in str(exc_info.value)

    load_settings.cache_clear()
