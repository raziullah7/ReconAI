from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
DEFAULT_BACKEND_CORS_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]


class Settings(BaseSettings):
    """Store runtime settings required by the local app shell.

    What: Validates the one infrastructure URL required by the current
        foundation: PostgreSQL plus the Base API review confidence threshold.
    Why: Redis, Ollama, storage, and workers are deferred until their own
        phases, so the backend should not require those services to boot.

    States / Side Effects:
        Reads environment variables using the configured settings source.
    """

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        enable_decoding=False,
        extra="ignore",
        populate_by_name=True,
    )

    database_url: str = Field(
        default="",
        alias="DATABASE_URL",
        validate_default=True,
    )
    extraction_review_confidence_threshold: float = Field(
        default=0.80,
        alias="EXTRACTION_REVIEW_CONFIDENCE_THRESHOLD",
        ge=0,
        le=1,
    )
    backend_cors_origins: list[str] = Field(
        default_factory=lambda: DEFAULT_BACKEND_CORS_ORIGINS.copy(),
        alias="BACKEND_CORS_ORIGINS",
    )
    service_name: str = "reconai-backend"
    app_version: str = "0.1.0"

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_backend_cors_origins(cls, value: object) -> list[str]:
        """Parse local frontend origins from comma-separated config."""
        if value is None or value == "":
            return DEFAULT_BACKEND_CORS_ORIGINS.copy()
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, list):
            return [str(origin).strip() for origin in value if str(origin).strip()]
        msg = "BACKEND_CORS_ORIGINS must be a comma-separated string"
        raise ValueError(msg)

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """Validate that the configured database URL targets PostgreSQL."""
        if not value.startswith("postgresql"):
            msg = "DATABASE_URL must use a postgresql scheme"
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
