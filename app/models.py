"""Persistent database models."""

from datetime import date

from sqlalchemy import CheckConstraint, Date, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Student(Base):
    """A student record, using an application-facing unique identifier."""

    __tablename__ = "students"
    __table_args__ = (
        CheckConstraint(
            "email IS NOT NULL OR phone IS NOT NULL", name="student_has_contact"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    course: Mapped[str | None] = mapped_column(String(150), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    enrollment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
