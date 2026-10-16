"""SQLAlchemy engine, session, and initialization helpers."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Base class for ORM models."""


class Database:
    """Owns an engine and produces request-scoped database sessions."""

    def __init__(self, database_url: str) -> None:
        connect_args = (
            {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        )
        self.engine = create_engine(database_url, connect_args=connect_args)
        self.session_factory = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False
        )

    def create_tables(self) -> None:
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        session = self.session_factory()
        try:
            yield session
        finally:
            session.close()
