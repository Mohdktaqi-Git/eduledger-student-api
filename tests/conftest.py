import asyncio
from collections.abc import Generator

import httpx
import pytest

from app.config import Settings
from app.main import create_app


class ApiClient:
    """Small synchronous adapter around HTTPX's in-process ASGI transport."""

    def __init__(self, app) -> None:
        self.app = app

    def request(self, method: str, url: str, **kwargs):
        async def send():
            transport = httpx.ASGITransport(app=self.app)
            async with httpx.AsyncClient(
                transport=transport, base_url="http://testserver"
            ) as client:
                return await client.request(method, url, **kwargs)

        return asyncio.run(send())

    def get(self, url: str, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs):
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs):
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs):
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs):
        return self.request("DELETE", url, **kwargs)


@pytest.fixture
def client(tmp_path) -> Generator[ApiClient, None, None]:
    database_path = tmp_path / "students-test.db"
    settings = Settings(
        database_url=f"sqlite:///{database_path}", max_request_size_bytes=1_024
    )
    app = create_app(settings)
    yield ApiClient(app)
    # Explicit disposal releases SQLite file handles on Windows before pytest cleanup.
    app.state.database.engine.dispose()


@pytest.fixture
def student_payload() -> dict[str, str]:
    return {
        "student_id": "STU-100",
        "name": "Avery Patel",
        "date_of_birth": "2004-05-21",
        "email": "avery.patel@example.com",
        "phone": "+1 555 010 1000",
        "course": "Computer Science",
        "address": "101 Fictional Lane",
        "enrollment_date": "2023-08-01",
    }
