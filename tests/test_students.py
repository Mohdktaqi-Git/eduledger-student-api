from copy import deepcopy
from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.config import Settings
from app.main import create_app
from app.models import Student


def create(client, payload):
    response = client.post("/students", json=payload)
    assert response.status_code == 201, response.text
    return response


def test_create_student_and_get_it(client, student_payload):
    created = create(client, student_payload)
    assert created.json()["student_id"] == "STU-100"
    assert created.json()["date_of_birth"] == "2004-05-21"

    fetched = client.get("/students/STU-100")
    assert fetched.status_code == 200
    assert fetched.json()["email"] == "avery.patel@example.com"


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", ""),
        ("date_of_birth", "not-a-date"),
        ("email", "not-an-email"),
        ("phone", "abc"),
    ],
)
def test_invalid_input_is_rejected(client, student_payload, field, value):
    payload = deepcopy(student_payload)
    payload[field] = value
    response = client.post("/students", json=payload)
    assert response.status_code == 422
    assert response.json()["detail"] == "Validation failed."


def test_required_contact_is_enforced(client, student_payload):
    payload = deepcopy(student_payload)
    payload["email"] = None
    payload["phone"] = None
    response = client.post("/students", json=payload)
    assert response.status_code == 422
    assert response.json()["detail"] == "Validation failed."


def test_duplicate_identifier_is_rejected(client, student_payload):
    create(client, student_payload)
    response = client.post("/students", json=student_payload)
    assert response.status_code == 409
    assert response.json()["detail"] == "Student ID 'STU-100' already exists."


def test_listing_filtering_pagination_and_ordering(client, student_payload):
    first = deepcopy(student_payload)
    first.update(
        {"student_id": "STU-200", "name": "Zoe Example", "course": "Mathematics"}
    )
    second = deepcopy(student_payload)
    second.update(
        {"student_id": "STU-050", "name": "Avery Quinn", "course": "Computer Science"}
    )
    create(client, first)
    create(client, second)

    listed = client.get("/students", params={"limit": 1, "offset": 0})
    assert listed.status_code == 200
    assert listed.json()["total"] == 2
    assert listed.json()["items"][0]["student_id"] == "STU-050"

    searched = client.get("/students", params={"q": "zoe"})
    assert [item["student_id"] for item in searched.json()["items"]] == ["STU-200"]
    filtered = client.get("/students", params={"course": "computer"})
    assert [item["student_id"] for item in filtered.json()["items"]] == ["STU-050"]


def test_missing_student_has_consistent_error(client):
    response = client.get("/students/DOES-NOT-EXIST")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student 'DOES-NOT-EXIST' was not found."


def test_put_replaces_mutable_fields(client, student_payload):
    create(client, student_payload)
    replacement = {
        "name": "Avery Updated",
        "date_of_birth": "2004-05-21",
        "email": "updated@example.com",
        "phone": "+1 555 010 1001",
        "course": "Data Science",
        "address": "202 Fictional Lane",
        "enrollment_date": "2023-08-01",
    }
    response = client.put("/students/STU-100", json=replacement)
    assert response.status_code == 200
    assert response.json()["student_id"] == "STU-100"
    assert response.json()["course"] == "Data Science"


def test_patch_validates_merged_record(client, student_payload):
    create(client, student_payload)
    changed = client.patch("/students/STU-100", json={"course": "Cyber Security"})
    assert changed.status_code == 200
    assert changed.json()["course"] == "Cyber Security"

    invalid = client.patch("/students/STU-100", json={"email": None, "phone": None})
    assert invalid.status_code == 422
    empty = client.patch("/students/STU-100", json={})
    assert empty.status_code == 422


def test_delete_and_repeat_delete(client, student_payload):
    create(client, student_payload)
    deleted = client.delete("/students/STU-100")
    assert deleted.status_code == 204
    assert deleted.content == b""
    repeated = client.delete("/students/STU-100")
    assert repeated.status_code == 404


def test_persistence_across_application_restarts(tmp_path, student_payload):
    database_url = f"sqlite:///{tmp_path / 'persistent.db'}"
    settings = Settings(database_url=database_url)
    first_app = create_app(settings)
    with first_app.state.database.session_factory() as session:
        student = Student(
            **{
                **student_payload,
                "date_of_birth": date.fromisoformat(student_payload["date_of_birth"]),
                "enrollment_date": date.fromisoformat(student_payload["enrollment_date"]),
            }
        )
        session.add(student)
        session.commit()

    second_app = create_app(settings)
    with second_app.state.database.session_factory() as session:
        assert (
            session.query(Student).filter_by(student_id="STU-100").one().name
            == "Avery Patel"
        )
    first_app.state.database.engine.dispose()
    second_app.state.database.engine.dispose()


def test_database_contact_constraint(tmp_path):
    settings = Settings(database_url=f"sqlite:///{tmp_path / 'constraint.db'}")
    app = create_app(settings)
    with app.state.database.session_factory() as session:
        session.add(
            Student(
                student_id="STU-CONTACT",
                name="Constraint Example",
                date_of_birth=date.fromisoformat("2004-01-01"),
                email=None,
                phone=None,
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
    app.state.database.engine.dispose()


def test_large_request_and_health_are_safe(client):
    response = client.post(
        "/students", content="x" * 1_025, headers={"content-type": "application/json"}
    )
    assert response.status_code == 413
    assert response.json() == {"detail": "Request body is too large."}
    assert client.get("/health").json() == {"status": "ok"}
