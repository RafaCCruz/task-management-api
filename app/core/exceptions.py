"""Custom application exceptions and FastAPI exception handlers."""

from typing import Any, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Any] = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None) -> None:
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND, details=details)


class UnauthorizedException(AppException):
    """Authentication failed or token invalid."""

    def __init__(
        self, message: str = "Could not validate credentials", details: Optional[Any] = None
    ) -> None:
        super().__init__(
            message=message, status_code=status.HTTP_401_UNAUTHORIZED, details=details
        )


class ForbiddenException(AppException):
    """Authenticated user lacks permission."""

    def __init__(
        self, message: str = "Not enough permissions", details: Optional[Any] = None
    ) -> None:
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN, details=details)


class ConflictException(AppException):
    """Resource conflict (e.g. duplicate email)."""

    def __init__(
        self, message: str = "Resource already exists", details: Optional[Any] = None
    ) -> None:
        super().__init__(message=message, status_code=status.HTTP_409_CONFLICT, details=details)


class BadRequestException(AppException):
    """Invalid client request."""

    def __init__(
        self, message: str = "Bad request", details: Optional[Any] = None
    ) -> None:
        super().__init__(
            message=message, status_code=status.HTTP_400_BAD_REQUEST, details=details
        )


def _error_response(
    status_code: int,
    message: str,
    details: Optional[Any] = None,
) -> JSONResponse:
    content: dict[str, Any] = {
        "error": {
            "message": message,
            "status_code": status_code,
        }
    }
    if details is not None:
        content["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=content)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return _error_response(exc.status_code, exc.message, exc.details)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return _error_response(exc.status_code, str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Validation error",
            details=exc.errors(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # In production you would log the full traceback here
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Internal server error",
        )
