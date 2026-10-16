# EduLedger - Student Records Management API

EduLedger is an internship backend project for managing fictional student records. It provides a simple, persistent CRUD API using FastAPI and SQLite.

## Features

- Create, list, retrieve, replace, partially update, and delete students.
- SQLite persistence with a unique `student_id` database constraint.
- Validated names, dates, email addresses, phone numbers, and contact details.
- Search, course filtering, deterministic ordering, and pagination.
- Clear validation, duplicate-ID, and missing-record responses.
- Interactive Swagger documentation at `/docs` in development.

## Technology

- Python 3.11 or later
- FastAPI and Pydantic
- SQLAlchemy 2.x
- SQLite
- Pytest, HTTPX, Ruff, and MyPy

## Project layout

```text
app/          API, configuration, database model, schemas, services, routes
tests/        isolated automated tests using temporary SQLite databases
examples/     sample HTTP requests
data/         local development SQLite database (ignored by Git)
```

## Setup and startup (Windows PowerShell)

From the project directory:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to use Swagger UI. The application creates `data/students.db` automatically on first start.

Optional local configuration: copy `.env.example` to `.env` and change only non-secret development values. The default SQLite location is already suitable for local use.

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/students` | Create a student |
| GET | `/students` | List students; supports `q`, `course`, `offset`, and `limit` |
| GET | `/students/{student_id}` | Retrieve one student |
| PUT | `/students/{student_id}` | Replace mutable student fields |
| PATCH | `/students/{student_id}` | Update selected mutable fields |
| DELETE | `/students/{student_id}` | Delete a student |

`student_id` is immutable after creation, which keeps resource URLs predictable. `PUT` requires all mutable required fields; `PATCH` accepts only changes.

## Example request

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/students -ContentType 'application/json' -Body '{
  "student_id": "STU-101",
  "name": "Jordan Lee",
  "date_of_birth": "2004-09-12",
  "email": "jordan.lee@example.test",
  "phone": "+1 555 010 1010",
  "course": "Computer Science",
  "enrollment_date": "2023-08-01"
}'
```

More copy-ready requests are in `examples/requests.http`.

## Tests and quality checks

Run the HTTP test suite on a normal Windows Python environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Run code quality checks:

```powershell
.\.venv\Scripts\python.exe -m ruff check app tests
.\.venv\Scripts\python.exe -m mypy app --ignore-missing-imports
```

## Security notes

- SQLAlchemy parameterizes database queries; no SQL strings are built from request data.
- Pydantic rejects malformed or incomplete requests, and request bodies are size-limited.
- Duplicate and missing records return safe client-facing errors; internal database details are not returned.
- CORS is disabled unless an explicit allow-list is configured in the environment.
- `.env`, virtual environments, caches, and local SQLite databases are excluded from Git.
- All examples use fictional `.test` contact information.

## Resetting a development database

Stop the server first. Then delete only `data\students.db` from this project directory and restart the application. Do not use this on a database containing records you need to keep.

## Internship review explanation

The application separates FastAPI routes from validation schemas, database models, and business operations. A request is validated by Pydantic, handled by a route, persisted through SQLAlchemy to SQLite, and returned through a response schema. This keeps CRUD behavior easy to test and explain.

## Limitations

This is a local educational backend. It intentionally has no authentication, frontend, deployment, email integration, or optional Ollama feature. For production, add authentication, HTTPS, backup procedures, and a managed database only after requirements are defined.

## GitHub submission

The intended private repository name is `eduledger-student-api`. Do not create or push it until the final file list and visibility have been reviewed and explicitly approved.
