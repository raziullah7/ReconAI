from typing import Annotated

from fastapi import Depends, FastAPI

from app.core.config import Settings, load_settings
from app.routers import reconciliation_cases
from app.routers.errors import register_error_handlers


async def health(
    settings: Annotated[Settings, Depends(load_settings)],
) -> dict[str, str]:
    """Return readiness metadata for the app shell.

    What: Reports a small health payload for local probes and future clients.
    Why: Phase 1 needs a stable integration point before domain APIs ship.

    Args:
        settings: Validated runtime settings injected by FastAPI.

    Returns:
        Service name, version, and status metadata.
    """
    return {
        "status": "ok",
        "service": settings.service_name,
        "version": settings.app_version,
    }


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the FastAPI application for the Phase 1 shell.

    What: Registers metadata, dependency overrides, and the health route.
    Why: Tests and development commands need a repeatable app factory before
        domain routers exist.

    Args:
        settings: Optional prebuilt settings for tests. Defaults to None,
            which loads settings from the environment.

    Returns:
        Configured application with only foundation routes.

    States / Side Effects:
        Reads cached settings when no explicit settings object is supplied.
    """
    application = FastAPI(title="ReconAI", version="0.1.0")
    register_error_handlers(application)

    if settings is not None:

        def load_settings_override() -> Settings:
            return settings

        application.dependency_overrides[load_settings] = load_settings_override

    application.add_api_route("/health", health, methods=["GET"])
    application.include_router(reconciliation_cases.router)
    return application


app = create_app()
