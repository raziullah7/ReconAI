from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import ValidationError
from starlette.middleware.cors import CORSMiddleware

from app.core.config import Settings, load_settings
from app.routers import reconciliation_cases
from app.routers.errors import register_error_handlers


def resolve_app_settings(settings: Settings | None) -> Settings | None:
    """Resolve settings for app-level middleware without blocking imports.

    What: Uses explicit test settings when provided and otherwise attempts to
        load environment-backed settings.
    Why: The module-level ASGI app should still import in tooling contexts where
        `DATABASE_URL` is absent, while local runtime can use configured CORS
        origins once settings are valid.

    Args:
        settings: Optional settings object supplied by tests or app factories.

    Returns:
        Valid settings when available, otherwise None.
    """
    if settings is not None:
        return settings
    try:
        return load_settings()
    except ValidationError:
        return None


def add_cors_middleware(application: FastAPI, settings: Settings | None) -> None:
    """Register local frontend CORS middleware when origins are configured.

    What: Allows the local Vite frontend to call the Base API routes directly.
    Why: Milestone 2 uses browser-to-FastAPI requests without a Vite proxy.

    Args:
        application: FastAPI app receiving middleware.
        settings: Runtime settings that may provide allowed frontend origins.
    """
    if settings is None or not settings.backend_cors_origins:
        return

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["content-type"],
    )


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
    """Create the FastAPI application for the Base API.

    What: Registers metadata, dependency overrides, error handlers, health
        route, and reconciliation routes.
    Why: Tests and development commands need a repeatable app factory for the
        backend application.

    Args:
        settings: Optional prebuilt settings for tests. Defaults to None,
            which loads settings from the environment.

    Returns:
        Configured application with health and Base API routes.

    States / Side Effects:
        Reads cached settings when no explicit settings object is supplied.
    """
    application = FastAPI(title="ReconAI", version="0.1.0")
    runtime_settings = resolve_app_settings(settings)
    register_error_handlers(application)
    add_cors_middleware(application, runtime_settings)

    if settings is not None:

        def load_settings_override() -> Settings:
            return settings

        application.dependency_overrides[load_settings] = load_settings_override

    application.add_api_route("/health", health, methods=["GET"])
    application.include_router(reconciliation_cases.router)
    return application


app = create_app()
