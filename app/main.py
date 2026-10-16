"""FastAPI application factory and HTTP error protections."""

import logging

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from .config import Settings, get_settings
from .database import Database
from .routes import build_student_router
from .services import DuplicateStudentIdError, StudentNotFoundError

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    database = Database(settings.database_url)
    database.create_tables()

    app = FastAPI(
        title="EduLedger - Student Records Management API",
        version="1.0.0",
        description="A FastAPI and SQLite backend for fictional student records.",
        docs_url="/docs" if settings.app_env == "development" else None,
        redoc_url=None,
    )
    app.state.database = database

    if settings.allowed_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins,
            allow_credentials=False,
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
            allow_headers=["Content-Type", "Accept"],
        )

    @app.middleware("http")
    async def restrict_request_size(request: Request, call_next):  # type: ignore[no-untyped-def]
        content_length = request.headers.get("content-length")
        if (
            content_length
            and content_length.isdigit()
            and int(content_length) > settings.max_request_size_bytes
        ):
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "Request body is too large."},
            )
        return await call_next(request)

    @app.exception_handler(StudentNotFoundError)
    async def student_not_found(
        _: Request, error: StudentNotFoundError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"Student '{error.args[0]}' was not found."},
        )

    @app.exception_handler(DuplicateStudentIdError)
    async def duplicate_student(
        _: Request, error: DuplicateStudentIdError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": f"Student ID '{error.args[0]}' already exists."},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(
        _: Request, error: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation failed.",
                "errors": jsonable_encoder(error.errors()),
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error(_: Request, __: SQLAlchemyError) -> JSONResponse:
        logger.exception("Database operation failed")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "A database error occurred."},
        )

    @app.get("/", summary="Identify the API")
    def root() -> dict[str, str]:
        return {
            "service": "EduLedger - Student Records Management API",
            "docs": "/docs" if settings.app_env == "development" else "disabled",
        }

    @app.get("/health", summary="Check service health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(build_student_router(database))
    return app


app = create_app()
