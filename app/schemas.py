"""Pydantic request and response contracts."""

from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

StudentId = Annotated[
    str, Field(min_length=1, max_length=50, pattern=r"^[A-Za-z0-9_-]+$")
]
Name = Annotated[str, Field(min_length=1, max_length=150)]
Phone = Annotated[str, Field(min_length=7, max_length=32, pattern=r"^[0-9+(). -]+$")]
Course = Annotated[str, Field(min_length=1, max_length=150)]
Address = Annotated[str, Field(min_length=1, max_length=1000)]


class StudentFields(BaseModel):
    name: Name
    date_of_birth: date
    email: EmailStr | None = None
    phone: Phone | None = None
    course: Course | None = None
    address: Address | None = None
    enrollment_date: date | None = None

    @model_validator(mode="after")
    def has_contact_information(self) -> "StudentFields":
        if not self.email and not self.phone:
            raise ValueError("Provide at least one contact method: email or phone.")
        return self

    @model_validator(mode="after")
    def dates_are_consistent(self) -> "StudentFields":
        if self.enrollment_date and self.enrollment_date < self.date_of_birth:
            raise ValueError("enrollment_date cannot be before date_of_birth.")
        return self


class StudentCreate(StudentFields):
    student_id: StudentId


class StudentReplace(StudentFields):
    """Complete replacement of mutable student fields; student_id is immutable."""


class StudentPatch(BaseModel):
    name: Name | None = None
    date_of_birth: date | None = None
    email: EmailStr | None = None
    phone: Phone | None = None
    course: Course | None = None
    address: Address | None = None
    enrollment_date: date | None = None

    @model_validator(mode="after")
    def includes_a_change(self) -> "StudentPatch":
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update.")
        return self


class StudentResponse(StudentCreate):
    model_config = ConfigDict(from_attributes=True)


class StudentListResponse(BaseModel):
    items: list[StudentResponse]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1)


class ErrorResponse(BaseModel):
    detail: str
