# Patient-Admission-System
MySQL Raw SQL Backend with Role-Based Access Control

A secure backend system for managing patient admissions in a healthcare-like environment. This project demonstrates role-based access control, manual SQL relationships, and authentication using JWT—all built from scratch using **FastAPI** and **MySQL** (via `mysql-connector`), without relying on an ORM.

---

## Features

- **Role-Based Login System**
  - Separate login endpoints for **doctors** and **patients**
  - JWT tokens for session handling
  - Access restrictions based on user role

- **CRUD Operations**
  - Patients, Doctors, Provinces, and Admissions
  - Full support for `GET`, `POST`, `PUT`, `PATCH`, and `DELETE`

- **Manual Relationship Construction**
  - Nested JSON responses created without an ORM
  - Custom functions simulate `.relationship` behavior from SQLAlchemy

- **Security**
  - Passwords hashed using **bcrypt**
  - Users can't access or modify unauthorized resources
  - Status codes: `200`, `201`, `204`, `400`, `403`, `404`

- **Testing**
  - Postman collection & FastAPI’s Swagger/OpenAPI Docs

---

## Tech Stack

| Layer           | Technology         |
|-----------------|--------------------|
| Language        | Python, SQL        |
| Framework       | FastAPI            |
| Database        | MySQL              |
| SQL Driver      | `mysql-connector`  |
| Auth            | JWT Tokens         |
| Security        | bcrypt             |
| Validation      | Pydantic           |
| Testing         | Postman, Swagger UI|

Install them using:

```bash
pip install -r requirements.txt
