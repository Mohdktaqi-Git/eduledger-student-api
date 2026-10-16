"""Student business operations for the EduLedger application."""

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import Student
from .schemas import StudentCreate, StudentPatch, StudentReplace


class StudentNotFoundError(Exception):
    """Raised when no record matches an application student identifier."""


class DuplicateStudentIdError(Exception):
    """Raised when a student identifier violates its unique database constraint."""


def get_student_or_raise(session: Session, student_id: str) -> Student:
    """Retrieve a student or raise an error when the record does not exist."""
    student = session.scalar(select(Student).where(Student.student_id == student_id))

    if student is None:
        raise StudentNotFoundError(student_id)

    return student


def create_student(session: Session, payload: StudentCreate) -> Student:
    """Create and persist a student record."""
    student = Student(**payload.model_dump())
    session.add(student)

    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        raise DuplicateStudentIdError(payload.student_id) from error

    session.refresh(student)
    return student


def list_students(
    session: Session,
    *,
    q: str | None,
    course: str | None,
    offset: int,
    limit: int,
) -> tuple[list[Student], int]:
    """Return filtered, ordered student records and their total count."""
    filters = []

    if q:
        pattern = f"%{q.strip()}%"
        filters.append(
            or_(
                Student.student_id.ilike(pattern),
                Student.name.ilike(pattern),
            )
        )

    if course:
        filters.append(Student.course.ilike(f"%{course.strip()}%"))

    statement = select(Student).order_by(Student.student_id.asc())
    total_statement = select(func.count()).select_from(Student)

    if filters:
        statement = statement.where(*filters)
        total_statement = total_statement.where(*filters)

    students = list(session.scalars(statement.offset(offset).limit(limit)))
    total = session.scalar(total_statement) or 0

    return students, total


def replace_student(
    session: Session,
    student_id: str,
    payload: StudentReplace,
) -> Student:
    """Replace a student's mutable fields and persist the changes."""
    student = get_student_or_raise(session, student_id)

    for field, value in payload.model_dump().items():
        setattr(student, field, value)

    session.commit()
    session.refresh(student)

    return student


def patch_student(
    session: Session,
    student_id: str,
    payload: StudentPatch,
) -> Student:
    """Apply partial changes after validating the complete updated record."""
    student = get_student_or_raise(session, student_id)

    changes = payload.model_dump(exclude_unset=True)

    # Construct the complete record using current values.
    merged = {
        "name": student.name,
        "date_of_birth": student.date_of_birth,
        "email": student.email,
        "phone": student.phone,
        "course": student.course,
        "address": student.address,
        "enrollment_date": student.enrollment_date,
    }

    # Apply requested changes before validating the combined record.
    merged.update(changes)

    # A PATCH request must not leave the student without both contact methods.
    # Convert internal Pydantic validation errors into a proper HTTP 422 response.
    try:
        StudentReplace.model_validate(merged)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail="Validation failed.",
        ) from exc

    # Only modify the database after the complete record passes validation.
    for field, value in changes.items():
        setattr(student, field, value)

    session.commit()
    session.refresh(student)

    return student


def delete_student(session: Session, student_id: str) -> None:
    """Delete an existing student record."""
    student = get_student_or_raise(session, student_id)

    session.delete(student)
    session.commit()
