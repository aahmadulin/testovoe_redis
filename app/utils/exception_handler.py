import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


logger: logging.Logger = logging.getLogger(__name__)

INTERNAL_SERVER_ERROR_STATUS_CODE: int = 500
INTERNAL_SERVER_ERROR_MESSAGE: str = "Internal server error"


async def global_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handle unexpected application errors globally.

    Args:
        request (Request): Incoming FastAPI request.
        exc (Exception): Unhandled exception instance.

    Returns:
        JSONResponse: Standardized error response.
    """
    logger.exception(
        "Unhandled exception occurred. Path: %s, Method: %s, Error: %s",
        request.url.path,
        request.method,
        str(exc)
    )

    return JSONResponse(
        status_code=INTERNAL_SERVER_ERROR_STATUS_CODE,
        content={"detail": INTERNAL_SERVER_ERROR_MESSAGE}
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers in FastAPI application.

    Args:
        app (FastAPI): FastAPI application instance.
    """
    app.add_exception_handler(Exception, global_exception_handler)