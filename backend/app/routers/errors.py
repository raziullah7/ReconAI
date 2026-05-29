from collections.abc import Mapping

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

DEFAULT_REQUEST_ID = "local-request"
ERROR_CODE_KEY = "code"
ERROR_MESSAGE_KEY = "message"


def build_error_response(
    code: str,
    message: str,
    request_id: str,
) -> dict[str, dict[str, str]]:
    """Build the canonical API error envelope.

    What: Returns the shared error object used by Base API endpoints.
    Why: Clients need one predictable failure shape before frontend work starts.

    Args:
        code: Stable machine-readable error code.
        message: Human-readable explanation.
        request_id: Request correlation value, or a local placeholder before
            request context exists.

    Returns:
        dict[str, dict[str, str]]: Canonical error envelope.
    """
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }


def register_error_handlers(application: FastAPI) -> None:
    """Register canonical Base API error handlers.

    What: Installs handlers that convert FastAPI validation errors and expected
        route errors into the shared error envelope.
    Why: The API contract requires non-2xx responses to use one predictable
        shape.

    Args:
        application: FastAPI app created by `create_app`.

    States / Side Effects:
        Mutates the FastAPI application exception-handler registry.
    """

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=build_error_response(
                "ValidationFailed",
                "Request validation failed.",
                _request_id(request),
            ),
        )

    @application.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_response(
                _error_code(exc.status_code, exc.detail),
                _error_message(exc.detail),
                _request_id(request),
            ),
        )


def _request_id(request: Request) -> str:
    return request.headers.get("X-Request-ID", DEFAULT_REQUEST_ID)


def _error_code(status_code: int, detail: object) -> str:
    if isinstance(detail, Mapping):
        code = detail.get(ERROR_CODE_KEY)
        if isinstance(code, str):
            return code
    if status_code == status.HTTP_404_NOT_FOUND:
        return "NotFound"
    return "ValidationFailed"


def _error_message(detail: object) -> str:
    if isinstance(detail, Mapping):
        message = detail.get(ERROR_MESSAGE_KEY)
        if isinstance(message, str):
            return message
    if isinstance(detail, str):
        return detail
    return "Request failed."
