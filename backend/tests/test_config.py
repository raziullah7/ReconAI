from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import load_settings


def test_settings_require_database_and_redis_urls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifies that required infrastructure URLs fail fast when absent.

    Mocks:
        monkeypatch: Clears environment variables so settings validation is
            isolated from the developer machine.

    Assertions:
        - `load_settings.cache_clear()` is called before and after
          environment mutation so cached settings cannot leak between tests.
        - Missing `DATABASE_URL` raises a validation error.
        - Missing `REDIS_URL` raises a validation error.
        - Error text names the missing setting to keep local setup
          actionable.
    """
    load_settings.cache_clear()
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)
    monkeypatch.chdir(Path(__file__).parent)

    with pytest.raises(ValidationError) as exc_info:
        load_settings()

    error_text = str(exc_info.value)
    assert "DATABASE_URL" in error_text
    assert "REDIS_URL" in error_text

    load_settings.cache_clear()
