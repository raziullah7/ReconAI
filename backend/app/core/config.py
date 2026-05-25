from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Stores runtime settings required by the Phase 1 app shell.

    What: Validates infrastructure URLs, feature-flag defaults, storage
        location, and local runtime endpoints from environment variables.
    Why: The app must fail fast when required local dependencies are not
        configured, before later phases add domain behavior.

    States / Side Effects:
        Reads environment variables using the configured settings source.
    """

    model_config = SettingsConfigDict(
        env_file="../.env",
        extra="ignore",
        populate_by_name=True,
    )

    database_url: str = Field(
        default="",
        alias="DATABASE_URL",
        validate_default=True,
    )
    redis_url: str = Field(
        default="",
        alias="REDIS_URL",
        validate_default=True,
    )
    ollama_base_url: str = Field(
        default="http://ollama:11434",
        alias="OLLAMA_BASE_URL",
    )
    storage_root: str = Field(
        default="/var/lib/reconai/storage",
        alias="STORAGE_ROOT",
    )
    reconai_processing_enabled: bool = Field(
        default=False,
        alias="RECONAI_PROCESSING_ENABLED",
    )
    reconai_notifications_enabled: bool = Field(
        default=False,
        alias="RECONAI_NOTIFICATIONS_ENABLED",
    )
    reconai_exports_enabled: bool = Field(
        default=False,
        alias="RECONAI_EXPORTS_ENABLED",
    )
    worker_concurrency: int = Field(default=1, ge=1, alias="WORKER_CONCURRENCY")
    service_name: str = "reconai-backend"
    app_version: str = "0.1.0"

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """Validate that the configured database URL targets PostgreSQL."""
        if not value.startswith("postgresql"):
            msg = "DATABASE_URL must use a postgresql scheme"
            raise ValueError(msg)
        return value

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, value: str) -> str:
        """Validate that the configured cache URL targets Redis."""
        if not value.startswith("redis"):
            msg = "REDIS_URL must use a redis scheme"
            raise ValueError(msg)
        return value


@lru_cache
def load_settings() -> Settings:
    """Load and cache validated runtime settings.

    What: Builds the typed settings object once per process.
    Why: FastAPI dependencies and tests need a single settings entrypoint
        that can be overridden without global ad hoc parsing.

    Returns:
        Validated runtime configuration for the app shell.

    Raises:
        ValidationError: If required environment values are missing or
            malformed.

    States / Side Effects:
        Reads environment variables and caches the resulting settings.
    """
    return Settings()
