# EduLedger — Student Records Management API

EduLedger is a Python backend application developed for the EWB Edu Tech Pvt. Ltd. internship assignment. It provides a simple, persistent API for managing fictional student records using FastAPI and SQLite.

The project demonstrates Create, Read, Update, and Delete (CRUD) operations, input validation, database persistence, error handling, and automated testing.

## Features

- Create new student records.
- Retrieve individual student records.
- List, search, and filter student records.
- Replace existing student information.
- Partially update student information.
- Delete student records.
- Store records persistently using SQLite.
- Enforce unique student IDs.
- Validate names, dates, email addresses, phone numbers, and contact information.
- Handle invalid requests, duplicate IDs, and missing records.
- Support pagination and deterministic ordering.
- Provide interactive API documentation through Swagger UI.
- Include automated tests and API request examples.

## Technology Stack

| Technology     | Purpose                                 |
| -------------- | --------------------------------------- |
| Python 3.11+   | Backend programming language            |
| FastAPI        | REST API framework                      |
| Pydantic       | Request validation and data schemas     |
| SQLAlchemy 2.x | Database operations and ORM             |
| SQLite         | Persistent relational database          |
| Pytest         | Automated testing                       |
| HTTPX          | HTTP API testing                        |
| Ruff           | Code linting                            |
| MyPy           | Static type checking                    |
| Git and GitHub | Version control and source-code hosting |

## Project Structure

```text
students-database-crud-api/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   ├── schemas.py
│   └── services.py
│
├── data/
│   └── students.db              # Local database; excluded from Git
│
├── examples/
│   └── requests.http            # Example API requests
│
├── tests/
│   ├── conftest.py
│   └── test_students.py
│
├── .env.example
├── .gitignore
├── FINAL_SUBMISSION_CHECKLIST.md
├── IMPLEMENTATION_CHECKLIST.md
├── README.md
└── requirements.txt
```

Virtual environments, temporary files, caches, local configuration, and SQLite database files are excluded from the Git repository.

## Prerequisites

Before running the application, ensure that you have:

- Windows, Linux, or macOS.
- Python 3.11 or a compatible newer version.
- pip, Python's package installer.
- Git, if you want to clone the repository.

Python 3.11.9 was used for local testing.

## Installation and Setup

### 1. Clone the Repository

Open Command Prompt or a terminal and run:

```bash
git clone https://github.com/Mohdktaqi-Git/eduledger-student-api.git
```

Enter the project directory:

```bash
cd eduledger-student-api
```

### 2. Create a Virtual Environment

On Windows, run:

```cmd
py -3.11 -m venv .venv
```

Activate the environment in Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Alternatively, in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Run:

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the Application

The project includes an `.env.example` file containing example configuration settings.

For local configuration, create a copy named `.env` if needed.

The default SQLite database location is:

```text
data/students.db
```

Do not add real passwords, access tokens, private keys, or other secrets to `.env.example` or commit your `.env` file.

### 5. Start the Application

Run:

```bash
python -m uvicorn app.main:app --reload
```

The development server starts at:

```text
http://127.0.0.1:8000
```

The application initializes the SQLite database as configured.

## Interactive API Documentation

After starting the application, open:

**Swagger UI:** http://127.0.0.1:8000/docs

You can use Swagger UI to inspect endpoints, submit requests, and view API responses without needing a separate API client.

FastAPI also provides OpenAPI documentation at:

http://127.0.0.1:8000/openapi.json

These URLs are local development addresses. They do not represent a public deployment.

## API Endpoints

The application provides the following student-management endpoints.

| Method | Endpoint                 | Description                              |
| ------ | ------------------------ | ---------------------------------------- |
| POST   | `/students`              | Create a student record                  |
| GET    | `/students`              | List, search, and filter student records |
| GET    | `/students/{student_id}` | Retrieve a student by ID                 |
| PUT    | `/students/{student_id}` | Replace a student's mutable fields       |
| PATCH  | `/students/{student_id}` | Partially update a student               |
| DELETE | `/students/{student_id}` | Delete a student                         |

### Listing and Filtering

The listing endpoint supports query parameters for:

- `q`: Search by student ID or name.
- `course`: Filter by course.
- `offset`: Specify the number of records to skip.
- `limit`: Specify the maximum number of records to return.

Example:

```http
GET /students?q=Jordan&course=Computer%20Science&offset=0&limit=10
```

Student IDs are unique and remain unchanged after creation.

`PUT` replaces the mutable fields and requires the necessary fields for a valid record. `PATCH` changes only the supplied fields while validating the resulting record.

## Example API Request

The following PowerShell example creates a fictional student.

Start the server first, then open another PowerShell window and run:

```powershell
$body = @{
    student_id = "STU-101"
    name = "Jordan Lee"
    date_of_birth = "2004-09-12"
    email = "jordan.lee@example.com"
    phone = "+1 555 010 1010"
    course = "Computer Science"
    enrollment_date = "2023-08-01"
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/students" `
    -ContentType "application/json" `
    -Body $body
```

The example uses fictional information. It is intended for local testing only.

More example requests are available in:

```text
examples/requests.http
```

## Automated Testing

The project contains automated tests for student creation, retrieval, listing, validation, duplicate identifiers, updates, deletion, database persistence, and database constraints.

### Run All Tests

On Windows, from the project directory, run:

```cmd
.\.venv\Scripts\python.exe -m pytest -q
```

Expected successful output resembles:

```text
15 passed
```

### Run Code Quality Checks

Run Ruff:

```cmd
.\.venv\Scripts\python.exe -m ruff check .
```

Run MyPy:

```cmd
.\.venv\Scripts\python.exe -m mypy .
```

### Verification Results

During local project verification:

- All 15 automated tests passed.
- Ruff reported that all checks passed.
- MyPy reported no issues in 10 source files.

These results describe the local verification performed during development. They do not imply that a continuous-integration service or a public production deployment has run.

## Database Design

EduLedger uses SQLite for persistent storage.

Student records contain the following fields:

- Student ID
- Name
- Date of birth
- Email
- Phone
- Course
- Address
- Enrollment date

Student IDs are unique. Date fields use appropriate date representations, and the application validates incoming data before processing requests.

The database persists records between application restarts.

## Error Handling and Validation

The application handles common errors, including:

- Invalid request data.
- Missing student records.
- Duplicate student identifiers.
- Invalid date or contact information.
- Student records with no valid contact method.

Invalid requests receive appropriate HTTP error responses. Database operations use SQLAlchemy rather than constructing SQL statements directly from untrusted request input.

## Security Considerations

The project incorporates several basic security practices:

- SQLAlchemy ORM for database operations.
- Pydantic request validation.
- Request-body size limits.
- Safe client-facing validation and error responses.
- Configurable CORS allow-listing.
- Environment-based local configuration.
- Git exclusions for local environment files and database data.
- Fictional data in examples and tests.

The project is an educational backend, not a production-ready student information system.

For production use, additional measures would be needed, including authentication, authorization, HTTPS, appropriate database backups, monitoring, and a deployment-specific security review.

**Never commit passwords, API keys, private keys, `.env` files, real student records, or other confidential information.**

## Resetting the Development Database

The local development database is stored at:

```text
data/students.db
```

To reset development data:

1. Stop the application.
2. Make sure the database contains no records you need to preserve.
3. Delete only the local `data/students.db` file.
4. Restart the application.

The application can initialize the database again according to its configuration.

Do not perform this operation on a database containing important records without first making an appropriate backup.

## Architecture Overview

The application separates its main responsibilities into several modules:

- `main.py`: Application initialization and middleware.
- `config.py`: Application configuration.
- `database.py`: Database engine and session management.
- `models.py`: SQLAlchemy database models.
- `schemas.py`: Pydantic request and response schemas.
- `routes.py`: FastAPI endpoint definitions.
- `services.py`: Student-related business operations.
- `tests/`: Automated tests.

A request is validated, processed by a route, handled by the appropriate service operation, and persisted through SQLAlchemy to SQLite when necessary.

This structure keeps the code organized and makes the main CRUD functionality easier to test and explain.

## Project Limitations

This project intentionally focuses on the mandatory internship assignment.

It does not include:

- A frontend application.
- User authentication or role-based access control.
- Email notifications.
- Public cloud deployment.
- The optional Ollama AI extension.

The optional AI extension was omitted because it is not required to complete the core FastAPI and SQLite assignment.

## GitHub Repository

**Project:** EduLedger — Student Records Management API

**Repository:** https://github.com/Mohdktaqi-Git/eduledger-student-api

**Technology:** Python, FastAPI, Pydantic, SQLAlchemy, SQLite

**Visibility:** Public

The repository contains the project source code, tests, API request examples, dependency specification, and documentation.

The repository is intended for internship review. No production deployment is implied.

## Internship Review

During a project demonstration, the following steps can be used:

1. Explain why FastAPI and SQLite were selected.
2. Start the application locally.
3. Open Swagger UI.
4. Create a fictional student.
5. Retrieve the student by ID.
6. List or filter student records.
7. Update the student using `PATCH` or `PUT`.
8. Delete the student.
9. Explain input validation and missing-record handling.
10. Demonstrate the automated test suite.

This demonstrates the central purpose of EduLedger: a persistent student-records CRUD API with validation, organized code, and automated tests.

---

_Developed as an individual Python backend internship project for the EWB Edu Tech Pvt. Ltd. assignment._
