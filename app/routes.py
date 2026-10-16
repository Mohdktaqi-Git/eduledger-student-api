"""HTTP routes for student CRUD operations."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from .database import Database
from .models import Student
from .schemas import (
    StudentCreate,
    StudentListResponse,
    StudentPatch,
    StudentReplace,
    StudentResponse,
)
from .services import (
    create_student,
    delete_student,
    get_student_or_raise,
    list_students,
    patch_student,
    replace_student,
)


def build_student_router(database: Database) -> APIRouter:
    router = APIRouter(prefix="/students", tags=["Students"])
    session_dependency = Depends(database.get_session)

    @router.post(
        "",
        response_model=StudentResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Create a student",
    )
    def create(
        payload: StudentCreate, session: Annotated[Session, session_dependency]
    ) -> Student:
        return create_student(session, payload)

    @router.get(
        "",
        response_model=StudentListResponse,
        summary="List, search, and filter students",
    )
    def list_all(
        session: Annotated[Session, session_dependency],
        q: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
        course: Annotated[str | None, Query(min_length=1, max_length=150)] = None,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=100)] = 25,
    ) -> StudentListResponse:
        items, total = list_students(
            session, q=q, course=course, offset=offset, limit=limit
        )
        return StudentListResponse(
            items=[StudentResponse.model_validate(student) for student in items],
            total=total,
            offset=offset,
            limit=limit,
        )

    @router.get(
        "/{student_id}", response_model=StudentResponse, summary="Retrieve one student"
    )
    def get_one(
        student_id: str, session: Annotated[Session, session_dependency]
    ) -> Student:
        return get_student_or_raise(session, student_id)

    @router.put(
        "/{student_id}",
        response_model=StudentResponse,
        summary="Replace mutable student details",
    )
    def replace(
        student_id: str,
        payload: StudentReplace,
        session: Annotated[Session, session_dependency],
    ) -> Student:
        return replace_student(session, student_id, payload)

    @router.patch(
        "/{student_id}",
        response_model=StudentResponse,
        summary="Partially update mutable student details",
    )
    def patch(
        student_id: str,
        payload: StudentPatch,
        session: Annotated[Session, session_dependency],
    ) -> Student:
        return patch_student(session, student_id, payload)

    @router.delete(
        "/{student_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        summary="Delete a student",
    )
    def delete(
        student_id: str, session: Annotated[Session, session_dependency]
    ) -> Response:
        delete_student(session, student_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
